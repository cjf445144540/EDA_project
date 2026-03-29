# -*- coding: utf-8 -*-
"""
其他（默认禁用）新闻爬虫模块
"""

from .bing_news_crawler import BingNewsCrawler
from .iwencai_news_crawler import IWenCaiNewsCrawler
from .eechina_news_crawler import EEChinaNewsCrawler
from .eetchina_news_crawler import EETChinaNewsCrawler
from .eeworld_news_crawler import EEWorldNewsCrawler
from .synopsys_news_crawler import SynopsysNewsCrawler
from .cadence_news_crawler import CadenceNewsCrawler
from .siemens_news_crawler import SiemensNewsCrawler

__all__ = [
    'BingNewsCrawler',
    'IWenCaiNewsCrawler',
    'EEChinaNewsCrawler',
    'EETChinaNewsCrawler',
    'EEWorldNewsCrawler',
    'SynopsysNewsCrawler',
    'CadenceNewsCrawler',
    'SiemensNewsCrawler',
]
