import logging
import requests
import cchardet
import traceback
from user_agent import random_ua

# 禁用请求的证书警告
from requests.packages.urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

# 配置日志模块
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s : %(message)s')


def fetch(url, headers=None, binary=False, debug=False, timeout=10):
    '''
    requests请求函数
    :param url: 目标url
    :param _headers: 请求头
    :param binary: 是否是二进制数据
    :param debug: 是否开启debug模式
    :param timeout: 超时时间
    :return: 状态码，请求链接，响应数据
    '''
    _headers = headers
    if not _headers:
        _headers = {'User-Agent': random_ua()}
    final_url = url
    try:
        with requests.get(url, headers=_headers, verify=False, timeout=timeout) as response:
            # 如果是二进制数据，不编码直接返回
            if binary:
                html = response.content
            else:
                # 自动解析编码格式，忽略个别字符不匹配
                encoding = cchardet.detect(response.content)['encoding']
                html = response.content.decode(encoding, errors='ignore')
            status = response.status_code
            final_url = response.url
    except:
        if debug:
            traceback.print_exc()
        logging.error('Download failed ,the url: %s', final_url)
        if binary:
            html = b''
        else:
            html = ''
        status = 0
    # 返回状态码，url，获取的信息
    return status, final_url, html


if __name__ == '__main__':
    status, final_url, html = fetch('http://www.httpbin.org/get')
    print(html)
    print(status)
    print(final_url)
