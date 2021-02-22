import asyncio, aiohttp
import random, os, sys, shutil
import time, string, re, logging
from urllib.parse import urljoin
import subprocess
import platform

sys.path.append('..')
from downloader_aio import fetch
from parsel_url import ParseUrl

prefix = '总有妖怪想害朕'

urls_str = '''
第01集$http://iqiyi.cdn9-okzy.com/20210209/22159_7d0fb636/index.m3u8
第02集$http://iqiyi.cdn9-okzy.com/20210209/22160_203248b8/index.m3u8
第03集$http://iqiyi.cdn9-okzy.com/20210209/22158_806c82a6/index.m3u8
第04集$http://iqiyi.cdn9-okzy.com/20210209/22162_b1bcb173/index.m3u8
第05集$http://iqiyi.cdn9-okzy.com/20210209/22161_24a477d6/index.m3u8
'''

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s: %(message)s')


class DownloadM3u8:

    def __init__(self):
        self.semaphore = asyncio.Semaphore(100)
        self.final_url = ''
        self.loop = asyncio.get_event_loop()
        self.session = None

    # 合并 video 片段
    async def merge(self, video_name, short_name):
        os.chdir(os.path.dirname(__file__) + f'/{short_name}/')
        try:
            if platform.system() == 'Windows':
                merge_cmd = f'copy /b *.ts {video_name}.ts'
            else:
                merge_cmd = f'cat *.ts > {video_name}.ts'
            logging.info('正在合并视频片段: %s : %s', video_name, merge_cmd)
            devNull = open(os.devnull, 'w')
            subprocess.call(merge_cmd, shell=True, stdout=devNull)
            logging.info('合并视频片段-%s-成功: %s', short_name, video_name)
        except Exception as e:
            logging.error('合并视频片段-%s-失败详情: %s', short_name, e)
        # 移动文件
        logging.info('尝试移动合成文件: %s', video_name)
        from_path = os.path.dirname(__file__) + f'/{short_name}/' + video_name + '.ts'
        if not os.path.exists(from_path):
            logging.info('移动合成文件不存在: %s', video_name)
            return
        try:
            to_path = os.path.dirname(__file__)
            shutil.copy(from_path, to_path)
            logging.info('视频移动成功')
        except Exception as e:
            logging.error('视频移动失败: %s', e)

    # 合并成功后删除源video片段
    async def del_video_part(self, short_name):
        dir_path = os.path.dirname(__file__) + f'/{short_name}'
        os.chdir(os.path.dirname(__file__))
        try:
            if os.path.isdir(dir_path):
                shutil.rmtree(dir_path)
        except Exception as e:
            logging.error('文件夹删除失败! %s', e)

    # 下载失败重试
    async def retry(self, video_url, binary=True):
        counter = 0
        while counter < 3:
            counter += 1
            status, final_url, html = await fetch(self.session, video_url, binary=binary, timeout=10)
            logging.info('正在执行重新下载, 状态码: %s 重试第 %s 次', status, counter)
            if status == 200 and html:
                # 处理 video 下载
                return status, final_url, html
        if binary:
            html = b''
        else:
            html = ''
        return 0, video_url, html

    async def download_video(self, video_name, part_url, index, short_name, v_list_length):
        async with self.semaphore:
            # 计算进度
            percent = int(index / v_list_length * 100)
            # 拼接视频片段url
            video_url = urljoin(self.final_url, part_url)
            part_name = short_name + str(index).zfill(4) + '.ts'
            logging.info('主任务: %s 正在执行子任务: %s 当前进度: %s %%', video_name, part_name, percent)
            # 文件保存全路径
            file_path = os.path.dirname(__file__) + f'/{short_name}/' + part_name
            status, _, content_part = await fetch(self.session, video_url, binary=True)
            if status != 200 or not content_part:
                logging.info('主任务: %s 正在执行子任务: %s 状态码: %s 即将重试', video_name, part_name, status)
                status, _, content_part = await self.retry(video_url, binary=True)
                logging.info('主任务: %s 正在执行子任务: %s 状态码: %s 重试成功,继续下载', video_name, part_name, status)
            # 创建视频文件夹
            dir_path = os.path.dirname(__file__) + '/' + short_name
            if not os.path.exists(dir_path):
                os.mkdir(dir_path)
            try:
                with open(file_path, 'wb')as f:
                    f.write(content_part)
            except Exception as e:
                logging.error('写入文件失败 %s', e)

    # 正确的m3u8链接
    async def final_m3u8_url(self, url):
        status, _, response = await fetch(self.session, url)
        if '#EXTM3U' not in response:
            logging.error('非m3u8视频格式文件')
            return False
        res_list = response.strip().split('\n')
        if ('.asp' not in response or '.asp' not in response) and len(res_list) <= 3:
            return urljoin(url, res_list[-1])
        else:
            return url

    # 解析返回的m3u8链接,获取ts段落
    async def get_v_list(self, final_url):
        status, _, response = await fetch(self.session, final_url)
        m3u8_v_list = []
        for index, part_url in enumerate(response.strip().split('\n')):
            if not part_url: continue
            if '.asp' in part_url or '.ts' in part_url:
                # 未经修改的index.m3u8源视频片段
                part_url = part_url.strip('\r')
                m3u8_v_list.append(part_url)
        logging.info('m3u8_v_list : %s', m3u8_v_list)
        return m3u8_v_list

    async def start(self):
        logging.info('The program started successfully!')
        item = ParseUrl.urls_type(prefix, urls_str.strip())
        logging.info('The item: %s', item)
        async with aiohttp.ClientSession(loop=self.loop) as self.session:
            # 遍历下载视频
            for video_name, url in item.items():
                short_name = ''.join(random.sample(string.ascii_letters, 3))
                # 正确的url
                self.final_url = await self.final_m3u8_url(url)
                logging.info('final_url : %s', self.final_url)
                # 获得视频片段的list
                m3u8_video_list = await self.get_v_list(self.final_url)
                if m3u8_video_list:
                    v_list_length = len(m3u8_video_list)
                    # 创建协程对象列表
                    tasks = [asyncio.ensure_future(
                        self.download_video(video_name, part_url, index, short_name, v_list_length))
                        for index, part_url in enumerate(m3u8_video_list)]
                    await asyncio.wait(tasks)
                    await asyncio.sleep(1)
                    logging.info('正在合并 %s 片段', video_name)
                    await self.merge(video_name, short_name)
                    logging.info('正在删除 %s 片段', video_name)
                    await asyncio.sleep(1)
                    await self.del_video_part(short_name)
                    logging.info('%s 视频处理完成~', video_name)
                else:
                    logging.error('m3u8.m3u8_video_list 是空的！')


if __name__ == '__main__':
    start = time.time()
    downloader = DownloadM3u8()
    downloader.loop.run_until_complete(downloader.start())
    time_cost = time.time() - start
    print(time_cost)
