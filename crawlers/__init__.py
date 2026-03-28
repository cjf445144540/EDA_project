# -*- coding: utf-8 -*-
"""
爬虫模块
包含各公司官网和数据源的新闻爬虫
"""

# 行业/媒体新闻爬虫
from .stock_news_crawler import THSNewsCrawler
from .seccw_news_crawler import SeccwNewsCrawler
from .dramx_news_crawler import DramxNewsCrawler
from .eetimes_news_crawler import EETimesNewsCrawler
from .sohu_news_crawler import SohuNewsCrawler
from .sina_news_crawler import SinaNewsCrawler
from .qq_news_crawler import QQNewsCrawler
from .bing_news_crawler import BingNewsCrawler
from .iwencai_news_crawler import IWenCaiNewsCrawler
from .laoyaoba_news_crawler import LaoyaobaNewsCrawler
from .designnews_news_crawler import DesignNewsCrawler
from .digitimes_news_crawler import DigitimesNewsCrawler
from .eastmoney_news_crawler import EastmoneyNewsCrawler
from .eechina_news_crawler import EEChinaNewsCrawler
from .eetchina_news_crawler import EETChinaNewsCrawler
from .eeworld_news_crawler import EEWorldNewsCrawler

# 公司官网爬虫（从 official 子目录导入）
from .official import (
    SemitronixNewsCrawler,
    PrimariusNewsCrawler,
    UnivistiaNewsCrawler,
    XepicNewsCrawler,
    S2CNewsCrawler,
    GigaDANewsCrawler,
    XpedicNewsCrawler,
    SynopsysNewsCrawler,
    CadenceNewsCrawler,
    SiemensNewsCrawler,
)

__all__ = [
    # 行业/媒体
    'THSNewsCrawler',
    'SeccwNewsCrawler',
    'DramxNewsCrawler',
    'EETimesNewsCrawler',
    'SohuNewsCrawler',
    'SinaNewsCrawler',
    'QQNewsCrawler',
    'BingNewsCrawler',
    'IWenCaiNewsCrawler',
    'LaoyaobaNewsCrawler',
    'DesignNewsCrawler',
    'DigitimesNewsCrawler',
    'EastmoneyNewsCrawler',
    'EEChinaNewsCrawler',
    'EETChinaNewsCrawler',
    'EEWorldNewsCrawler',
    # 公司官网
    'SemitronixNewsCrawler',
    'PrimariusNewsCrawler',
    'UnivistiaNewsCrawler',
    'XepicNewsCrawler',
    'S2CNewsCrawler',
    'GigaDANewsCrawler',
    'XpedicNewsCrawler',
    'SynopsysNewsCrawler',
    'CadenceNewsCrawler',
    'SiemensNewsCrawler',
]
