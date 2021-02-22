import time, re


class ParseUrl:

    @classmethod
    def urls_type(cls, prefix, url_str):
        if '$' in url_str:
            item = cls.ok_parse(prefix, url_str)
        elif '\n' in url_str:
            item = cls.urls_parse(prefix, url_str)
        else:
            item = cls.normal_parse(prefix, url_str)
        return item

    @classmethod
    def ok_parse(cls, prefix, urls_str):
        video_dict = {}
        pat = re.compile(r'(.*?)\$(http.*?/index.m3u8)')
        for _ in pat.findall(urls_str):
            video_dict[prefix + _[0]] = _[-1]
        return video_dict

    @classmethod
    def normal_parse(cls, prefix, url_str):
        url_dict = {prefix: str(url_str)}
        return url_dict

    @classmethod
    def urls_parse(cls, prefix, urls_str):
        video_dict = {}
        v_name = int(time.time())
        for index, url in enumerate(urls_str.strip().split('\n')):
            video_dict[prefix + f'-{index}'] = url
        return video_dict


if __name__ == '__main__':
    prefix = '这个杀手不太冷'

    urls_str = '''
    HD高清$http://youku.com-youku.net/20180703/16450_7b7d7fff/index.m3u8
    '''
    item = ParseUrl.urls_type(prefix, urls_str)
    for _ in item.items():
        print(_)
