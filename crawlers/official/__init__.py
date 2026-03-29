# -*- coding: utf-8 -*-
"""
公司官网新闻爬虫模块
包含国内外EDA公司官网的新闻爬虫
"""

from .semitronix_news_crawler import SemitronixNewsCrawler
from .primarius_news_crawler import PrimariusNewsCrawler
from .univista_news_crawler import UnivistiaNewsCrawler
from .xepic_news_crawler import XepicNewsCrawler
from .s2c_news_crawler import S2CNewsCrawler
from .gigada_news_crawler import GigaDANewsCrawler
from .xpeedic_news_crawler import XpedicNewsCrawler

__all__ = [
    'SemitronixNewsCrawler',
    'PrimariusNewsCrawler',
    'UnivistiaNewsCrawler',
    'XepicNewsCrawler',
    'S2CNewsCrawler',
    'GigaDANewsCrawler',
    'XpedicNewsCrawler',
]
