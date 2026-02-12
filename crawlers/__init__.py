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

__all__ = [
    'THSNewsCrawler',
    'SemitronixNewsCrawler', 
    'PrimariusNewsCrawler',
    'UnivistiaNewsCrawler',
    'XepicNewsCrawler',
]
