import threading
import logging
import requests
import json
import time
import reactivex as rx
from reactivex import Observable, operators as ops
from typing import Dict, Any, Callable, List
from it4u_http_request import HttpRequest, default_cache_key_calculator

class Url:
    def __init__(self, url: str, method: str = "GET", params: Dict[str, Any] = None, json: Dict[str, Any] = None) -> None:
        self.url: str = url
        self.method: str = method
        self.params: Dict[str, Any] = params
        self.json: Dict[str, Any] = json


class WebCrawler:
    def __init__(self, max_threads: int = 16, session_builder: Callable[[], requests.Session] = lambda: requests.Session(), headers: Dict[str, str] = None):
        self.http_request = HttpRequest(
            cache_key_calculator=default_cache_key_calculator, 
            session_builder=session_builder, 
            headers=headers)
        self.max_threads: int = max_threads
        self.responses_lock = threading.Lock()

    def crawl_data(self, responses: List[Any], semaphore, url: Url, pipes: List[Observable] = [], headers: Dict[str, str] = None, allow_redirects: bool = True, timeout: int = 5, max_retries: int = 3) -> requests.Response:
        with semaphore:
            try:
                response = self.http_request \
                    .get_response_stream(url=url.url, 
                                         method=url.method, 
                                         params=url.params, 
                                         json=url.json, 
                                         headers=headers,
                                         allow_redirects=allow_redirects,
                                         timeout=timeout,
                                         max_retries=max_retries) \
                    .pipe(*pipes) \
                    .run()

                with self.responses_lock:
                    responses.append(response)

                logging.info("Crawled data from: %s", url.url)
            except requests.exceptions.RequestException as e:
                logging.error("Error crawling data from: %s, %s", url.url, e)

    def start_crawling(self, urls: List[Url], pipes: List[Observable] = [], headers: Dict[str, str] = None, allow_redirects: bool = True, timeout: int = 5, max_retries: int = 3) -> List[requests.Response]:
        responses = []
        semaphore = threading.Semaphore(self.max_threads)
        threads = []
        start_time = time.time()

        for url in urls:
            thread = threading.Thread(target=self.crawl_data, args=(responses, semaphore, url, pipes, headers, allow_redirects, timeout, max_retries))
            thread.start()
            threads.append(thread)

        for thread in threads:
            thread.join()

        end_time = time.time()
        logging.info("All threads have finished.")
        execution_time = end_time - start_time
        return responses, execution_time
