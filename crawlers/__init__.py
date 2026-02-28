# -*- coding: utf-8 -*-
"""
爬虫模块
包含各公司官网和数据源的新闻爬虫
"""

from .stock_news_crawler import THSNewsCrawler
from .semitronix_news_crawler import SemitronixNewsCrawler
from .primarius_news_crawler import PrimariusNewsCrawler
from .univista_news_crawler import UnivistiaNewsCrawler
from .xepic_news_crawler import XepicNewsCrawler
from .seccw_news_crawler import SeccwNewsCrawler
from .dramx_news_crawler import DramxNewsCrawler
from .synopsys_news_crawler import SynopsysNewsCrawler
from .cadence_news_crawler import CadenceNewsCrawler
from .siemens_news_crawler import SiemensNewsCrawler
from .eetimes_news_crawler import EETimesNewsCrawler

__all__ = [
    'THSNewsCrawler',
    'SemitronixNewsCrawler',
    'PrimariusNewsCrawler',
    'UnivistiaNewsCrawler',
    'XepicNewsCrawler',
    'SeccwNewsCrawler',
    'DramxNewsCrawler',
    'SynopsysNewsCrawler',
    'CadenceNewsCrawler',
    'SiemensNewsCrawler',
    'EETimesNewsCrawler',
]
