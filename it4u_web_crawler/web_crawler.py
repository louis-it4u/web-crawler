import concurrent.futures
import json
import logging
import threading
import time
from typing import Any, Callable, Dict, List, Tuple

import reactivex as rx
import requests
from it4u_http_request import HttpRequest, Url, default_cache_key_calculator
from reactivex import Observable
from reactivex import operators as ops
from tqdm import tqdm


class WebCrawler:
    def __init__(self, max_threads: int = 16, session_builder: Callable[[], requests.Session] = lambda: requests.Session(), headers: Dict[str, str] = None):
        self.http_request = HttpRequest(
            cache_key_calculator=default_cache_key_calculator, 
            session_builder=session_builder, 
            headers=headers)
        self.max_threads: int = max_threads
        self.responses_lock = threading.Lock()

    def crawl_data(self, param: List[Tuple[Any, Url]], pipes: List[Observable] = [], headers: Dict[str, str] = None, allow_redirects: bool = True, timeout: int = 5, verify: bool = False, max_retries: int = 3, proxy_builder: Callable[[], Dict[str, str]] = None) -> Any:
        urls: Url = [w[1] for w in param]

        return self.http_request \
            .get_responses_stream(urls=urls,
                                  pipes=pipes,
                                  headers=headers,
                                  allow_redirects=allow_redirects,
                                  timeout=timeout,
                                  verify=verify,
                                  max_retries=max_retries,
                                  proxy_builder=proxy_builder)

    def start_crawling(self, list: List[List[Url]], pipes: List[Observable] = [], headers: Dict[str, str] = None, allow_redirects: bool = True, timeout: int = 5, max_retries: int = 3, verify: bool = False, proxy_builder: Callable[[], Dict[str, str]] = None) -> List[Any]:
        responses = []
        start_time = time.time()

        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_threads) as executor:
            futures = []
            for index, urls in enumerate(list):
                futures.append(executor.submit(self.crawl_data, [(index * i, u) for i, u in enumerate(urls)], pipes, headers, allow_redirects, timeout, verify, max_retries, proxy_builder))
            
            with tqdm(total=len(list), desc=f"Fetching") as pbar:
                for future in concurrent.futures.as_completed(futures):
                    response = future.result()
                    if response is not None:
                        responses.append(response)
                    pbar.update(1)

        end_time = time.time()
        logging.info("All threads have finished.")
        execution_time = end_time - start_time
        return responses, execution_time
