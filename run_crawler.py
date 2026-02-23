# -*- coding: utf-8 -*-
"""
统一新闻爬取入口脚本
支持调用多个爬虫脚本：
- 同花顺个股新闻 (stock_news_crawler)
- 广立微官网新闻 (semitronix_news_crawler)
- 未来可继续添加其他爬虫...
"""

from crawlers import THSNewsCrawler, SemitronixNewsCrawler, PrimariusNewsCrawler, UnivistiaNewsCrawler, XepicNewsCrawler, SeccwNewsCrawler, DramxNewsCrawler
from classify_news import NewsClassifier
from auto_news_writer import get_first_news_link, fetch_news_content, copy_to_clipboard
import pyperclip
import json
import os
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
}

# ========================================
# 爬虫配置（在这里添加新的爬虫配置）
# ========================================

# 同花顺个股新闻配置
THS_CONFIG = {
    'enabled': True,  # 是否启用
    'stocks': [
        "301269",  # 华大九天
        "688206",  # 概伦电子
        "301095"   # 广立微
    ],
    'days': 7,  # 最近几天
}

# 广立微官网新闻配置
SEMITRONIX_CONFIG = {
    'enabled': True,  # 是否启用
    'max_pages': 1,  # 最大爬取页数
    'months': 1,      # 只保留最近几个月的新闻
}

# 概伦电子官网新闻配置
PRIMARIUS_CONFIG = {
    'enabled': True,  # 是否启用
    'max_pages': 1,   # 最大爬取页数（只有1页）
    'months': 1,      # 只保留最近几个月的新闻
}

# 合见工软官网新闻配置
UNIVISTA_CONFIG = {
    'enabled': True,  # 是否启用
    'max_pages': 1,   # 最大爬取页数
    'months': 1,      # 只保留最近几个月的新闻
}

# 芯华章官网新闻配置
XEPIC_CONFIG = {
    'enabled': True,  # 是否启用
    'max_pages': 1,   # 最大爬取页数
    'months': 1,      # 只保留最近几个月的新闻
}

# 深圳电子商会新闻配置
SECCW_CONFIG = {
    'enabled': True,  # 是否启用
    'max_pages': 1,   # 最大爬取页数
    'months': 1,      # 只保留最近几个月的新闻
    'keyword': 'EDA', # 搜索关键词
}

# 全球半导体观察新闻配置
DRAMX_CONFIG = {
    'enabled': True,  # 是否启用
    'max_pages': 1,   # 最大爬取页数
    'months': 1,      # 只保留最近几个月的新闻
}

# 未来可以继续添加其他爬虫配置...
# OTHER_CRAWLER_CONFIG = {
#     'enabled': False,
#     ...
# }

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
            
            print(f"✅ 股票 {code} 爬取完成，获取 {len(news_list)} 条新闻")
            
        except Exception as e:
            print(f"❌ 股票 {code} 爬取失败: {e}")
    
    # 将汇总结果保存
    output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'output')
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
    
    print("\n" + "="*50)
    print("同花顺个股新闻爬虫")
    print("="*50)
    
    stock_list = config.get('stocks', [])
    days = config.get('days', 7)
    
    end_date = datetime.now().strftime("%Y-%m-%d")
    start_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
    
    print(f"开始批量爬取任务，共 {len(stock_list)} 只股票...")
    print(f"爬取模式: 日期范围 {start_date} 至 {end_date}")
    
    all_results = {}
    
    for code in stock_list:
        try:
            crawler = THSNewsCrawler(code)
            news_list = crawler.crawl(start_date=start_date, end_date=end_date)
            
            all_results[code] = {
                "source": "同花顺",
                "count": len(news_list),
                "news": news_list
            }
            print(f"✅ 股票 {code} 爬取完成，获取 {len(news_list)} 条新闻")
        except Exception as e:
            print(f"❌ 股票 {code} 爬取失败: {e}")
    
    return all_results


def run_semitronix_crawler(config):
    """运行广立微官网新闻爬虫"""
    if not config.get('enabled', False):
        return {}
    
    print("\n" + "="*50)
    print("广立微官网新闻爬虫")
    print("="*50)
    
    max_pages = config.get('max_pages', 10)
    months = config.get('months', 3)
    
    try:
        crawler = SemitronixNewsCrawler()
        news_list = crawler.crawl(max_pages=max_pages, months=months)
        
        # 返回统一格式
        result = {
            "semitronix": {
                "source": "广立微官网",
                "count": len(news_list),
                "news": news_list
            }
        }
        print(f"✅ 广立微官网爬取完成，获取 {len(news_list)} 条新闻（最近{months}个月）")
        return result
    except Exception as e:
        print(f"❌ 广立微官网爬取失败: {e}")
        return {}


def run_primarius_crawler(config):
    """运行概伦电子官网新闻爬虫"""
    if not config.get('enabled', False):
        return {}
    
    print("\n" + "="*50)
    print("概伦电子官网新闻爬虫")
    print("="*50)
    
    max_pages = config.get('max_pages', 10)
    months = config.get('months', 3)
    
    try:
        crawler = PrimariusNewsCrawler()
        news_list = crawler.crawl(max_pages=max_pages, months=months)
        
        # 返回统一格式
        result = {
            "primarius": {
                "source": "概伦电子官网",
                "count": len(news_list),
                "news": news_list
            }
        }
        print(f"✅ 概伦电子官网爬取完成，获取 {len(news_list)} 条新闻（最近{months}个月）")
        return result
    except Exception as e:
        print(f"❌ 概伦电子官网爬取失败: {e}")
        return {}


def run_univista_crawler(config):
    """运行合见工软官网新闻爬虫"""
    if not config.get('enabled', False):
        return {}
    
    print("\n" + "="*50)
    print("合见工软官网新闻爬虫")
    print("="*50)
    
    max_pages = config.get('max_pages', 5)
    months = config.get('months', 3)
    
    try:
        crawler = UnivistiaNewsCrawler()
        news_list = crawler.crawl(max_pages=max_pages, months=months)
        
        # 返回统一格式
        result = {
            "univista": {
                "source": "合见工软官网",
                "count": len(news_list),
                "news": news_list
            }
        }
        print(f"✅ 合见工软官网爬取完成，获取 {len(news_list)} 条新闻（最近{months}个月）")
        return result
    except Exception as e:
        print(f"❌ 合见工软官网爬取失败: {e}")
        return {}


def run_xepic_crawler(config):
    """运行芯华章官网新闻爬虫"""
    if not config.get('enabled', False):
        return {}
    
    print("\n" + "="*50)
    print("芯华章官网新闻爬虫")
    print("="*50)
    
    max_pages = config.get('max_pages', 5)
    months = config.get('months', 3)
    
    try:
        crawler = XepicNewsCrawler()
        news_list = crawler.crawl(max_pages=max_pages, months=months)
        
        # 返回统一格式
        result = {
            "xepic": {
                "source": "芯华章官网",
                "count": len(news_list),
                "news": news_list
            }
        }
        print(f"✅ 芯华章官网爬取完成，获取 {len(news_list)} 条新闻（最近{months}个月）")
        return result
    except Exception as e:
        print(f"❌ 芯华章官网爬取失败: {e}")
        return {}


def run_seccw_crawler(config):
    """运行深圳电子商会新闻爬虫"""
    if not config.get('enabled', False):
        return {}
    
    print("\n" + "="*50)
    print("深圳电子商会新闻爬虫 (EDA关键词)")
    print("="*50)
    
    max_pages = config.get('max_pages', 5)
    months = config.get('months', 3)
    keyword = config.get('keyword', 'EDA')
    
    try:
        crawler = SeccwNewsCrawler(keyword=keyword)
        news_list = crawler.crawl(max_pages=max_pages, months=months)
        
        # 返回统一格式
        result = {
            "seccw": {
                "source": "深圳电子商会",
                "count": len(news_list),
                "news": news_list
            }
        }
        print(f"✅ 深圳电子商会爬取完成，获取 {len(news_list)} 条新闻（最近{months}个月）")
        return result
    except Exception as e:
        print(f"❌ 深圳电子商会爬取失败: {e}")
        return {}


def run_dramx_crawler(config):
    """运行全球半导体观察新闻爬虫"""
    if not config.get('enabled', False):
        return {}
    
    print("\n" + "="*50)
    print("全球半导体观察新闻爬虫 (EDA)")
    print("="*50)
    
    max_pages = config.get('max_pages', 1)
    months = config.get('months', 1)
    
    try:
        crawler = DramxNewsCrawler()
        news_list = crawler.crawl(max_pages=max_pages, months=months)
        
        # 返回统一格式
        result = {
            "dramx": {
                "source": "全球半导体观察",
                "count": len(news_list),
                "news": news_list
            }
        }
        print(f"✅ 全球半导体观察爬取完成，获取 {len(news_list)} 条新闻（最近{months}个月）")
        return result
    except Exception as e:
        print(f"❌ 全球半导体观察爬取失败: {e}")
        return {}


def convert_to_new_format(raw_results):
    """
    将爬取结果转换为新格式：
    公司名称 -> 新闻来源 -> 新闻列表
    """
    formatted = {}
    
    for key, data in raw_results.items():
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
                'date': news.get('date', '')
            })
    
    return formatted


def main():
    print("\n" + "#"*60)
    print("#" + " "*20 + "统一新闻爬取系统" + " "*19 + "#")
    print("#"*60)
    
    all_results = {}
    
    # ======== 1. 运行同花顺爬虫 ========
    ths_results = run_ths_crawler(THS_CONFIG)
    all_results.update(ths_results)
    
    # ======== 2. 运行广立微官网爬虫 ========
    semitronix_results = run_semitronix_crawler(SEMITRONIX_CONFIG)
    all_results.update(semitronix_results)
    
    # ======== 3. 运行概伦电子官网爬虫 ========
    primarius_results = run_primarius_crawler(PRIMARIUS_CONFIG)
    all_results.update(primarius_results)
    
    # ======== 4. 运行合见工软官网爬虫 ========
    univista_results = run_univista_crawler(UNIVISTA_CONFIG)
    all_results.update(univista_results)
    
    # ======== 5. 运行芯华章官网爬虫 ========
    xepic_results = run_xepic_crawler(XEPIC_CONFIG)
    all_results.update(xepic_results)
    
    # ======== 6. 运行深圳电子商会爬虫 ========
    seccw_results = run_seccw_crawler(SECCW_CONFIG)
    all_results.update(seccw_results)
    
    # ======== 7. 运行全球半导体观察爬虫 ========
    dramx_results = run_dramx_crawler(DRAMX_CONFIG)
    all_results.update(dramx_results)
    
    # ======== 8. 未来可以继续添加其他爬虫 ========
    # other_results = run_other_crawler(OTHER_CONFIG)
    # all_results.update(other_results)
    
    # ======== 保存汇总结果 ========
    if all_results:
        # 转换为新格式：公司名称 -> 来源 -> 新闻列表
        formatted_results = convert_to_new_format(all_results)
        
        output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'output')
        os.makedirs(output_dir, exist_ok=True)
        output_file = os.path.join(output_dir, "batch_news_results.json")
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(formatted_results, f, ensure_ascii=False, indent=2)
        
        print("\n" + "="*50)
        print(f"所有爬虫任务完成！汇总数据已保存至: {output_file}")
        print("="*50)
        
        # 统计汇总
        total_news = sum(data.get('count', 0) for data in all_results.values())
        print(f"\n汇总统计: 共爬取 {total_news} 条新闻")
        for company, sources in formatted_results.items():
            company_total = sum(len(news_list) for news_list in sources.values())
            print(f"  - {company}: {company_total} 条")
            for source, news_list in sources.items():
                print(f"      · {source}: {len(news_list)} 条")
    
    # ======== 自动执行分类 ========
    if all_results:
        # 使用转换后的格式进行分类
        formatted_results = convert_to_new_format(all_results)
        
        print("\n" + "="*50)
        print("开始自动分类新闻...")
        print("="*50)
        
        # 创建分类器
        classifier = NewsClassifier()
        target_categories = ["战略合作", "技术研发", "行业分析"]
        skip_sources = []  # 不跳过任何来源
        category_only_sources = ["广立微官网", "概伦电子官网", "合见工软官网", "芯华章官网", "深圳电子商会", "全球半导体观察"]  # 公司官网和行业新闻只做分类筛选，不限公司相关
        
        print(f"过滤规则: 同花顺新闻筛选 {', '.join(target_categories)} 三类 + 公司直接相关")
        print(f"         公司官网新闻筛选 {', '.join(target_categories)} 三类（不限公司相关）\n")
        
        # 执行分类（两层筛选）- 使用转换后的格式
        classified_results = classifier.classify_batch(
            formatted_results, 
            filter_categories=target_categories,
            only_company_related=True,
            skip_filter_sources=skip_sources,
            category_only_sources=category_only_sources
        )
        
        # 保存分类结果
        classifier.save_classified_results(classified_results)
        
        # 打印统计摘要
        if classified_results:
            classifier.print_summary(classified_results)
            
            # 打印详细分类结果示例
            print("\n" + "="*60)
            print("详细分类示例 (仅显示前3条)")
            print("="*60)
            
            for company_name, sources in classified_results.items():
                print(f"\n【{company_name}】")
                for source_name, news_list in sources.items():
                    if news_list:
                        print(f"\n  [{source_name}] ({len(news_list)}条)")
                        for i, news in enumerate(news_list[:3], 1):
                            print(f"    {i}. {news['title']}")
                            print(f"       链接: {news['link']}")
                        if len(news_list) > 3:
                            print(f"    ... 还有 {len(news_list) - 3} 条")
        else:
            print("\n⚠️  警告: 所有股票的新闻都被过滤掉了，没有符合条件的新闻")
        
    # ======== 自动运行 Writer 脚本 ========
    print("\n" + "="*50)
    print("请从上方列表中选择一条新闻生成新闻稿")
    print("="*50)
        
    # 显示所有新闻链接供用户选择（树状结构）
    all_news = []
    global_index = 1
        
    if classified_results:
        print("\n正在检查新闻内容...")
        print("-" * 60)
        
        # 先收集所有新闻及其内容
        temp_index = 1
        news_by_company = {}  # {公司名: {来源: [(news, content, content_len)]}}
        
        # 创建芯华章爬虫实例用于获取内容
        xepic_crawler = XepicNewsCrawler()
        # 创建深圳电子商会爬虫实例用于获取内容
        seccw_crawler = SeccwNewsCrawler()
        # 创建全球半导体观察爬虫实例用于获取内容
        dramx_crawler = DramxNewsCrawler()
        
        for company_name, sources in classified_results.items():
            news_by_company[company_name] = {}
            for source_name, news_list in sources.items():
                news_by_company[company_name][source_name] = []
                for news in news_list:
                    # 获取新闻内容并判断字数
                    print(f"  正在检查第 {temp_index} 条新闻...", end="\r")
                    
                    # 芯华章官网使用专用爬虫获取内容
                    if source_name == "芯华章官网":
                        content = xepic_crawler.fetch_news_content(news['link'])
                    elif source_name == "深圳电子商会":
                        content = seccw_crawler.fetch_news_content(news['link'])
                    elif source_name == "全球半导体观察":
                        content = dramx_crawler.fetch_news_content(news['link'])
                    else:
                        content = fetch_news_content(news['link'])
                    
                    content_len = len(content) if content else 0
                    temp_index += 1
                    
                    # 过滤掉字数少于100的新闻
                    if content_len < 100:
                        continue
                    
                    news_by_company[company_name][source_name].append({
                        'news': news,
                        'content': content,
                        'content_len': content_len
                    })
        
        # 清除检查进度提示
        print(" " * 60, end="\r")
        
        # 树状结构显示
        print("\n" + "="*60)
        print("可选新闻列表（树状结构）")
        print("="*60)
        
        for company_name, sources in news_by_company.items():
            # 统计该公司的新闻总数
            total_count = sum(len(items) for items in sources.values())
            if total_count == 0:
                continue
            
            print(f"\n📁 {company_name} ({total_count}条)")
            
            source_list = list(sources.items())
            for source_idx, (source_name, news_items) in enumerate(source_list):
                if not news_items:
                    continue
                
                # 判断是否是最后一个来源
                is_last_source = (source_idx == len(source_list) - 1)
                source_prefix = "└─" if is_last_source else "├─"
                
                print(f"  {source_prefix} 📰 {source_name} ({len(news_items)}条)")
                
                for news_idx, item in enumerate(news_items):
                    news = item['news']
                    content_len = item['content_len']
                    is_complete = "✅完整" if content_len > 200 else "⚠️较少"
                    
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
                    
                    print(f"{news_prefix} [{global_index}] {news['title'][:50]}{'...' if len(news['title']) > 50 else ''}")
                    print(f"{detail_prefix}状态: {is_complete} ({content_len}字) | 日期: {news.get('date', '-')}")
                    print(f"{link_prefix}链接: {news['link']}")
                    
                    all_news.append({
                        'news': news,
                        'content': item['content'],
                        'content_len': content_len,
                        'source': source_name,
                        'company': company_name
                    })
                    global_index += 1
        
        print("-" * 60)
        print(f"共 {len(all_news)} 条新闻（已过滤掉字数<100的新闻）")
        
    # 等待用户输入
    print("\n请输入新闻序号或直接粘贴链接（直接回车选择第1条）：")
    user_input = input().strip()
        
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
            print("无效的序号")
            return
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
        print("无效的输入")
        return
            
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
        print("✅ 提示词已复制到剪贴板！")
        if is_official:
            print(f"   （{content_len}字，来自 [{source_name}]，已添加去除主观描述的提示词）")
        else:
            print(f"   （{content_len}字，来自 [{source_name}]，已添加扩充/缩减到800字的提示词）")
        print("="*60)
    else:
        print("\n⚠️  没有找到可用的新闻来生成新闻稿")
if __name__ == "__main__":
    main()
