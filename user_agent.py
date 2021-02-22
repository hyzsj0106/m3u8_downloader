# 导入包
import requests
import random
import json
import os


# 获取user-agent并保存为json文件
def fetch_ua():
    # 确定目标url
    user_agent_url = 'http://fake-useragent.herokuapp.com/browsers/0.1.11'
    # 获取内容
    response = requests.get(user_agent_url)
    # 保存内容
    with open('browsers.json', 'w') as f:
        json.dump(response.text, f)
        f.write('\n')


# 获取本地json文件中的browsers
def random_ua():
    local_path = os.path.dirname(os.path.abspath(__file__))
    with open(local_path + '\\browsers.json', 'r') as f:
        # 提取出来是str类型
        browsers_json = json.load(f)
        # print(browsers_json, type(browsers_json))
        # 转换成字典
        browsers_dict = json.loads(browsers_json)
        # print(browsers_json, type(browsers_json))
        # 下面都是取键值对操作
        browsers = browsers_dict['browsers']

        # 判断浏览器
        num = random.randint(0, len(browsers))
        browsers_name = ''
        if num == 0:
            browsers_name = browsers['chrome']
        elif num == 1:
            browsers_name = browsers['opera']
        elif num == 2:
            browsers_name = browsers['firefox']
        elif num == 3:
            browsers_name = browsers['internetexplorer']
        else:
            browsers_name = browsers['safari']
        # browsers_name <class 'list'>
        return random.choice(browsers_name)


if __name__ == '__main__':
    # 将json文件下载到本地
    # fetch_ua()
    print(random_ua())
