import requests
import logging
import random
from it4u_web_crawler import WebCrawler
from it4u_http_request import Url, proxies
from reactivex import operators as ops

logging.basicConfig(level=logging.INFO, filename='out.log')

if __name__ == '__main__':
    # Example usage:
    urls = ['https://masothue.com/1201670888-cong-ty-tnhh-mtv-dung-lien',
            'https://masothue.com/0317690352-cong-ty-tnhh-thuong-mai-va-dich-vu-sm-group',
            'https://masothue.com/0317690666-cong-ty-tnhh-thuong-mai-xe-may-nhap-khau-duy-hung',
            'https://masothue.com/0317690987-cong-ty-tnhh-phan-long-laser',
            'https://masothue.com/0317689237-cong-ty-tnhh-phan-mem-thuan-phat',
            'https://masothue.com/0317689068-cong-ty-tnhh-coolera',
            'https://masothue.com/0110256660-cong-ty-tnhh-tm-va-dv-cong-nghe-phuong-anh',
            'https://masothue.com/0110256646-cong-ty-tnhh-suneva-viet-nam',
            'https://masothue.com/0110256639-cong-ty-tnhh-thuong-mai-dich-vu-an-phong-khanh',
            'https://masothue.com/0317691518-cong-ty-tnhh-mimisa-beauty-226-clinic']
    urls = [Url(u) for u in urls]

    crawler = WebCrawler(max_threads=8, session_builder=lambda: requests.Session())  # Limit to 5 parallel requests
    responses, execution_time = crawler.start_crawling(urls, [
        ops.filter(lambda res: res is not None),
        ], proxy_builder=lambda: random.choice(proxies))
    
    print (len(responses))
    # for response in responses:
    #     print("Response JSON:", response)

    print("Execution time:", execution_time)
    print(responses[0])