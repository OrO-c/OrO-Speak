import random
import time

import requests
from requests.adapters import HTTPAdapter
from urllib3 import Retry

from pipesay.constants.constants import YIYAN_CATEGORY


class Fetcher:
    def __init__(self, fetch_mode: str, generations: int, category: list, file_path: str):
        self.mode = fetch_mode
        self.generations = generations
        self.category = category
        self.file_path = file_path
    
    def new_fetcher(self):
        fdict = {
            "hitokoto": self.hitokoto,
            "local": self.local
        }
        func = fdict.get(self.mode)
        if func is None:
            raise ValueError(f"{self.mode}不是一个有效的模式")
        return func
    
    
    def hitokoto(self):
        """
        控制对Hitokoto服务的请求及对其结果的格式化
        
        Args:
            generations(int): 需要的句子数量
            category(str): 需要的分类
        
        
        Returns:
            list: 一个包含字符串的列表，每个字符串是一个完整的句子。
                句子格式为："“句子内容”\n   ————出处"
                例如: [
                    "“你不努力，你得到的一切一定会被夺走！”\n   ————Posherlunch"
                    "“生命璀璨美丽，却成为众人的囚笼。”\n   ————黑暗之魂2"
                ]
        """
        
        sentences = []
        last_sentence = ""
        retry_word = ""
        
        while len(sentences) < self.generations:
            print(f"{retry_word}正在向Hitokoto一言获取{len(sentences) + 1}/{self.generations}个句子...", end=" ")
            fetch_sentence, author, from_work = self._fetch_hitokoto()
            print(" ✅")
        
            if len(sentences) == 0 or fetch_sentence != last_sentence:
                if author is not None:
                    sen_from = f"————{author}  《{from_work}》"
                else:
                    sen_from = f"————《{from_work}》"
                width = len(fetch_sentence) + 4
                sentences.append(f"“{fetch_sentence}”\n{sen_from:>{width}}")
                last_sentence = fetch_sentence
                retry_word = ""
            elif last_sentence == fetch_sentence:
                print("由于api方缓存问题，此句和上句重复，本程序将睡2秒再重新获取😋")
                retry_word = "🔄 重试："
                time.sleep(2)
            
        return sentences


    def _category_to_dict(self):
        """将分类名称列表转换为 Hitokoto API 的分类代码。
    
            
        Returns:
            dict: API 参数字典，格式为 {'c': ['a', 'k']}
                如果 categories 为空，返回空字典 {}
        """
        
        choose = []
        for c in self.category:
            for category, name in YIYAN_CATEGORY.items():
                if c == name:
                    choose.append(category)
                    break
        return {"c": choose} if choose else {}
    
    
    def _fetch_hitokoto(self):
        """
        向Hitokoto服务请求并获得句子信息
        
        Args:
            params(dict): 需要在请求后附加的url参数，以此控制筛选分类 
        Returns:
            str: 句子本身
            str: 句子的言者/作者
            str: 出处
        
        
        Raises:
            requests.exceptions.Timeout: 请求超时被抛出
        """
        
        retry_strategy = Retry(
        total=3,                     # 最多重试 3 次（不算第一次请求）
        backoff_factor=1,            # 重试间隔：1s, 2s, 4s（指数退避）
        status_forcelist=[500, 502, 503, 504],  # 碰到这些 HTTP 状态码就重试
        allowed_methods=["GET", "POST"]          # 允许重试的方法（默认只有 GET）
    )
        
        session = requests.Session()
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount('http://', adapter)
        session.mount('https://', adapter)
        
        try:
            r = session.get('https://v1.hitokoto.cn', timeout=(3.5, 6.5), params=self._category_to_dict())
        except requests.exceptions.Timeout:
            print("请求超时，请您检查网络和Hitokoto服务状态，并稍后再试")
            raise
        
        return r.json()["hitokoto"], r.json()["from_who"], r.json()["from"]




    def local(self):
        """
        从本地文件中挑选句子
        
        Returns:
            list: 句子列表
        """
        sentences = []
        with open(file=self.file_path, mode="r", encoding="utf-8") as f:
            local_sentence = f.readlines()
            for i in range(self.generations):
                sentences.append(random.choice(local_sentence))
        return sentences