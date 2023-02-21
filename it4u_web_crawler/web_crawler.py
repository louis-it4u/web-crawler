import threading
import logging
import requests
import json
import time
import reactivex as rx
from reactivex import Observable, operators as ops
from typing import Dict, Any, Callable, List
from it4u_http_request import HttpRequest, Url, default_cache_key_calculator
import concurrent.futures

class WebCrawler:
    def __init__(self, max_threads: int = 16, session_builder: Callable[[], requests.Session] = lambda: requests.Session(), headers: Dict[str, str] = None):
        self.http_request = HttpRequest(
            cache_key_calculator=default_cache_key_calculator, 
            session_builder=session_builder, 
            headers=headers)
        self.max_threads: int = max_threads
        self.responses_lock = threading.Lock()

    def crawl_data(self, responses: List[Any], semaphore, url: Url, pipes: List[Observable] = [], headers: Dict[str, str] = None, allow_redirects: bool = True, timeout: int = 5, max_retries: int = 3, proxy_builder: Callable[[], Dict[str, str]] = None) -> Any:
        with semaphore:
            try:
                response = self.http_request \
                    .get_response_stream(url=url,
                                         pipes=pipes,
                                         headers=headers,
                                         allow_redirects=allow_redirects,
                                         timeout=timeout,
                                         max_retries=max_retries,
                                         proxy_builder=proxy_builder)

                with self.responses_lock:
                    responses.append(response)

                logging.info("Crawled data from: %s", url.url)
            except requests.exceptions.RequestException as e:
                logging.error("Error crawling data from: %s, %s", url.url, e)

    def start_crawling(self, urls: List[Url], pipes: List[Observable] = [], headers: Dict[str, str] = None, allow_redirects: bool = True, timeout: int = 5, max_retries: int = 3, proxy_builder: Callable[[], Dict[str, str]] = None) -> List[Any]:
        responses = []
        semaphore = threading.Semaphore(self.max_threads)
        start_time = time.time()

        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_threads) as executor:
            futures = []
            for url in urls:
                futures.append(executor.submit(self.crawl_data, responses, semaphore, url, pipes, headers, allow_redirects, timeout, max_retries, proxy_builder))

            for future in concurrent.futures.as_completed(futures):
                try:
                    response = future.result()
                    if response is not None:
                        responses.append(response)
                except Exception as e:
                    logging.error(f"An exception occurred while crawling {url}: {e}")

        end_time = time.time()
        logging.info("All threads have finished.")
        execution_time = end_time - start_time
        return responses, execution_time
