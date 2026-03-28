# -*- coding: utf-8 -*-
"""
统一新闻爬取入口脚本
支持调用多个爬虫脚本：
- 同花顺个股新闻 (stock_news_crawler)
- 广立微官网新闻 (semitronix_news_crawler)
- 未来可继续添加其他爬虫...
"""

# ========================================
# 全局配置（统一修改所有爬虫的默认值）
# ========================================
DEFAULT_DAYS = 7        # 默认爬取最近几天的新闻
DEFAULT_MAX_PAGES = 1   # 默认最大爬取页数
DEFAULT_MIN_CONTENT_LENGTH = 500  # 默认正文最小字数

# ========================================
# 爬虫配置（在这里添加新的爬虫配置）
# ========================================


# 新浪网 新闻配置
SINA_CONFIG = {
    'enabled': True,  # 是否启用
    'max_pages': DEFAULT_MAX_PAGES,
    'days': DEFAULT_DAYS,
    'keyword': 'EDA',
}

# 腾讯网 新闻配置
QQ_CONFIG = {
    'enabled': True,  # 是否启用
    'max_pages': DEFAULT_MAX_PAGES,
    'days': DEFAULT_DAYS,
    'keyword': 'EDA',
}

# 搜狐网 新闻配置
SOHU_CONFIG = {
    'enabled': True,  # 是否启用
    'max_pages': 3,  # 搜狐搜索结果不按时间排序，需多爬几页
    'days': DEFAULT_DAYS,
    'keyword': 'EDA',
}

# Bing 新闻配置
BING_CONFIG = {
    'enabled': True,  # 是否启用
    'max_pages': DEFAULT_MAX_PAGES,
    'days': DEFAULT_DAYS,
    'min_content_length': DEFAULT_MIN_CONTENT_LENGTH,
    'keyword': 'EDA',  # 使用 EDA 关键词获取更多新闻
}

# 问财网 新闻配置（已禁用：网站反爬虫限制，需要登录）
IWENCAI_CONFIG = {
    'enabled': False,  # 禁用：问财网有严格的反爬虫限制
    'max_pages': DEFAULT_MAX_PAGES,
    'days': DEFAULT_DAYS,
    'min_content_length': 100,
    'keywords': ['EDA', 'synopsys', '新思科技', 'cadence'],
}

# 集微网 新闻配置
LAOYAOBA_CONFIG = {
    'enabled': True,  # 是否启用
    'max_pages': DEFAULT_MAX_PAGES,
    'days': DEFAULT_DAYS,
    'min_content_length': 100,
    'keywords': ['EDA', 'synopsys', '新思科技', 'cadence'],  # 支持多个关键词
}

# design news 新闻配置
DESIGNNEWS_CONFIG = {
    'enabled': True,
    'max_pages': DEFAULT_MAX_PAGES,
    'days': DEFAULT_DAYS,
    'min_content_length': 0,
    'keywords': ['EDA', 'synopsys'],
}

# digitimes 新闻配置
DIGITIMES_CONFIG = {
    'enabled': True,
    'max_pages': DEFAULT_MAX_PAGES,
    'days': DEFAULT_DAYS,
    'min_content_length': 0,
    'keywords': ['EDA', 'synopsys'],
}

# 东方财富网 新闻配置
EASTMONEY_CONFIG = {
    'enabled': True,
    'max_pages': DEFAULT_MAX_PAGES,
    'days': DEFAULT_DAYS,
    'min_content_length': DEFAULT_MIN_CONTENT_LENGTH,
    'keywords': ['EDA', 'synopsys', '新思科技'],
}

# 同花顺个股新闻配置
THS_CONFIG = {
    'enabled': True,  # 是否启用
    'stocks': [
        "301269",  # 华大九天
        "688206",  # 概伦电子
        "301095"   # 广立微
    ],
    'days': DEFAULT_DAYS,
}

# 深圳电子商会新闻配置
SECCW_CONFIG = {
    'enabled': True,  # 是否启用
    'max_pages': DEFAULT_MAX_PAGES,
    'days': DEFAULT_DAYS,
    'keyword': 'EDA',
}

# 全球半导体观察新闻配置
DRAMX_CONFIG = {
    'enabled': True,  # 是否启用
    'max_pages': DEFAULT_MAX_PAGES,
    'days': DEFAULT_DAYS,
}

# 广立微官网新闻配置
SEMITRONIX_CONFIG = {
    'enabled': True,  # 是否启用
    'max_pages': DEFAULT_MAX_PAGES,
    'days': DEFAULT_DAYS,
}

# 概伦电子官网新闻配置
PRIMARIUS_CONFIG = {
    'enabled': True,  # 是否启用
    'max_pages': DEFAULT_MAX_PAGES,
    'days': DEFAULT_DAYS,
}

# 合见工软官网新闻配置
UNIVISTA_CONFIG = {
    'enabled': True,  # 是否启用
    'max_pages': DEFAULT_MAX_PAGES,
    'days': DEFAULT_DAYS,
}

# 芯华章官网新闻配置
XEPIC_CONFIG = {
    'enabled': True,  # 是否启用
    'max_pages': DEFAULT_MAX_PAGES,
    'days': DEFAULT_DAYS,
}

# Synopsys 新闻配置
SYNOPSYS_CONFIG = {
    'enabled': False,  # 是否启用
    'max_pages': DEFAULT_MAX_PAGES,
    'days': DEFAULT_DAYS,
}

# Cadence 新闻配置
CADENCE_CONFIG = {
    'enabled': False,  # 是否启用
    'max_pages': DEFAULT_MAX_PAGES,
    'days': DEFAULT_DAYS,
}

# Siemens 新闻配置
SIEMENS_CONFIG = {
    'enabled': False,  # 是否启用
    'max_pages': DEFAULT_MAX_PAGES,
    'days': DEFAULT_DAYS,
}

# EETimes 新闻配置
EETIMES_CONFIG = {
    'enabled': True,   # 是否启用
    'max_pages': DEFAULT_MAX_PAGES,
    'days': DEFAULT_DAYS,
    'keywords': ['synopsys', 'cadence', 'siemens', 'EDA'],
}

# 思尔芯 新闻配置
S2C_CONFIG = {
    'enabled': True,  # 是否启用
    'max_pages': DEFAULT_MAX_PAGES,
    'days': DEFAULT_DAYS,
}

# 鸿芯微纳 新闻配置
GIGADA_CONFIG = {
    'enabled': True,  # 是否启用
    'max_pages': DEFAULT_MAX_PAGES,
    'days': DEFAULT_DAYS,
}

# 芯和半导体 新闻配置
XPEEDIC_CONFIG = {
    'enabled': True,  # 是否启用
    'max_pages': DEFAULT_MAX_PAGES,
    'days': DEFAULT_DAYS,
}

# 电子工程网 新闻配置
EECHINA_CONFIG = {
    'enabled': False,  # 是否启用
    'max_pages': DEFAULT_MAX_PAGES,
    'days': DEFAULT_DAYS,
    'min_content_length': DEFAULT_MIN_CONTENT_LENGTH,
    'keyword': 'EDA',
}

# 电子工程专辑（eet-china.com）
EETCHINA_CONFIG = {
    'enabled': False,  # 是否启用
    'max_pages': DEFAULT_MAX_PAGES,
    'days': DEFAULT_DAYS,
    'min_content_length': DEFAULT_MIN_CONTENT_LENGTH,
    'keyword': 'eda',
}

# 电子工程世界（eeworld.com.cn）
EEWORLD_CONFIG = {
    'enabled': False,  # 是否启用
    'max_pages': DEFAULT_MAX_PAGES,
    'days': DEFAULT_DAYS,
    'min_content_length': DEFAULT_MIN_CONTENT_LENGTH,
    'keyword': 'EDA',
}

# 未来可以继续添加其他爬虫配置...
# OTHER_CRAWLER_CONFIG = {
#     'enabled': False,
#     ...
# }


import os
import sys
import logging
import contextlib
from glob import glob

# 静默模式：减少日志输出，只显示关键信息
QUIET_MODE = False  # 关闭静默模式，保留爬取日志
COLOR_ENABLED = sys.stdout.isatty() and os.environ.get("NO_COLOR") is None

# 抑制webdriver_manager的警告日志
os.environ['WDM_LOG'] = '0'
os.environ['WDM_LOG_LEVEL'] = '0'
os.environ['WDM_LOCAL'] = '1'  # 优先使用本地缓存，不检查更新
os.environ['WDM_SSL_VERIFY'] = '0'
os.environ['WDM_OFFLINE'] = '1'  # 完全禁用网络请求，使用本地缓存
os.environ['NO_PROXY'] = '*'
os.environ['no_proxy'] = '*'
# 禁用 selenium-manager 自动下载
os.environ['SE_MANAGER_DISABLED'] = '1'
for _name in ['WDM', 'webdriver_manager', 'webdriver_manager.core', 'urllib3', 'selenium.webdriver.common.selenium_manager']:
    logging.getLogger(_name).setLevel(logging.CRITICAL)
    logging.getLogger(_name).propagate = False
    logging.getLogger(_name).disabled = True

# 静默模式下的日志函数
def log(msg, force=False):
    """输出日志，静默模式下只输出force=True的内容"""
    if not QUIET_MODE or force:
        print(format_console_message(msg), flush=True)


def _color(text, code):
    if not COLOR_ENABLED:
        return text
    return f"\033[{code}m{text}\033[0m"


def _unicode_icon_enabled():
    encoding = (getattr(sys.stdout, "encoding", "") or "").lower()
    return "utf" in encoding or encoding == "cp65001"


def _icon(unicode_text, fallback_text):
    return unicode_text if _unicode_icon_enabled() else fallback_text


def _style_console_line(line):
    if line.startswith("[OK]"):
        return _color(line.replace("[OK]", _icon("✅", "[OK]"), 1), "92")
    if line.startswith("[ERR]"):
        return _color(line.replace("[ERR]", _icon("❌", "[ERR]"), 1), "91")
    if line.startswith("[!]"):
        return _color(line.replace("[!]", _icon("⚠️", "[!]"), 1), "93")
    if line.startswith("【Step"):
        return _color(f"{_icon('🔹', '>>')} {line}", "96")
    if line.startswith("开始并行爬取"):
        return _color(f"{_icon('🚀', '>>')} {line}", "96")
    if line.startswith("爬取完成，耗时"):
        return _color(f"{_icon('⏱️', '>>')} {line}", "96")
    if "完成 (" in line and line.strip().startswith("["):
        return _color(f"{_icon('✅', '[OK]')} {line}", "92")
    if "失败" in line:
        return _color(f"{_icon('❌', '[ERR]')} {line}", "91")
    if set(line.strip()) == {"="} and len(line.strip()) >= 30:
        return _color(line, "94")
    if set(line.strip()) == {"-"} and len(line.strip()) >= 20:
        return _color(line, "90")
    return line


def format_console_message(msg):
    text = str(msg)
    parts = text.splitlines(keepends=True)
    styled = []
    for part in parts:
        if part.endswith("\n"):
            raw = part[:-1]
            styled.append(_style_console_line(raw) + "\n")
        else:
            styled.append(_style_console_line(part))
    return "".join(styled)


def create_chrome_driver(chrome_options):
    from selenium import webdriver
    from selenium.webdriver.chrome.service import Service

    def find_local_chromedriver():
        roots = [
            os.path.join(os.path.dirname(os.path.abspath(__file__)), '.wdm', 'drivers', 'chromedriver'),
            os.path.join(os.getcwd(), '.wdm', 'drivers', 'chromedriver'),
            os.path.join(os.path.expanduser('~'), '.wdm', 'drivers', 'chromedriver'),
        ]
        candidates = []
        for root in roots:
            if not os.path.isdir(root):
                continue
            candidates.extend(glob(os.path.join(root, '**', 'chromedriver.exe'), recursive=True))
            candidates.extend(glob(os.path.join(root, '**', 'chromedriver'), recursive=True))
        candidates = [p for p in candidates if os.path.isfile(p)]
        if not candidates:
            return ''
        candidates.sort(key=lambda p: os.path.getmtime(p), reverse=True)
        return candidates[0]

    # 优先使用本地缓存的 chromedriver
    local_driver = find_local_chromedriver()
    if local_driver:
        try:
            service = Service(local_driver)
            return webdriver.Chrome(service=service, options=chrome_options)
        except Exception:
            pass
    
    # 尝试不指定 service 直接创建
    try:
        return webdriver.Chrome(options=chrome_options)
    except Exception as e:
        raise RuntimeError(f"Failed to create Chrome driver: {e}")

from crawlers import THSNewsCrawler, SemitronixNewsCrawler, PrimariusNewsCrawler, UnivistiaNewsCrawler, XepicNewsCrawler, SeccwNewsCrawler, DramxNewsCrawler, SynopsysNewsCrawler, CadenceNewsCrawler, SiemensNewsCrawler, EETimesNewsCrawler, S2CNewsCrawler, GigaDANewsCrawler, XpedicNewsCrawler, SinaNewsCrawler, QQNewsCrawler, SohuNewsCrawler, BingNewsCrawler, IWenCaiNewsCrawler, LaoyaobaNewsCrawler, DesignNewsCrawler, DigitimesNewsCrawler, EastmoneyNewsCrawler, EEChinaNewsCrawler, EETChinaNewsCrawler, EEWorldNewsCrawler
from classify_news import NewsClassifier
from auto_news_writer import get_first_news_link, fetch_news_content, copy_to_clipboard
from concurrent.futures import ThreadPoolExecutor, as_completed
import pyperclip
import json
from datetime import datetime, timedelta


# ========================================
# 公司名称映射
# ========================================
COMPANY_NAMES = {
    "301269": "华大九天",
    "688206": "概伦电子",
    "301095": "广立微",
    "semitronix": "广立微",  # 广立微官网
    "primarius": "概伦电子",  # 概伦电子官网
    "univista": "合见工软",  # 合见工软官网
    "xepic": "芯华章",  # 芯华章官网
    "seccw": "行业新闻",  # 深圳电子商会
    "dramx": "行业新闻",  # 全球半导体观察
    "synopsys": "Synopsys",  # Synopsys 新闻
    "cadence_semiwiki": "Cadence",  # Cadence SemiWiki
    "cadence_design_reuse": "Cadence",  # Cadence Design-Reuse
    "siemens_semiwiki": "Siemens",  # Siemens SemiWiki
    "siemens_design_reuse": "Siemens",  # Siemens Design-Reuse
    "eetimes": "EETimes",  # EETimes
    "s2c": "思尔芯",  # 思尔芯
    "gigada": "鸿芯微纳",  # 鸿芯微纳
    "xpeedic": "芯和半导体",  # 芯和半导体
    "sina": "行业新闻",  # 新浪网
    "qq": "行业新闻",  # 腾讯网
    "sohu": "行业新闻",  # 搜狐网
    "bing": "行业新闻",  # Bing新闻
    "iwencai": "行业新闻",  # 问财网
    "laoyaoba": "行业新闻",  # 集微网
    "designnews": "行业新闻",  # Design News
    "digitimes": "行业新闻",  # DIGITIMES
    "eastmoney": "行业新闻",  # 东方财富网
    "eechina": "行业新闻",  # 电子工程网
    "eetchina": "行业新闻",  # 电子工程专辑
    "eeworld": "行业新闻",  # 电子工程世界
}


def run_batch_crawl(stock_list, mode="today", start_date=None, end_date=None):
    """
    批量爬取多只股票的新闻
    :param stock_list: 股票代码列表，例如 ['301269', '600519']
    :param mode: 爬取模式 - "today": 当天, "range": 日期范围, "all": 所有
    :param start_date: 开始日期 (格式: 'YYYY-MM-DD')
    :param end_date: 结束日期 (格式: 'YYYY-MM-DD')
    """
    all_results = {}
    
    # 打印爬取信息
    print(f"开始批量爬取任务，共 {len(stock_list)} 只股票...")
    if mode == "today":
        print("爬取模式: 只爬取当天新闻")
    elif mode == "range":
        print(f"爬取模式: 日期范围 {start_date} 至 {end_date}")
    else:
        print("爬取模式: 爬取所有新闻")
    
    for code in stock_list:
        try:
            # 1. 初始化爬虫
            crawler = THSNewsCrawler(code)
            
            # 2. 根据模式执行爬取
            if mode == "today":
                news_list = crawler.crawl(only_today=True)
            elif mode == "range":
                news_list = crawler.crawl(start_date=start_date, end_date=end_date)
            else:
                news_list = crawler.crawl()
            
            # 3. 存储结果
            all_results[code] = {
                "count": len(news_list),
                "news": news_list
            }
            
            print(f"[OK] 股票 {code} 爬取完成，获取 {len(news_list)} 条新闻")
            
        except Exception as e:
            print(f"[ERR] 股票 {code} 爬取失败: {e}")
    
    # 将汇总结果保存
    output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'json')
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, "batch_news_results.json")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(all_results, f, ensure_ascii=False, indent=2)
    
    print(f"\n" + "="*50)
    print(f"抓取任务结束！汇总数据已保存至: {output_file}")
    print("="*50)
    
    return all_results

def run_ths_crawler(config):
    """运行同花顺个股新闻爬虫"""
    if not config.get('enabled', False):
        return {}
    
    # 使用stderr避免多线程stdout竞争
    import sys
    print("\n" + "="*50, file=sys.stderr)
    print("同花顺个股新闻爬虫", file=sys.stderr)
    print("="*50, file=sys.stderr)
    
    stock_list = config.get('stocks', [])
    days = config.get('days', 7)
    
    end_date = datetime.now().strftime("%Y-%m-%d")
    start_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
    
    print(f"开始批量爬取任务，共 {len(stock_list)} 只股票...", file=sys.stderr)
    print(f"爬取模式: 日期范围 {start_date} 至 {end_date}", file=sys.stderr)
    
    all_results = {}
    
    for code in stock_list:
        try:
            crawler = THSNewsCrawler(code)
            news_list = crawler.crawl(start_date=start_date, end_date=end_date)
            
            # 保存单独的 JSON 文件
            crawler.save_to_json(news_list)
            
            all_results[code] = {
                "source": "同花顺",
                "count": len(news_list),
                "news": news_list
            }
            print(f"[OK] 股票 {code} 爬取完成，获取 {len(news_list)} 条新闻", file=sys.stderr)
        except Exception as e:
            print(f"[ERR] 股票 {code} 爬取失败: {e}", file=sys.stderr)
    
    return all_results


def run_semitronix_crawler(config):
    """运行广立微官网新闻爬虫"""
    if not config.get('enabled', False):
        return {}
    
    print("\n" + "="*50)
    print("广立微官网新闻爬虫")
    print("="*50)
    
    max_pages = config.get('max_pages', 10)
    days = config.get('days', 7)
    
    try:
        crawler = SemitronixNewsCrawler()
        news_list = crawler.crawl(max_pages=max_pages, days=days)
        
        # 保存单独的 JSON 文件
        crawler.save_to_json(news_list)
        
        # 返回统一格式
        result = {
            "semitronix": {
                "source": "广立微官网",
                "count": len(news_list),
                "news": news_list
            }
        }
        print(f"[OK] 广立微官网爬取完成，获取 {len(news_list)} 条新闻（最近{days}天）")
        return result
    except Exception as e:
        print(f"[ERR] 广立微官网爬取失败: {e}")
        return {}


def run_primarius_crawler(config):
    """运行概伦电子官网新闻爬虫"""
    if not config.get('enabled', False):
        return {}
    
    print("\n" + "="*50)
    print("概伦电子官网新闻爬虫")
    print("="*50)
    
    max_pages = config.get('max_pages', 10)
    days = config.get('days', 7)
    
    try:
        crawler = PrimariusNewsCrawler()
        news_list = crawler.crawl(max_pages=max_pages, days=days)
        
        # 保存单独的 JSON 文件
        crawler.save_to_json(news_list)
        
        # 返回统一格式
        result = {
            "primarius": {
                "source": "概伦电子官网",
                "count": len(news_list),
                "news": news_list
            }
        }
        print(f"[OK] 概伦电子官网爬取完成，获取 {len(news_list)} 条新闻（最近{days}天）")
        return result
    except Exception as e:
        print(f"[ERR] 概伦电子官网爬取失败: {e}")
        return {}


def run_univista_crawler(config):
    """运行合见工软官网新闻爬虫"""
    if not config.get('enabled', False):
        return {}
    
    print("\n" + "="*50)
    print("合见工软官网新闻爬虫")
    print("="*50)
    
    max_pages = config.get('max_pages', 5)
    days = config.get('days', 7)
    
    try:
        crawler = UnivistiaNewsCrawler()
        news_list = crawler.crawl(max_pages=max_pages, days=days)
        
        # 保存单独的 JSON 文件
        crawler.save_to_json(news_list)
        
        # 返回统一格式
        result = {
            "univista": {
                "source": "合见工软官网",
                "count": len(news_list),
                "news": news_list
            }
        }
        print(f"[OK] 合见工软官网爬取完成，获取 {len(news_list)} 条新闻（最近{days}天）")
        return result
    except Exception as e:
        print(f"[ERR] 合见工软官网爬取失败: {e}")
        return {}


def run_xepic_crawler(config):
    """运行芯华章官网新闻爬虫"""
    if not config.get('enabled', False):
        return {}
    
    print("\n" + "="*50)
    print("芯华章官网新闻爬虫")
    print("="*50)
    
    max_pages = config.get('max_pages', 5)
    days = config.get('days', 7)
    
    try:
        crawler = XepicNewsCrawler()
        news_list = crawler.crawl(max_pages=max_pages, days=days)
        
        # 保存单独的 JSON 文件
        crawler.save_to_json(news_list)
        
        # 返回统一格式
        result = {
            "xepic": {
                "source": "芯华章官网",
                "count": len(news_list),
                "news": news_list
            }
        }
        print(f"[OK] 芯华章官网爬取完成，获取 {len(news_list)} 条新闻（最近{days}天）")
        return result
    except Exception as e:
        print(f"[ERR] 芯华章官网爬取失败: {e}")
        return {}


def run_seccw_crawler(config):
    """运行深圳电子商会新闻爬虫"""
    if not config.get('enabled', False):
        return {}
    
    print("\n" + "="*50)
    print("深圳电子商会新闻爬虫 (EDA关键词)")
    print("="*50)
    
    max_pages = config.get('max_pages', 5)
    days = config.get('days', 7)
    keyword = config.get('keyword', 'EDA')
    
    try:
        crawler = SeccwNewsCrawler(keyword=keyword)
        news_list = crawler.crawl(max_pages=max_pages, days=days)
        
        # 保存单独的 JSON 文件
        crawler.save_to_json(news_list)
        
        # 返回统一格式
        result = {
            "seccw": {
                "source": "深圳电子商会",
                "count": len(news_list),
                "news": news_list
            }
        }
        print(f"[OK] 深圳电子商会爬取完成，获取 {len(news_list)} 条新闻（最近{days}天）")
        return result
    except Exception as e:
        print(f"[ERR] 深圳电子商会爬取失败: {e}")
        return {}


def run_dramx_crawler(config):
    """运行全球半导体观察新闻爬虫"""
    if not config.get('enabled', False):
        return {}
    
    print("\n" + "="*50)
    print("全球半导体观察新闻爬虫 (EDA)")
    print("="*50)
    
    max_pages = config.get('max_pages', 1)
    days = config.get('days', 7)
    
    try:
        crawler = DramxNewsCrawler()
        news_list = crawler.crawl(max_pages=max_pages, days=days)
        
        # 保存单独的 JSON 文件
        crawler.save_to_json(news_list)
        
        # 返回统一格式
        result = {
            "dramx": {
                "source": "全球半导体观察",
                "count": len(news_list),
                "news": news_list
            }
        }
        print(f"[OK] 全球半导体观察爬取完成，获取 {len(news_list)} 条新闻（最近{days}天）")
        return result
    except Exception as e:
        print(f"[ERR] 全球半导体观察爬取失败: {e}")
        return {}


def run_synopsys_crawler(config):
    """运行 Synopsys 新闻爬虫"""
    if not config.get('enabled', False):
        return {}
    
    print("\n" + "="*50)
    print("Synopsys 新闻爬虫 (SemiWiki/Design-Reuse/官网)")
    print("="*50)
    
    max_pages = config.get('max_pages', 1)
    days = config.get('days', 7)
    
    try:
        crawler = SynopsysNewsCrawler()
        news_list = crawler.crawl(max_pages=max_pages, days=days)
        
        # 保存单独的 JSON 文件
        crawler.save_to_json(news_list)
        
        # 返回统一格式 - 按来源分组
        result = {}
        for news in news_list:
            source = news.get('source', 'Synopsys')
            key = f"synopsys_{source.lower().replace('-', '_').replace(' ', '_')}"
            if key not in result:
                result[key] = {
                    "source": source,
                    "count": 0,
                    "news": []
                }
            result[key]["news"].append(news)
            result[key]["count"] = len(result[key]["news"])
        
        print(f"[OK] Synopsys 爬取完成，获取 {len(news_list)} 条新闻（最近{days}天）")
        return result
    except Exception as e:
        print(f"[ERR] Synopsys 爬取失败: {e}")
        return {}


def run_cadence_crawler(config):
    """运行 Cadence 新闻爬虫"""
    if not config.get('enabled', False):
        return {}

    print("\n" + "="*50)
    print("Cadence 新闻爬虫 (SemiWiki/Design-Reuse)")
    print("="*50)

    max_pages = config.get('max_pages', 1)
    days = config.get('days', 7)

    try:
        crawler = CadenceNewsCrawler()
        news_list = crawler.crawl(max_pages=max_pages, days=days)

        # 保存单独的 JSON 文件
        crawler.save_to_json(news_list)

        # 返回统一格式 - 按来源分组
        result = {}
        for news in news_list:
            source = news.get('source', 'Cadence')
            key = f"cadence_{source.lower().replace('-', '_').replace(' ', '_')}"
            if key not in result:
                result[key] = {
                    "source": source,
                    "count": 0,
                    "news": []
                }
            result[key]["news"].append(news)
            result[key]["count"] = len(result[key]["news"])

        print(f"[OK] Cadence 爬取完成，获取 {len(news_list)} 条新闻（最近{days}天）")
        return result
    except Exception as e:
        print(f"[ERR] Cadence 爬取失败: {e}")
        return {}


def run_siemens_crawler(config):
    """运行 Siemens 新闻爬虫"""
    if not config.get('enabled', False):
        return {}

    print("\n" + "="*50)
    print("Siemens EDA 新闻爬虫 (SemiWiki/Design-Reuse)")
    print("="*50)

    max_pages = config.get('max_pages', 1)
    days = config.get('days', 7)

    try:
        crawler = SiemensNewsCrawler()
        news_list = crawler.crawl(max_pages=max_pages, days=days)

        # 保存单独的 JSON 文件
        crawler.save_to_json(news_list)

        # 返回统一格式 - 按来源分组
        result = {}
        for news in news_list:
            source = news.get('source', 'Siemens')
            key = f"siemens_{source.lower().replace('-', '_').replace(' ', '_')}"
            if key not in result:
                result[key] = {
                    "source": source,
                    "count": 0,
                    "news": []
                }
            result[key]["news"].append(news)
            result[key]["count"] = len(result[key]["news"])

        print(f"[OK] Siemens 爬取完成，获取 {len(news_list)} 条新闻（最近{days}天）")
        return result
    except Exception as e:
        print(f"[ERR] Siemens 爬取失败: {e}")
        return {}


def run_eetimes_crawler(config):
    """运行 EETimes 新闻爬虫"""
    if not config.get('enabled', False):
        return {}

    print("\n" + "="*50)
    print("EETimes 新闻爬虫")
    print("="*50)

    max_pages = config.get('max_pages', 1)
    days = config.get('days', 7)
    keywords = config.get('keywords', ['synopsys', 'cadence', 'siemens'])

    try:
        crawler = EETimesNewsCrawler()
        news_list = crawler.crawl(max_pages=max_pages, days=days, keywords=keywords)
        crawler.save_to_json(news_list)

        result = {}
        if news_list:
            result['eetimes'] = {
                'source': 'EETimes',
                'count': len(news_list),
                'news': news_list
            }

        print(f"[OK] EETimes 爬取完成，获取 {len(news_list)} 条新闻（最近{days}天）")
        return result
    except Exception as e:
        print(f"[ERR] EETimes 爬取失败: {e}")
        return {}


def run_s2c_crawler(config):
    """运行思尔芯官网新闻爬虫"""
    if not config.get('enabled', False):
        return {}

    print("\n" + "="*50)
    print("思尔芯官网新闻爬虫")
    print("="*50)

    max_pages = config.get('max_pages', 3)
    days = config.get('days', 30)

    try:
        crawler = S2CNewsCrawler()
        news_list = crawler.crawl(max_pages=max_pages, days=days)
        crawler.save_to_json(news_list)

        result = {}
        if news_list:
            result['s2c'] = {
                'source': '思尔芯官网',
                'count': len(news_list),
                'news': news_list
            }

        print(f"[OK] 思尔芯 爬取完成，获取 {len(news_list)} 条新闻（最近{days}天）")
        return result
    except Exception as e:
        print(f"[ERR] 思尔芯 爬取失败: {e}")
        return {}


def run_gigada_crawler(config):
    """运行鸿芯微纳官网新闻爬虫"""
    if not config.get('enabled', False):
        return {}

    print("\n" + "="*50)
    print("鸿芯微纳官网新闻爬虫")
    print("="*50)

    max_pages = config.get('max_pages', 5)
    days = config.get('days', 30)

    try:
        crawler = GigaDANewsCrawler()
        news_list = crawler.crawl(max_pages=max_pages, days=days)
        crawler.save_to_json(news_list)

        result = {}
        if news_list:
            result['gigada'] = {
                'source': '鸿芯微纳官网',
                'count': len(news_list),
                'news': news_list
            }

        print(f"[OK] 鸿芯微纳 爬取完成，获取 {len(news_list)} 条新闻（最近{days}天）")
        return result
    except Exception as e:
        print(f"[ERR] 鸿芯微纳 爬取失败: {e}")
        return {}


def run_xpeedic_crawler(config):
    """运行芯和半导体官网新闻爬虫"""
    if not config.get('enabled', False):
        return {}

    print("\n" + "="*50)
    print("芯和半导体官网新闻爬虫")
    print("="*50)

    max_pages = config.get('max_pages', 3)
    days = config.get('days', 30)

    try:
        crawler = XpedicNewsCrawler()
        news_list = crawler.crawl(max_pages=max_pages, days=days)
        crawler.save_to_json(news_list)

        result = {}
        if news_list:
            result['xpeedic'] = {
                'source': '芯和半导体官网',
                'count': len(news_list),
                'news': news_list
            }

        print(f"[OK] 芯和半导体 爬取完成，获取 {len(news_list)} 条新闻（最近{days}天）")
        return result
    except Exception as e:
        print(f"[ERR] 芯和半导体 爬取失败: {e}")
        return {}


def run_sina_crawler(config):
    """运行新浪网新闻爬虫"""
    if not config.get('enabled', False):
        return {}

    print("\n" + "="*50)
    print("新浪网新闻爬虫")
    print("="*50)

    max_pages = config.get('max_pages', 3)
    days = config.get('days', 7)
    keyword = config.get('keyword', 'EDA')

    try:
        crawler = SinaNewsCrawler(keyword=keyword)
        news_list = crawler.crawl(max_pages=max_pages, days=days)
        crawler.save_to_json(news_list)

        result = {}
        if news_list:
            result['sina'] = {
                'source': '新浪网',
                'count': len(news_list),
                'news': news_list
            }

        print(f"[OK] 新浪网 爬取完成，获取 {len(news_list)} 条新闻（最近{days}天）")
        return result
    except Exception as e:
        print(f"[ERR] 新浪网 爬取失败: {e}")
        return {}


def run_qq_crawler(config):
    """运行腾讯网新闻爬虫"""
    if not config.get('enabled', False):
        return {}

    print("\n" + "="*50)
    print("腾讯网新闻爬虫")
    print("="*50)

    max_pages = config.get('max_pages', 3)
    days = config.get('days', 7)
    keyword = config.get('keyword', 'EDA')

    try:
        crawler = QQNewsCrawler(keyword=keyword)
        news_list = crawler.crawl(max_pages=max_pages, days=days)
        crawler.save_to_json(news_list)

        result = {}
        if news_list:
            result['qq'] = {
                'source': '腾讯网',
                'count': len(news_list),
                'news': news_list
            }

        print(f"[OK] 腾讯网 爬取完成，获取 {len(news_list)} 条新闻（最近{days}天）")
        return result
    except Exception as e:
        print(f"[ERR] 腾讯网 爬取失败: {e}")
        return {}


def run_sohu_crawler(config):
    """运行搜狐网新闻爬虫"""
    if not config.get('enabled', False):
        return {}

    print("\n" + "="*50)
    print("搜狐网新闻爬虫")
    print("="*50)

    max_pages = config.get('max_pages', 3)
    days = config.get('days', 7)
    keyword = config.get('keyword', 'EDA')

    try:
        crawler = SohuNewsCrawler(keyword=keyword)
        news_list = crawler.crawl(max_pages=max_pages, days=days)
        crawler.save_to_json(news_list)

        result = {}
        if news_list:
            result['sohu'] = {
                'source': '搜狐网',
                'count': len(news_list),
                'news': news_list
            }

        print(f"[OK] 搜狐网 爬取完成，获取 {len(news_list)} 条新闻（最近{days}天）")
        return result
    except Exception as e:
        print(f"[ERR] 搜狐网 爬取失败: {e}")
        return {}


def run_bing_crawler(config):
    """运行 Bing 新闻爬虫"""
    if not config.get('enabled', False):
        return {}

    print("\n" + "="*50)
    print("Bing 新闻爬虫")
    print("="*50)

    max_pages = config.get('max_pages', 1)
    days = config.get('days', 7)
    min_content_length = config.get('min_content_length', 0)
    keyword = config.get('keyword', 'EDA')

    try:
        crawler = BingNewsCrawler(keyword=keyword)
        news_list = crawler.crawl(max_pages=max_pages, days=days, min_content_length=min_content_length)
        crawler.save_to_json(news_list)

        result = {}
        if news_list:
            result['bing'] = {
                'source': 'Bing新闻',
                'count': len(news_list),
                'news': news_list
            }

        print(f"[OK] Bing新闻 爬取完成，获取 {len(news_list)} 条新闻（最近{days}天）")
        return result
    except Exception as e:
        print(f"[ERR] Bing新闻 爬取失败: {e}")
        return {}


def run_iwencai_crawler(config):
    """运行问财网新闻爬虫，支持多关键词"""
    if not config.get('enabled', False):
        return {}

    print("\n" + "="*50)
    print("问财网新闻爬虫")
    print("="*50)

    max_pages = config.get('max_pages', 1)
    days = config.get('days', 7)
    min_content_length = config.get('min_content_length', 0)
    
    # 支持多关键词（兼容旧的单关键词配置）
    keywords = config.get('keywords', [])
    if not keywords:
        keywords = [config.get('keyword', 'EDA')]

    try:
        all_news = []
        seen_links = set()
        
        for keyword in keywords:
            crawler = IWenCaiNewsCrawler(keyword=keyword)
            news_list = crawler.crawl(max_pages=max_pages, days=days, min_content_length=min_content_length)
            
            # 去重
            for news in news_list:
                link = news.get('link', '')
                if link and link not in seen_links:
                    seen_links.add(link)
                    all_news.append(news)
        
        # 保存合并后的结果
        if all_news:
            crawler = IWenCaiNewsCrawler(keyword=keywords[0])
            crawler.save_to_json(all_news)

        result = {}
        if all_news:
            result['iwencai'] = {
                'source': '问财网',
                'count': len(all_news),
                'news': all_news
            }

        print(f"[OK] 问财网 爬取完成，获取 {len(all_news)} 条新闻（最近{days}天，关键词: {', '.join(keywords)}）")
        return result
    except Exception as e:
        print(f"[ERR] 问财网 爬取失败: {e}")
        return {}


def run_laoyaoba_crawler(config):
    """运行集微网新闻爬虫，支持多关键词"""
    if not config.get('enabled', False):
        return {}

    print("\n" + "="*50)
    print("集微网新闻爬虫")
    print("="*50)

    max_pages = config.get('max_pages', 2)
    days = config.get('days', 30)
    min_content_length = config.get('min_content_length', 0)
    
    # 支持多关键词（兼容旧的单关键词配置）
    keywords = config.get('keywords', [])
    if not keywords:
        keywords = [config.get('keyword', 'EDA')]

    try:
        all_news = []
        seen_links = set()
        
        for keyword in keywords:
            crawler = LaoyaobaNewsCrawler(keyword=keyword)
            news_list = crawler.crawl(max_pages=max_pages, days=days, min_content_length=min_content_length)
            
            # 去重
            for news in news_list:
                link = news.get('link', '')
                if link and link not in seen_links:
                    seen_links.add(link)
                    all_news.append(news)
        
        # 保存合并后的结果
        if all_news:
            crawler = LaoyaobaNewsCrawler(keyword=keywords[0])
            crawler.save_to_json(all_news)

        result = {}
        if all_news:
            result['laoyaoba'] = {
                'source': '集微网',
                'count': len(all_news),
                'news': all_news
            }

        print(f"[OK] 集微网 爬取完成，获取 {len(all_news)} 条新闻（最近{days}天，关键词: {', '.join(keywords)}）")
        return result
    except Exception as e:
        print(f"[ERR] 集微网 爬取失败: {e}")
        return {}


def run_designnews_crawler(config):
    if not config.get('enabled', False):
        return {}

    print("\n" + "="*50)
    print("Design News 爬虫")
    print("="*50)

    max_pages = config.get('max_pages', 1)
    days = config.get('days', 7)
    min_content_length = config.get('min_content_length', 0)
    keywords = config.get('keywords', [])
    if not keywords:
        keywords = [config.get('keyword', 'EDA')]

    try:
        crawler = DesignNewsCrawler(keyword=keywords[0])
        news_list = crawler.crawl(
            max_pages=max_pages,
            days=days,
            min_content_length=min_content_length,
            keywords=keywords
        )
        crawler.save_to_json(news_list)
        result = {}
        if news_list:
            result['designnews'] = {
                'source': 'Design News',
                'count': len(news_list),
                'news': news_list
            }
        print(f"[OK] Design News 爬取完成，获取 {len(news_list)} 条新闻（最近{days}天，关键词: {', '.join(keywords)}）")
        return result
    except Exception as e:
        print(f"[ERR] Design News 爬取失败: {e}")
        return {}


def run_digitimes_crawler(config):
    if not config.get('enabled', False):
        return {}

    print("\n" + "="*50)
    print("DIGITIMES 爬虫")
    print("="*50)

    max_pages = config.get('max_pages', 1)
    days = config.get('days', 7)
    min_content_length = config.get('min_content_length', 0)
    keywords = config.get('keywords', [])
    if not keywords:
        keywords = [config.get('keyword', 'EDA')]

    try:
        crawler = DigitimesNewsCrawler(keyword=keywords[0])
        news_list = crawler.crawl(
            max_pages=max_pages,
            days=days,
            min_content_length=min_content_length,
            keywords=keywords
        )
        crawler.save_to_json(news_list)
        result = {}
        if news_list:
            result['digitimes'] = {
                'source': 'DIGITIMES',
                'count': len(news_list),
                'news': news_list
            }
        print(f"[OK] DIGITIMES 爬取完成，获取 {len(news_list)} 条新闻（最近{days}天，关键词: {', '.join(keywords)}）")
        return result
    except Exception as e:
        print(f"[ERR] DIGITIMES 爬取失败: {e}")
        return {}


def run_eastmoney_crawler(config):
    if not config.get('enabled', False):
        return {}

    print("\n" + "="*50)
    print("东方财富网爬虫")
    print("="*50)

    max_pages = config.get('max_pages', 1)
    days = config.get('days', 7)
    min_content_length = config.get('min_content_length', 0)
    keywords = config.get('keywords', [])
    if not keywords:
        keywords = [config.get('keyword', 'EDA')]

    try:
        crawler = EastmoneyNewsCrawler(keyword=keywords[0])
        news_list = crawler.crawl(
            max_pages=max_pages,
            days=days,
            min_content_length=min_content_length,
            keywords=keywords
        )
        crawler.save_to_json(news_list)
        result = {}
        if news_list:
            result['eastmoney'] = {
                'source': '东方财富网',
                'count': len(news_list),
                'news': news_list
            }
        print(f"[OK] 东方财富网 爬取完成，获取 {len(news_list)} 条新闻（最近{days}天，关键词: {', '.join(keywords)}）")
        return result
    except Exception as e:
        print(f"[ERR] 东方财富网 爬取失败: {e}")
        return {}


def run_eechina_crawler(config):
    """运行电子工程网新闻爬虫"""
    if not config.get('enabled', False):
        return {}

    print("\n" + "="*50)
    print("电子工程网新闻爬虫")
    print("="*50)

    max_pages = config.get('max_pages', 3)
    days = config.get('days', 30)
    min_content_length = config.get('min_content_length', 500)
    keyword = config.get('keyword', 'EDA')

    try:
        crawler = EEChinaNewsCrawler(keyword=keyword)
        news_list = crawler.crawl(max_pages=max_pages, days=days, min_content_length=min_content_length)
        crawler.save_to_json(news_list)

        result = {}
        if news_list:
            result['eechina'] = {
                'source': '电子工程网',
                'count': len(news_list),
                'news': news_list
            }

        print(f"[OK] 电子工程网 爬取完成，获取 {len(news_list)} 条新闻（最近{days}天）")
        return result
    except Exception as e:
        print(f"[ERR] 电子工程网 爬取失败: {e}")
        return {}


def run_eetchina_crawler(config):
    """运行电子工程专辑新闻爬虫"""
    if not config.get('enabled', False):
        return {}

    print("\n" + "="*50)
    print("电子工程专辑新闻爬虫")
    print("="*50)

    max_pages = config.get('max_pages', 10)
    days = config.get('days', 90)
    min_content_length = config.get('min_content_length', 500)
    keyword = config.get('keyword', 'eda')

    try:
        crawler = EETChinaNewsCrawler(keyword=keyword)
        news_list = crawler.crawl(max_pages=max_pages, days=days, min_content_length=min_content_length)
        crawler.save_to_json(news_list)

        result = {}
        if news_list:
            result['eetchina'] = {
                'source': '电子工程专辑',
                'count': len(news_list),
                'news': news_list
            }

        print(f"[OK] 电子工程专辑 爬取完成，获取 {len(news_list)} 条新闻（最近{days}天）")
        return result
    except Exception as e:
        print(f"[ERR] 电子工程专辑 爬取失败: {e}")
        return {}


def run_eeworld_crawler(config):
    """运行电子工程世界新闻爬虫"""
    if not config.get('enabled', False):
        return {}

    print("\n" + "="*50)
    print("电子工程世界新闻爬虫")
    print("="*50)

    max_pages = config.get('max_pages', 10)
    days = config.get('days', 30)
    min_content_length = config.get('min_content_length', 500)
    keyword = config.get('keyword', 'EDA')

    try:
        crawler = EEWorldNewsCrawler(keyword=keyword)
        news_list = crawler.crawl(max_pages=max_pages, days=days, min_content_length=min_content_length)
        crawler.save_to_json(news_list)

        result = {}
        if news_list:
            result['eeworld'] = {
                'source': '电子工程世界',
                'count': len(news_list),
                'news': news_list
            }

        print(f"[OK] 电子工程世界 爬取完成，获取 {len(news_list)} 条新闻（最近{days}天）")
        return result
    except Exception as e:
        print(f"[ERR] 电子工程世界 爬取失败: {e}")
        return {}


def convert_to_new_format(raw_results):
    """
    将爬取结果转换为新格式：
    公司名称 -> 新闻来源 -> 新闻列表
    """
    formatted = {}
    
    for key, data in raw_results.items():
        # 处理 Synopsys/Cadence/Siemens 系列的 key
        if key.startswith('synopsys_'):
            company_name = "Synopsys"
        elif key.startswith('cadence_'):
            company_name = "Cadence"
        elif key.startswith('siemens_'):
            company_name = "Siemens"
        elif key == 'eetimes':
            company_name = "EETimes"
        elif key == 's2c':
            company_name = "思尔芯"
        elif key == 'gigada':
            company_name = "鸿芯微纳"
        elif key == 'xpeedic':
            company_name = "芯和半导体"
        elif key == 'sina':
            company_name = "行业新闻"
        elif key == 'qq':
            company_name = "行业新闻"
        elif key == 'sohu':
            company_name = "行业新闻"
        elif key == 'bing':
            company_name = "行业新闻"
        elif key == 'iwencai':
            company_name = "行业新闻"
        elif key == 'eechina':
            company_name = "行业新闻"
        elif key == 'eetchina':
            company_name = "行业新闻"
        elif key == 'eeworld':
            company_name = "行业新闻"
        else:
            company_name = COMPANY_NAMES.get(key, key)
        source = data.get('source', '未知来源')
        news_list = data.get('news', [])
        
        # 初始化公司字典
        if company_name not in formatted:
            formatted[company_name] = {}
        
        # 初始化来源列表
        if source not in formatted[company_name]:
            formatted[company_name][source] = []
        
        # 添加新闻（只保留标题、链接、日期）
        for news in news_list:
            formatted[company_name][source].append({
                'title': news.get('title', ''),
                'link': news.get('link', ''),
                'date': news.get('date', ''),
                'content': news.get('content', '')
            })
    
    return formatted


def main():
    # 静默模式下重定向子模块的stdout
    import io
    class QuietStream:
        """静默模式下的输出流，过滤掉不重要的日志"""
        def __init__(self, original):
            self.original = original
        def write(self, msg):
            if not QUIET_MODE:
                self.original.write(msg)
                return
            # 过滤掉中间日志（以空格开头或包含特定模式的行）
            if not msg or msg == '\n':
                self.original.write(msg)
                return
            # 保留重要输出
            keep_patterns = ['汇总', '统计', '分类', '去重', '保存', '选择', 
                           '提示词', '剪贴板', '结果', '摘要', '示例',
                           '【', '】', '链接:', '总新闻数', '来源统计']
            if any(p in msg for p in keep_patterns):
                self.original.write(msg)
                return
            # 过滤掉详细日志
            skip_patterns = ['正在爬取', '正在启动', '第 ', '页:', '共获取', 
                           '正在获取新闻内容', '日期限制', 'Chrome', 'driver',
                           'Playwright', '切换到', '条新闻', '加载', 'Selenium',
                           '正在处理', '获取内容', '[OK]', '[ERR]', '新闻爬虫',
                           '完成 (', '失败:', '[', ']']
            if any(p in msg for p in skip_patterns):
                return
            self.original.write(msg)
        def flush(self):
            self.original.flush()
    
    if QUIET_MODE:
        sys.stdout = QuietStream(sys.__stdout__)
    
    log("\n" + "#"*60)
    log("#" + " "*20 + "统一新闻爬取系统" + " "*19 + "#")
    log("#"*60)
    
    # ======== 清理旧的输出文件 ========
    base_dir = os.path.dirname(os.path.abspath(__file__))
    json_dir = os.path.join(base_dir, 'json')
    result_dir = os.path.join(base_dir, 'result')
    
    # 清理 json 目录
    if os.path.exists(json_dir):
        for filename in os.listdir(json_dir):
            filepath = os.path.join(json_dir, filename)
            if os.path.isfile(filepath):
                os.remove(filepath)
        log("[OK] 已清理 json 目录下的旧文件")
    
    # 清理 result 目录
    if os.path.exists(result_dir):
        for filename in os.listdir(result_dir):
            filepath = os.path.join(result_dir, filename)
            if os.path.isfile(filepath):
                os.remove(filepath)
        log("[OK] 已清理 result 目录下的旧文件")
    
    all_results = {}
    
    # ======== 并行运行所有爬虫 ========
    log("\n开始并行爬取新闻...")
    
    # 定义所有爬虫任务
    crawler_tasks = [
        ("同花顺", run_ths_crawler, THS_CONFIG),
        ("广立微官网", run_semitronix_crawler, SEMITRONIX_CONFIG),
        ("概伦电子官网", run_primarius_crawler, PRIMARIUS_CONFIG),
        ("合见工软官网", run_univista_crawler, UNIVISTA_CONFIG),
        ("芯华章官网", run_xepic_crawler, XEPIC_CONFIG),
        ("深圳电子商会", run_seccw_crawler, SECCW_CONFIG),
        ("全球半导体观察", run_dramx_crawler, DRAMX_CONFIG),
        ("Synopsys", run_synopsys_crawler, SYNOPSYS_CONFIG),
        ("Cadence", run_cadence_crawler, CADENCE_CONFIG),
        ("Siemens", run_siemens_crawler, SIEMENS_CONFIG),
        ("EETimes", run_eetimes_crawler, EETIMES_CONFIG),
        ("思尔芯", run_s2c_crawler, S2C_CONFIG),
        ("鸿芯微纳", run_gigada_crawler, GIGADA_CONFIG),
        ("芯和半导体", run_xpeedic_crawler, XPEEDIC_CONFIG),
        ("新浪网", run_sina_crawler, SINA_CONFIG),
        ("Bing新闻", run_bing_crawler, BING_CONFIG),
        ("问财网", run_iwencai_crawler, IWENCAI_CONFIG),
        ("集微网", run_laoyaoba_crawler, LAOYAOBA_CONFIG),
        ("Design News", run_designnews_crawler, DESIGNNEWS_CONFIG),
        ("DIGITIMES", run_digitimes_crawler, DIGITIMES_CONFIG),
        ("东方财富网", run_eastmoney_crawler, EASTMONEY_CONFIG),
        # 以下使用Selenium的爬虫，会顺序执行
    ]
    
    # Selenium爬虫（不能并行，单独顺序执行）
    selenium_tasks = [
        ("腾讯网", run_qq_crawler, QQ_CONFIG),
        ("搜狐网", run_sohu_crawler, SOHU_CONFIG),
        ("电子工程网", run_eechina_crawler, EECHINA_CONFIG),
        ("电子工程专辑", run_eetchina_crawler, EETCHINA_CONFIG),
        ("电子工程世界", run_eeworld_crawler, EEWORLD_CONFIG),
    ]
    
    # 过滤已启用的爬虫
    enabled_tasks = [(name, func, config) for name, func, config in crawler_tasks if config.get('enabled', False)]
    selenium_enabled = [(name, func, config) for name, func, config in selenium_tasks if config.get('enabled', False)]
    
    import time
    import threading
    start_time = time.time()
    
    # 用于存储Selenium爬虫结果和共享driver
    selenium_results = {}
    selenium_lock = threading.Lock()
    driver_holder = {'driver': None}  # 使用字典来跨线程传递driver
    
    def run_selenium_crawlers():
        """在单独线程中顺序执行所有Selenium爬虫"""
        if not selenium_enabled:
            return
        
        log("\n" + "-"*40)
        log("【并行线程】开始执行Selenium爬虫（共享driver）...")
        log("-"*40)
        
        try:
            from selenium.webdriver.chrome.options import Options
            
            chrome_options = Options()
            chrome_options.add_argument('--headless=new')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-extensions')
            chrome_options.add_argument('--disable-logging')
            chrome_options.add_argument('--log-level=3')
            # SSL和安全相关选项
            chrome_options.add_argument('--ignore-certificate-errors')
            chrome_options.add_argument('--ignore-ssl-errors')
            chrome_options.add_argument('--allow-insecure-localhost')
            chrome_options.add_argument('--disable-web-security')
            chrome_options.add_argument('--disable-features=IsolateOrigins,site-per-process')
            chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
            chrome_options.add_argument('--disable-blink-features=AutomationControlled')
            chrome_options.add_experimental_option('excludeSwitches', ['enable-logging', 'enable-automation'])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            driver_holder['driver'] = create_chrome_driver(chrome_options)
            driver_holder['driver'].set_page_load_timeout(30)
            log("  Chrome共享driver已启动")
        except Exception as e:
            log(f"  共享driver创建失败: {e}")
            for name, func, config in selenium_enabled:
                try:
                    result = func(config)
                    with selenium_lock:
                        selenium_results.update(result)
                    news_count = sum(v.get('count', 0) if isinstance(v, dict) else 0 for v in result.values())
                    log(f"  [Selenium] {name} 完成 ({news_count}条)")
                except Exception as e:
                    log(f"  [Selenium] {name} 失败: {e}")
            return

        for name, func, config in selenium_enabled:
            try:
                try:
                    driver_holder['driver'].delete_all_cookies()
                    driver_holder['driver'].get('about:blank')
                    time.sleep(1)
                except:
                    pass

                keyword = config.get('keyword', 'EDA')
                max_pages = config.get('max_pages', 10)
                days = config.get('days', 30)

                if name == "电子工程网":
                    crawler = EEChinaNewsCrawler(keyword=keyword)
                    news_list = crawler.crawl(max_pages=max_pages, days=days, shared_driver=driver_holder['driver'])
                    crawler.save_to_json(news_list)
                    result = {'eechina': {'source': '电子工程网', 'news': news_list, 'count': len(news_list)}} if news_list else {}
                elif name == "电子工程专辑":
                    crawler = EETChinaNewsCrawler(keyword=keyword)
                    news_list = crawler.crawl(max_pages=max_pages, days=days, shared_driver=driver_holder['driver'])
                    crawler.save_to_json(news_list)
                    result = {'eetchina': {'source': '电子工程专辑', 'news': news_list, 'count': len(news_list)}} if news_list else {}
                elif name == "电子工程世界":
                    crawler = EEWorldNewsCrawler(keyword=keyword)
                    news_list = crawler.crawl(max_pages=max_pages, days=days, shared_driver=driver_holder['driver'])
                    crawler.save_to_json(news_list)
                    result = {'eeworld': {'source': '电子工程世界', 'news': news_list, 'count': len(news_list)}} if news_list else {}
                elif name in ["腾讯网", "搜狐网"]:
                    result = func(config)
                else:
                    result = {}

                with selenium_lock:
                    selenium_results.update(result)
                news_count = sum(v.get('count', 0) if isinstance(v, dict) else 0 for v in result.values())
                log(f"  [Selenium] {name} 完成 ({news_count}条)")
            except Exception as e:
                log(f"  [Selenium] {name} 失败: {e}")
    
    # 启动Selenium线程（与普通爬虫并行）
    selenium_thread = None
    if selenium_enabled:
        selenium_thread = threading.Thread(target=run_selenium_crawlers, name="SeleniumCrawlers")
        selenium_thread.start()
    
    # 普通爬虫结果存储
    normal_results = {}
    normal_lock = threading.Lock()
    
    def run_normal_crawlers():
        """在单独线程中并行执行所有普通爬虫"""
        nonlocal normal_results
        if not enabled_tasks:
            log("[普通爬虫] 没有启用的任务")
            return
        
        log(f"[普通爬虫] 开始执行，共 {len(enabled_tasks)} 个任务")
        log(f"\n开始并行爬取 {len(enabled_tasks)} 个普通来源...")
        try:
            log("[普通爬虫] 创建 ThreadPoolExecutor...")
            with ThreadPoolExecutor(max_workers=8) as executor:
                future_to_name = {}
                for name, func, config in enabled_tasks:
                    try:
                        future = executor.submit(func, config)
                        future_to_name[future] = name
                    except Exception as submit_err:
                        log(f"  [!] 提交 {name} 失败: {submit_err}")
                
                completed_count = 0
                for future in as_completed(future_to_name):
                    name = future_to_name[future]
                    completed_count += 1
                    try:
                        result = future.result()
                        with normal_lock:
                            normal_results.update(result)
                        news_count = 0
                        if result:
                            for v in result.values():
                                if isinstance(v, dict):
                                    for vv in v.values():
                                        if isinstance(vv, list):
                                            news_count += len(vv)
                                        elif isinstance(vv, int):
                                            news_count += vv
                                elif isinstance(v, list):
                                    news_count += len(v)
                        log(f"  [{completed_count}/{len(enabled_tasks)}] {name} 完成 ({news_count}条)")
                    except Exception as e:
                        log(f"  [{completed_count}/{len(enabled_tasks)}] {name} 失败: {e}")
        except Exception as e:
            log(f"[ERR] ThreadPoolExecutor异常: {e}")
            import traceback
            traceback.print_exc()
    
    # 启动普通爬虫线程（与Selenium爬虫并行）
    normal_thread = None
    if enabled_tasks:
        normal_thread = threading.Thread(target=run_normal_crawlers, name="NormalCrawlers")
        normal_thread.start()
    
    # 等待两个线程都完成
    if normal_thread:
        normal_thread.join()
        all_results.update(normal_results)
    
    if selenium_thread:
        selenium_thread.join()
        all_results.update(selenium_results)
    
    elapsed = time.time() - start_time
    log(f"\n爬取完成，耗时 {elapsed:.1f} 秒")
    
    # ======== 保存汇总结果 ========
    if all_results:
        # 转换为新格式：公司名称 -> 来源 -> 新闻列表
        formatted_results = convert_to_new_format(all_results)
        
        output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'json')
        os.makedirs(output_dir, exist_ok=True)
        output_file = os.path.join(output_dir, "batch_news_results.json")
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(formatted_results, f, ensure_ascii=False, indent=2)
        
        print("\n" + "="*50)
        print(f"所有爬虫任务完成！汇总数据已保存至: {output_file}")
        print("="*50)
        
        # 统计汇总（已屏蔽）
        total_news = sum(data.get('count', 0) for data in all_results.values())
    
    # ======== 自动执行分类 ========
    if all_results:
        # 使用转换后的格式进行分类
        formatted_results = convert_to_new_format(all_results)
        
        # 统计爬取总数
        crawl_total = sum(len(news_list) for sources in formatted_results.values() for news_list in sources.values())
        
        print("\n开始自动分类新闻...")
        print("="*50)
        print(f"【Step 1】爬取完成: {crawl_total} 条")
        
        # 创建分类器
        classifier = NewsClassifier()
        target_categories = ["财务相关", "战略合作", "技术研发", "行业分析"]
        skip_sources = ["EETimes"]  # EETimes已用synopsys/cadence/siemens搜索，直接保留
        category_only_sources = ["广立微官网", "概伦电子官网", "合见工软官网", "芯华章官网", "深圳电子商会", "全球半导体观察", "思尔芯官网", "鸿芯微纳官网", "芯和半导体官网", "新浪网", "腾讯网", "搜狐网", "Bing新闻", "问财网", "集微网", "Design News", "DIGITIMES", "东方财富网", "电子工程网", "电子工程专辑", "电子工程世界"]  # 公司官网和行业新闻只做分类筛选，不限公司相关
        company_only_sources = ["SemiWiki", "Design-Reuse", "Synopsys官网", "Cadence官网", "Siemens官网"]  # 只做公司相关筛选，不做分类筛选
        
        print(f"\n过滤规则:")
        print(f"  · 同花顺: {', '.join(target_categories)} 四类 + 公司直接相关")
        print(f"  · 公司官网: {', '.join(target_categories)} 四类（不限公司相关）")
        print(f"    [{', '.join([s for s in category_only_sources if '官网' in s])}]")
        print(f"  · 行业新闻: {', '.join(target_categories)} 四类（不限公司相关）")
        print(f"    [{', '.join([s for s in category_only_sources if '官网' not in s])}]")
        print(f"  · 第三方新闻: 只筛选公司相关（不做分类筛选）")
        print(f"    [{', '.join(company_only_sources)}]")
        print(f"  · 跳过筛选: [{', '.join(skip_sources)}]")
        
        # 执行分类（两层筛选）- 使用转换后的格式
        classified_results = classifier.classify_batch(
            formatted_results, 
            filter_categories=target_categories,
            only_company_related=True,
            skip_filter_sources=skip_sources,
            category_only_sources=category_only_sources,
            company_only_sources=company_only_sources
        )
        
        # 统计分类筛选后数量
        classify_total = sum(len(news_list) for sources in classified_results.values() for news_list in sources.values())
        print(f"\n【Step 2】分类筛选: {crawl_total} 条 → {classify_total} 条（过滤 {crawl_total - classify_total} 条）")
        
        # 按日期排序（最新的优先）
        for company_name in classified_results:
            for source_name in classified_results[company_name]:
                classified_results[company_name][source_name].sort(
                    key=lambda x: x.get('date', ''), reverse=True
                )
        
        # 去重：去掉标题重复的新闻（跨来源去重）
        seen_titles = set()
        total_before = sum(len(news_list) for sources in classified_results.values() for news_list in sources.values())
        for company_name in classified_results:
            for source_name in classified_results[company_name]:
                unique_news = []
                for news in classified_results[company_name][source_name]:
                    title = news.get('title', '').strip()
                    if title and title not in seen_titles:
                        seen_titles.add(title)
                        unique_news.append(news)
                classified_results[company_name][source_name] = unique_news
        total_after = sum(len(news_list) for sources in classified_results.values() for news_list in sources.values())
        print(f"【Step 3】标题去重: {total_before} 条 → {total_after} 条（去掉 {total_before - total_after} 条重复）")
        print(f"\n最终结果: {total_after} 条新闻")
        print("="*50)
        
        # 保存分类结果
        classifier.save_classified_results(classified_results)
        
        # 统计摘要和详细示例已屏蔽
        if not classified_results:
            print("\n[!] 警告: 所有股票的新闻都被过滤掉了，没有符合条件的新闻")
        
    # ======== 结束 ========
        
    # 显示所有新闻链接供用户选择（树状结构）
    all_news = []
    global_index = 1
        
    if classified_results:
        print("\n正在检查新闻内容（并行获取中）...")
        print("-" * 60)
        
        # 先收集所有新闻及其内容
        news_by_company = {}  # {公司名: {来源: [(news, content, content_len)]}}
        
        # 创建爬虫实例用于获取内容
        xepic_crawler = XepicNewsCrawler()
        semitronix_crawler = SemitronixNewsCrawler()
        primarius_crawler = PrimariusNewsCrawler()
        univista_crawler = UnivistiaNewsCrawler()
        seccw_crawler = SeccwNewsCrawler()
        dramx_crawler = DramxNewsCrawler()
        synopsys_crawler = SynopsysNewsCrawler()
        cadence_crawler = CadenceNewsCrawler()
        siemens_crawler = SiemensNewsCrawler()
        eetimes_crawler = EETimesNewsCrawler()
        s2c_crawler = S2CNewsCrawler()
        gigada_crawler = GigaDANewsCrawler()
        xpeedic_crawler = XpedicNewsCrawler()
        sina_crawler = SinaNewsCrawler()
        qq_crawler = QQNewsCrawler()
        sohu_crawler = SohuNewsCrawler()
        bing_crawler = BingNewsCrawler()
        iwencai_crawler = IWenCaiNewsCrawler()
        laoyaoba_crawler = LaoyaobaNewsCrawler()
        designnews_crawler = DesignNewsCrawler()
        digitimes_crawler = DigitimesNewsCrawler()
        eastmoney_crawler = EastmoneyNewsCrawler()
        
        # 收集所有需要获取内容的新闻
        all_news_items = []
        for company_name, sources in classified_results.items():
            for source_name, news_list in sources.items():
                for news in news_list:
                    all_news_items.append({
                        'company': company_name,
                        'source': source_name,
                        'news': news
                    })
        content_cache = {}
        cache_lock = threading.Lock()
        content_cache_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'json', 'content_cache.json')
        try:
            if os.path.exists(content_cache_file):
                with open(content_cache_file, 'r', encoding='utf-8') as f:
                    persisted_cache = json.load(f)
                    if isinstance(persisted_cache, dict):
                        for k, v in persisted_cache.items():
                            if isinstance(v, dict):
                                cached_text = v.get('content', '')
                            else:
                                cached_text = v if isinstance(v, str) else ''
                            if cached_text and len(cached_text) >= 200:
                                content_cache[k] = cached_text
        except Exception:
            pass
        
        # 定义获取单条新闻内容的函数
        def fetch_single_news(item):
            source_name = item['source']
            news = item['news']
            try:
                cached_content = news.get('content', '')
                if cached_content and len(cached_content) >= 200:
                    return {**item, 'content': cached_content, 'content_len': len(cached_content)}
                link = news.get('link', '')
                if link:
                    with cache_lock:
                        cached_by_link = content_cache.get(link, '')
                    cache_bypass_sources = {"合见工软官网", "广立微官网", "概伦电子官网"}
                    if source_name not in cache_bypass_sources and cached_by_link and len(cached_by_link) >= 200:
                        return {**item, 'content': cached_by_link, 'content_len': len(cached_by_link)}
                if source_name == "芯华章官网":
                    content = xepic_crawler.fetch_news_content(news['link'])
                elif source_name == "广立微官网":
                    content = semitronix_crawler.fetch_news_content(news['link'])
                elif source_name == "概伦电子官网":
                    content = primarius_crawler.fetch_news_content(news['link'])
                elif source_name == "合见工软官网":
                    content = univista_crawler.fetch_news_content(news['link'])
                elif source_name == "深圳电子商会":
                    content = seccw_crawler.fetch_news_content(news['link'])
                elif source_name == "全球半导体观察":
                    content = dramx_crawler.fetch_news_content(news['link'])
                elif source_name in ["SemiWiki", "Design-Reuse", "Synopsys官网"]:
                    content = synopsys_crawler.fetch_news_content(news['link'])
                elif source_name == "Cadence官网":
                    content = cadence_crawler.fetch_news_content(news['link'])
                elif source_name == "Siemens官网":
                    content = siemens_crawler.fetch_news_content(news['link'])
                elif source_name == "EETimes":
                    content = eetimes_crawler.fetch_news_content(news['link'])
                elif source_name == "思尔芯官网":
                    content = s2c_crawler.fetch_news_content(news['link'])
                elif source_name == "鸿芯微纳官网":
                    content = gigada_crawler.fetch_news_content(news['link'])
                elif source_name == "芯和半导体官网":
                    content = xpeedic_crawler.fetch_news_content(news['link'])
                elif source_name == "新浪网":
                    content = sina_crawler.fetch_news_content(news['link'])
                elif source_name == "腾讯网":
                    content = qq_crawler.fetch_news_content(news['link'])
                elif source_name == "搜狐网":
                    content = sohu_crawler.fetch_news_content(news['link'])
                elif source_name == "Bing新闻":
                    content = bing_crawler.fetch_news_content(news['link'])
                elif source_name == "问财网":
                    content = iwencai_crawler.fetch_news_content(news['link'])
                elif source_name == "集微网":
                    content = laoyaoba_crawler.fetch_news_content(news['link'])
                elif source_name == "Design News":
                    content = designnews_crawler.fetch_news_content(news['link'])
                elif source_name == "DIGITIMES":
                    content = digitimes_crawler.fetch_news_content(news['link'])
                elif source_name == "东方财富网":
                    content = eastmoney_crawler.fetch_news_content(news['link'])
                else:
                    content = fetch_news_content(news['link'])
                content_len = len(content) if content else 0
                if link and content_len >= 200:
                    with cache_lock:
                        content_cache[link] = content
                return {**item, 'content': content, 'content_len': content_len}
            except Exception as e:
                return {**item, 'content': None, 'content_len': 0}
        
        # 仅保留“内容获取阶段确实依赖共享driver慢路径”的来源
        selenium_sources = ["电子工程网", "电子工程专辑", "电子工程世界"]
        
        # 分离普通来源和Selenium来源
        normal_items = [item for item in all_news_items if item['source'] not in selenium_sources]
        selenium_items = [item for item in all_news_items if item['source'] in selenium_sources]
        normal_grouped_items = []
        normal_link_groups = {}
        for item in normal_items:
            link = item.get('news', {}).get('link', '')
            if link:
                normal_link_groups.setdefault(link, []).append(item)
            else:
                normal_grouped_items.append([item])
        normal_grouped_items.extend(normal_link_groups.values())
        unique_normal_items = [group[0] for group in normal_grouped_items if group]
        
        # 显示内容获取统计
        total_items = len(all_news_items)
        print(f"  总计: {total_items} 条新闻")
        print(f"    · 普通来源: {len(normal_items)} 条（并行获取）")
        print(f"      - 普通来源去重后请求: {len(unique_normal_items)} 条")
        print(f"    · Selenium重来源: {len(selenium_items)} 条（限并发获取）")
        print(f"\n  【两者同时开始】")
        
        # 用于存储结果
        results = []
        selenium_results_content = []
        results_lock = threading.Lock()
        
        def run_selenium_content_fetch():
            """在单独线程中顺序获取Selenium来源的内容"""
            if not selenium_items:
                return
            
            from bs4 import BeautifulSoup
            import time as time_module
            import requests
            from selenium.webdriver.common.by import By
            from selenium.webdriver.support.ui import WebDriverWait
            req_session = requests.Session()
            req_headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            }
            req_session.headers.update(req_headers)
            
            # 复用共享driver或创建新driver
            driver_to_use = driver_holder['driver']
            created_new_driver = False
            
            if driver_to_use is None:
                # 没有共享driver，创建新的
                try:
                    from selenium import webdriver
                    from selenium.webdriver.chrome.options import Options
                    from selenium.webdriver.chrome.service import Service
                    
                    chrome_options = Options()
                    chrome_options.add_argument('--headless=new')
                    chrome_options.add_argument('--disable-gpu')
                    chrome_options.add_argument('--no-sandbox')
                    chrome_options.add_argument('--disable-dev-shm-usage')
                    chrome_options.add_argument('--disable-extensions')
                    chrome_options.add_argument('--disable-logging')
                    chrome_options.add_argument('--log-level=3')
                    chrome_options.add_argument('--ignore-certificate-errors')
                    chrome_options.add_argument('--ignore-ssl-errors')
                    chrome_options.add_argument('--allow-insecure-localhost')
                    chrome_options.add_argument('--disable-web-security')
                    chrome_options.add_argument('--disable-features=IsolateOrigins,site-per-process')
                    chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
                    chrome_options.add_experimental_option('excludeSwitches', ['enable-logging', 'enable-automation'])
                    driver_to_use = create_chrome_driver(chrome_options)
                    driver_to_use.set_page_load_timeout(30)
                    created_new_driver = True
                except Exception as e:
                    print(f"\n  [Selenium] 初始化失败: {e}")
                    for item in selenium_items:
                        selenium_results_content.append({**item, 'content': '', 'content_len': 0})
                    return
            
            driver_lock = threading.Lock()

            def fetch_with_requests(url, source_name):
                try:
                    resp = req_session.get(url, timeout=10, verify=False, proxies={'http': None, 'https': None})
                    if resp.status_code == 200:
                        resp.encoding = resp.apparent_encoding or 'utf-8'
                        req_soup = BeautifulSoup(resp.text, 'html.parser')
                        if source_name == "电子工程网":
                            req_selectors = ['td[id^="postmessage_"]', 'td.portal_content', '#article-content', '.t_f', '.message', '.content']
                        elif source_name == "电子工程专辑":
                            for tag in req_soup.select('.partner-content, .recommend, .hot-article, .related, aside, .sidebar, .ad, .share, .comment'):
                                tag.decompose()
                            req_selectors = ['.article-con', '.article-detail', '.article-detail-content', '.article-content', '.detail-content', '.news-content', '.article-body']
                        else:
                            req_selectors = ['.newscc', 'article .newscc', '.article-content', '.article-body', '.content', '#content', '.news-content', 'article']
                        for selector in req_selectors:
                            node = req_soup.select_one(selector)
                            if not node:
                                continue
                            for tag in node.find_all(['script', 'style', 'iframe', 'nav', 'header', 'footer', 'aside']):
                                tag.decompose()
                            content = node.get_text(separator='\n', strip=True)
                            if content and len(content) > 100:
                                return content
                except Exception:
                    pass
                return ''

            def fetch_with_driver(url, source_name):
                try:
                    try:
                        driver_to_use.delete_all_cookies()
                    except:
                        pass
                    
                    driver_to_use.get(url)
                    if source_name == "电子工程专辑":
                        try:
                            WebDriverWait(driver_to_use, 6).until(
                                lambda d: d.find_elements(By.CSS_SELECTOR, '.article-con, .article-detail, .article-detail-content, .article-content, .detail-content, .news-content, .article-body') or d.find_elements(By.CSS_SELECTOR, 'p')
                            )
                        except:
                            pass
                        time_module.sleep(0.4)
                    elif source_name == "电子工程网":
                        try:
                            WebDriverWait(driver_to_use, 5).until(
                                lambda d: d.find_elements(By.CSS_SELECTOR, 'td[id^="postmessage_"], td.portal_content, #article-content, .t_f, .message') or d.find_elements(By.CSS_SELECTOR, 'p')
                            )
                        except:
                            pass
                        time_module.sleep(0.3)
                    elif source_name == "电子工程世界":
                        try:
                            WebDriverWait(driver_to_use, 5).until(
                                lambda d: d.find_elements(By.CSS_SELECTOR, '.newscc, article .newscc, .article-content, .article-body, #content, .news-content, article') or d.find_elements(By.CSS_SELECTOR, 'p')
                            )
                        except:
                            pass
                        time_module.sleep(0.3)
                    else:
                        time_module.sleep(1.2)
                    soup = BeautifulSoup(driver_to_use.page_source, 'html.parser')
                    
                    if source_name == "电子工程网":
                        for td in soup.select('td'):
                            td_id = td.get('id', '')
                            if td_id.startswith('postmessage_'):
                                content = td.get_text(separator='\n', strip=True)
                                if content and len(content) > 50:
                                    return content
                        selectors = ['td.portal_content', '#article-content', '.t_f', '.message', '.content']
                    elif source_name == "电子工程专辑":
                        for tag in soup.select('.partner-content, .recommend, .hot-article, .related, aside, .sidebar, .ad, .share, .comment'):
                            tag.decompose()
                        selectors = ['.article-con', '.article-detail', '.article-detail-content', '.article-content', '.detail-content', '.news-content', '.article-body']
                        for selector in selectors:
                            content_div = soup.select_one(selector)
                            if content_div:
                                for tag in content_div.find_all(['script', 'style', 'iframe', 'nav', 'header', 'footer']):
                                    tag.decompose()
                                paragraphs = content_div.find_all('p')
                                if paragraphs:
                                    content_found = '\n'.join([p.get_text(strip=True) for p in paragraphs if len(p.get_text(strip=True)) > 20])
                                else:
                                    content_found = content_div.get_text(separator='\n', strip=True)
                                if content_found and len(content_found) > 100:
                                    return content_found
                        all_paragraphs = soup.find_all('p')
                        long_paragraphs = [p.get_text(strip=True) for p in all_paragraphs if len(p.get_text(strip=True)) > 50]
                        if long_paragraphs:
                            content_found = '\n'.join(long_paragraphs)
                            if len(content_found) > 200:
                                return content_found
                        return ''
                    else:  # 电子工程世界
                        selectors = ['.newscc', 'article .newscc', '.article-content', '.content']
                    
                    for selector in selectors:
                        content_div = soup.select_one(selector)
                        if content_div:
                            for tag in content_div.find_all(['script', 'style', 'iframe', 'nav', 'header', 'footer']):
                                tag.decompose()
                            content = content_div.get_text(separator='\n', strip=True)
                            if content and len(content) > 50:
                                return content
                    
                    body = soup.select_one('body')
                    if body:
                        for tag in body.find_all(['script', 'style', 'iframe', 'nav', 'header', 'footer', 'aside']):
                            tag.decompose()
                        content = body.get_text(separator='\n', strip=True)
                        if content and len(content) > 100:
                            return content[:5000]
                    return ''
                except Exception:
                    return ''

            def fetch_selenium_item(item):
                source_name = item['source']
                news = item['news']
                link = news.get('link', '')
                cached_content = news.get('content', '')
                if cached_content and len(cached_content) >= 200:
                    return {**item, 'content': cached_content, 'content_len': len(cached_content), 'cache_hit': True}
                if link:
                    with cache_lock:
                        cached_by_link = content_cache.get(link, '')
                    if cached_by_link and len(cached_by_link) >= 200:
                        return {**item, 'content': cached_by_link, 'content_len': len(cached_by_link), 'cache_hit': True}
                content = fetch_with_requests(link, source_name)
                if not content:
                    with driver_lock:
                        content = fetch_with_driver(link, source_name)
                content_len = len(content) if content else 0
                if link and content_len >= 200:
                    with cache_lock:
                        content_cache[link] = content
                return {**item, 'content': content, 'content_len': content_len, 'cache_hit': False}

            selenium_workers = 3 if len(selenium_items) >= 3 else len(selenium_items)
            print(f"  [Selenium] 启动限并发获取（{selenium_workers}线程）...")
            with ThreadPoolExecutor(max_workers=selenium_workers) as executor:
                futures = {executor.submit(fetch_selenium_item, item): item for item in selenium_items}
                completed = 0
                cache_hit_count = 0
                for future in as_completed(futures):
                    completed += 1
                    result = future.result()
                    source_name = result['source']
                    news = result['news']
                    title_short = news['title'][:30] + "..." if len(news['title']) > 30 else news['title']
                    content_len = result.get('content_len', 0)
                    if result.get('cache_hit'):
                        cache_hit_count += 1
                    selenium_results_content.append(result)
                    status = f"[+]{content_len}字" if content_len > 0 else "[-]无内容"
                    print(f"  [Selenium {completed}/{len(selenium_items)}] {source_name}: {status} | {title_short}")
            
            selenium_success = sum(1 for r in selenium_results_content if r.get('content_len', 0) > 0)
            print(f"  [Selenium] 完成: {selenium_success}条成功, {len(selenium_items)-selenium_success}条无内容, 缓存命中{cache_hit_count}条")
            
            if created_new_driver:
                driver_to_use.quit()
        
        # 启动Selenium内容获取线程
        selenium_content_thread = None
        if selenium_items:
            selenium_content_thread = threading.Thread(target=run_selenium_content_fetch, name="SeleniumContent")
            selenium_content_thread.start()
        
        # 并行获取普通来源
        total = len(normal_items)
        completed = 0
        success_count = 0
        fail_count = 0
        
        if unique_normal_items:
            normal_workers = 12 if len(unique_normal_items) >= 12 else len(unique_normal_items)
            print(f"  [普通] 正在并行获取（{normal_workers}线程）...")
            print(f"  [普通] 总任务数: {total}")
            with ThreadPoolExecutor(max_workers=normal_workers) as executor:
                futures = {
                    executor.submit(fetch_single_news, group[0]): group
                    for group in normal_grouped_items if group
                }
                for future in as_completed(futures):
                    group = futures[future]
                    src_item = group[0]
                    source_name = src_item.get('source', '-')
                    title = src_item.get('news', {}).get('title', '')
                    title_short = title[:28] + "..." if len(title) > 28 else title
                    result = future.result()
                    for idx, grouped_item in enumerate(group):
                        if idx == 0:
                            grouped_result = result
                        else:
                            grouped_result = {
                                **grouped_item,
                                'content': result.get('content', ''),
                                'content_len': result.get('content_len', 0)
                            }
                        results.append(grouped_result)
                        content_len = grouped_result.get('content_len', 0)
                        if content_len > 0:
                            success_count += 1
                            status = f"{_icon('✅', '[OK]')} 成功"
                        else:
                            fail_count += 1
                            status = f"{_icon('❌', '[ERR]')} 无内容"
                        completed += 1
                        progress = (completed / total * 100) if total else 100
                        print(f"  [普通 {completed}/{total} {progress:5.1f}%] {source_name} | {status} | {content_len}字 | {title_short}")
            print(f"  [普通] 完成: {success_count}条成功, {fail_count}条无内容")
        
        # 等待Selenium内容获取完成
        if selenium_content_thread:
            selenium_content_thread.join()
            results.extend(selenium_results_content)

        try:
            os.makedirs(os.path.dirname(content_cache_file), exist_ok=True)
            persisted_payload = {}
            for link, text in content_cache.items():
                if text and len(text) >= 200:
                    persisted_payload[link] = {
                        'content': text,
                        'updated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    }
            if len(persisted_payload) > 1500:
                trimmed_items = list(persisted_payload.items())[-1500:]
                persisted_payload = dict(trimmed_items)
            with open(content_cache_file, 'w', encoding='utf-8') as f:
                json.dump(persisted_payload, f, ensure_ascii=False)
            print(f"  内容缓存已更新: {len(persisted_payload)} 条")
        except Exception:
            pass
        
        # 关闭共享driver（如果存在）
        if driver_holder['driver']:
            try:
                driver_holder['driver'].quit()
                print("\n  共享driver已关闭")
            except:
                pass
        
        # 整理结果到 news_by_company
        # Selenium来源（内容获取可能不稳定，放宽字数限制）
        selenium_sources = ["腾讯网", "搜狐网", "电子工程网", "电子工程专辑", "电子工程世界"]
        
        for item in results:
            company_name = item['company']
            source_name = item['source']
            content_len = item['content_len']
            
            # Selenium来源放宽字数限制（50字），其他来源200字
            min_len = 200
            if content_len < min_len:
                continue
            
            if company_name not in news_by_company:
                news_by_company[company_name] = {}
            if source_name not in news_by_company[company_name]:
                news_by_company[company_name][source_name] = []
            
            news_by_company[company_name][source_name].append({
                'news': item['news'],
                'content': item['content'],
                'content_len': content_len
            })

        # 将“行业新闻”按标题归并到对应公司，无法归并的保留在“行业新闻”
        company_aliases = {
            "Synopsys": ["synopsys", "新思科技", "新思", "snps"],
            "Cadence": ["cadence", "铿腾电子", "楷登", "cdns"],
            "Siemens": ["siemens", "西门子", "mentor"],
            "华大九天": ["华大九天", "empyrean"],
            "概伦电子": ["概伦电子", "primarius"],
            "广立微": ["广立微", "semitronix"],
            "合见工软": ["合见工软", "univista"],
            "芯华章": ["芯华章", "x-epic", "xepic"],
            "思尔芯": ["思尔芯", "s2c"],
            "鸿芯微纳": ["鸿芯微纳", "gigada"],
            "芯和半导体": ["芯和半导体", "xpeedic"],
        }

        def match_company_by_title(title_text):
            text = (title_text or '').lower()
            best_company = ''
            best_len = 0
            for company, aliases in company_aliases.items():
                for alias in aliases:
                    if alias and alias.lower() in text:
                        if len(alias) > best_len:
                            best_len = len(alias)
                            best_company = company
            return best_company

        industry_sources = news_by_company.get("行业新闻", {})
        if industry_sources:
            moved_items = {}
            remained_sources = {}
            moved_count = 0
            for source_name, news_items in industry_sources.items():
                remained_items = []
                for item in news_items:
                    title = item.get('news', {}).get('title', '')
                    matched_company = match_company_by_title(title)
                    if matched_company:
                        if matched_company not in moved_items:
                            moved_items[matched_company] = {}
                        if source_name not in moved_items[matched_company]:
                            moved_items[matched_company][source_name] = []
                        moved_items[matched_company][source_name].append(item)
                        moved_count += 1
                    else:
                        remained_items.append(item)
                if remained_items:
                    remained_sources[source_name] = remained_items

            for company_name, sources in moved_items.items():
                if company_name not in news_by_company:
                    news_by_company[company_name] = {}
                for source_name, news_items in sources.items():
                    if source_name not in news_by_company[company_name]:
                        news_by_company[company_name][source_name] = []
                    news_by_company[company_name][source_name].extend(news_items)

            if remained_sources:
                news_by_company["行业新闻"] = remained_sources
            else:
                news_by_company.pop("行业新闻", None)

            print(f"  行业新闻标题归并完成: 归并 {moved_count} 条，未归并 {sum(len(v) for v in remained_sources.values()) if remained_sources else 0} 条")
        
        # 清除检查进度提示
        print(" " * 60, end="\r")
        
        # 按日期排序（最新的优先）- 每个来源内部排序
        for company_name in news_by_company:
            for source_name in news_by_company[company_name]:
                news_by_company[company_name][source_name].sort(
                    key=lambda x: x['news'].get('date', ''), reverse=True
                )
        
        # 获取每个公司的最新日期，用于公司排序
        def get_company_latest_date(company_sources):
            latest = ''
            for news_items in company_sources.values():
                for item in news_items:
                    date = item['news'].get('date', '')
                    if date > latest:
                        latest = date
            return latest
        
        # 按公司最新日期排序
        sorted_companies = sorted(
            news_by_company.items(),
            key=lambda x: get_company_latest_date(x[1]),
            reverse=True
        )
        
        # 树状结构显示
        print("\n" + _color("="*60, "94"))
        print(_color(f"{_icon('📰', '[LIST]')} 可选新闻列表（树状结构）- 按日期排序，最新优先", "96"))
        print(_color("="*60, "94"))
        
        for company_name, sources in sorted_companies:
            # 统计该公司的新闻总数
            total_count = sum(len(items) for items in sources.values())
            if total_count == 0:
                continue
            
            print(_color(f"\n{_icon('📁', '[DIR]')} {company_name} ({total_count}条)", "95"))
            
            # 来源按最新日期排序
            def get_source_latest_date(news_items):
                if not news_items:
                    return ''
                return max(item['news'].get('date', '') for item in news_items)
            
            source_list = sorted(
                sources.items(),
                key=lambda x: get_source_latest_date(x[1]),
                reverse=True
            )
            for source_idx, (source_name, news_items) in enumerate(source_list):
                if not news_items:
                    continue
                
                # 判断是否是最后一个来源
                is_last_source = (source_idx == len(source_list) - 1)
                source_prefix = "└─" if is_last_source else "├─"
                
                print(_color(f"  {source_prefix} {_icon('🗞️', '[NEWS]')} {source_name} ({len(news_items)}条)", "94"))
                
                for news_idx, item in enumerate(news_items):
                    news = item['news']
                    content_len = item['content_len']
                    is_complete = "[OK]完整" if content_len > 200 else "[!]较少"
                    
                    # 判断是否是最后一条新闻
                    is_last_news = (news_idx == len(news_items) - 1)
                    
                    if is_last_source:
                        news_prefix = "     └─"
                        detail_prefix = "        "
                        link_prefix = "        "
                    else:
                        news_prefix = "  │  └─"
                        detail_prefix = "  │     "
                        link_prefix = "  │     "
                    
                    print(_color(f"{news_prefix} {_icon('🔢', '[#]')} [{global_index}] {news['title']}", "97"))
                    status_color = "92" if content_len > 200 else "93"
                    status_icon = _icon("✅", "[OK]") if content_len > 200 else _icon("⚠️", "[!]")
                    print(_color(f"{detail_prefix}状态: {status_icon}{is_complete} ({content_len}字) | 日期: {news.get('date', '-')}", status_color))
                    print(_color(f"{link_prefix}{_icon('🔗', '[LINK]')} {news['link']}", "90"))
                    
                    all_news.append({
                        'news': news,
                        'content': item['content'],
                        'content_len': content_len,
                        'source': source_name,
                        'company': company_name
                    })
                    global_index += 1
        
        print(_color("-" * 60, "90"))
        print(_color(f"{_icon('📊', '[SUM]')} 共 {len(all_news)} 条新闻（已过滤掉字数<100的新闻）", "96"))
        
    if not sys.stdin or not sys.stdin.isatty():
        print("\n检测到非交互环境，跳过手动选择。")
        return

    while True:
        print("\n请输入新闻序号或直接粘贴链接（直接回车选择第1条，输入 q 退出）：")
        user_input = input().strip()
        
        # 退出条件
        if user_input.lower() in ['q', 'quit', 'exit', '0']:
            print("\n“再见！")
            break
        
        selected_item = None
        
        if not user_input:
            # 默认选择第一条
            if all_news:
                selected_item = all_news[0]
        elif user_input.isdigit():
            # 用户输入了序号
            idx = int(user_input) - 1
            if 0 <= idx < len(all_news):
                selected_item = all_news[idx]
            else:
                print("[ERR] 无效的序号，请重新输入")
                continue
        elif user_input.startswith("http"):
            # 用户输入了链接
            selected_item = {
                'news': {"title": "用户输入的新闻", "link": user_input},
                'content': None,
                'content_len': 0,
                'source': '',
                'company': ''
            }
        else:
            print("[ERR] 无效的输入，请输入序号、链接或 q 退出")
            continue
            
        if selected_item:
            selected_news = selected_item['news']
            cached_content = selected_item.get('content')
            source_name = selected_item.get('source', '')
            company_name = selected_item.get('company', '')
            
            print(f"\n选取新闻: {selected_news.get('title', '-')}")
            print(f"来源: {source_name}")
            print(f"链接: {selected_news['link']}")
            
            # 使用缓存的内容，如果没有则重新获取
            if cached_content:
                content = cached_content
            else:
                content = fetch_news_content(selected_news['link'])
            
            if not content:
                content = selected_news.get('title', '')
        
            content_len = len(content) if content else 0
            is_complete = content_len > 200
        
            is_official = "官网" in source_name
        
            # 所有新闻都添加提示词
            # 官网新闻：添加去主观化要求
            # 非官网新闻：添加扩充/缩减到800字的要求
            prompt = copy_to_clipboard(content, selected_news.get('title', '新闻'), source_name)
            print("\n" + "="*60)
            print("[OK] 提示词已复制到剪贴板！")
            if is_official:
                print(f"   （{content_len}字，来自 [{source_name}]，已添加去除主观描述的提示词）")
            else:
                print(f"   （{content_len}字，来自 [{source_name}]，已添加扩充/缩减到800字的提示词）")
            print("="*60)
        
            # 保存提示词到 result 目录
            result_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'result')
            os.makedirs(result_dir, exist_ok=True)
            prompt_file = os.path.join(result_dir, 'selected_news_prompt.txt')
            with open(prompt_file, 'w', encoding='utf-8') as f:
                f.write(prompt)
            print(f"[FILE] 提示词已保存到: {prompt_file}")
        else:
            print("\n[!] 没有找到可用的新闻来生成新闻稿")
if __name__ == "__main__":
    main()
