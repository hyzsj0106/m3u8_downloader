import asyncio
import traceback
import cchardet
import logging
from user_agent import random_ua

'''
from aiohttp import TCPConnector

self.session = aiohttp.ClientSession(loop=self.loop, connector=TCPConnector(verify_ssl=False))
'''

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s: %(message)s')


async def fetch(session, url, headers=None, binary=False, debug=False, timeout=10):
    '''
    requests请求函数
    :param url: 目标url
    :param _headers: 请求头
    :param binary: 是否是二进制数据
    :param debug: 是否开启debug模式
    :param timeout: 超时时间
    :return: 状态码，请求链接，响应数据
    '''
    if not headers:
        headers = {'User-Agent': random_ua()}
    final_url = url
    try:
        async with session.get(url, headers=headers, timeout=timeout) as response:
            # read() 返回的是 bytes
            html = await response.read()
            if not binary:
                # 自动解析编码格式，忽略个别字符不匹配
                encoding = cchardet.detect(html)['encoding']
                html = html.decode(encoding, errors='ignore')
            status = response.status
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


async def main():
    '''
    测试函数，抓取实例时不需要调用
    :return:
    '''
    url = 'http://www.httpbin.org/get'
    async with aiohttp.ClientSession() as session:
        for _ in range(50):
            status, final_url, html = await fetch(session, url)
            print(html)
            print(status)
            print(final_url)


if __name__ == '__main__':
    import aiohttp

    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
