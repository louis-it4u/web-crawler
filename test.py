import requests
import logging
from it4u_web_crawler import WebCrawler, Url
from reactivex import operators as ops

logging.basicConfig(level=logging.INFO, filename='out.log')

if __name__ == '__main__':
    # Example usage:
    urls = [
        Url(f'https://www.tratencongty.com/?page={i + 1}') for i in range(16)
        # Add more URLs here
    ]

    crawler = WebCrawler(max_threads=8, session_builder=lambda: requests.Session())  # Limit to 5 parallel requests
    responses, execution_time = crawler.start_crawling(urls, [
        ops.filter(lambda res: res is not None),
        ])
    
    print (len(responses))
    # for response in responses:
    #     print("Response JSON:", response)

    print("Execution time:", execution_time)
    print(responses[0].text)