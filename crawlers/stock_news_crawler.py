# -*- coding: utf-8 -*-
"""
同花顺股票新闻爬虫
爬取指定股票代码的新闻链接
"""

import requests
from bs4 import BeautifulSoup
import re
import json
from datetime import datetime


class THSNewsCrawler:
    """同花顺新闻爬虫类"""
    
    def __init__(self, stock_code):
        """
        初始化爬虫
        :param stock_code: 股票代码，如 301269
        """
        self.stock_code = stock_code
        self.base_url = f"https://stockpage.10jqka.com.cn/{stock_code}/news/"
        self.ajax_url = f"https://stockpage.10jqka.com.cn/ajax/code/{stock_code}/type/news/"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Referer': f'https://stockpage.10jqka.com.cn/{stock_code}/',
        }
    
    def _normalize_date(self, date_str):
        """
        统一日期格式为 YYYY-MM-DD
        :param date_str: 原始日期字符串，可能是 'MM/DD' 或 'YYYY-MM-DD' 格式
        :return: 统一格式后的日期字符串
        """
        if not date_str:
            return ''
        
        date_str = date_str.strip('[]')
        current_year = datetime.now().year
        
        try:
            # 如果是 MM/DD 格式
            if '/' in date_str and len(date_str) == 5:
                month, day = date_str.split('/')
                return f"{current_year}-{month}-{day}"
            # 如果已经是 YYYY-MM-DD 格式
            elif '-' in date_str and len(date_str) == 10:
                return date_str
            else:
                return date_str
        except:
            return date_str
    
    def fetch_news_from_page(self):
        """
        从HTML页面直接爬取新闻链接
        :return: 新闻列表，每项包含标题、链接、日期
        """
        news_list = []
        
        try:
            response = requests.get(self.base_url, headers=self.headers, timeout=15)
            response.encoding = 'gbk'  # 同花顺使用GBK编码
            
            if response.status_code != 200:
                print(f"请求失败，状态码: {response.status_code}")
                return news_list
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 方法1: 从热点新闻区域获取 (dl > dt > a)
            dt_tags = soup.find_all('dt')
            for dt in dt_tags:
                link_tag = dt.find('a', class_='client')
                if link_tag and link_tag.get('href'):
                    title = link_tag.get_text(strip=True)
                    href = link_tag.get('href')
                    
                    # 获取日期并统一格式
                    date_span = dt.find('span', class_='date')
                    date = ''
                    if date_span:
                        date = self._normalize_date(date_span.get_text(strip=True))
                    
                    if title and href:
                        news_list.append({
                            'title': title,
                            'link': href,
                            'date': date
                        })
            
            # 方法2: 从其他新闻列表获取 (ul.sub_list > li > a)
            sub_lists = soup.find_all('ul', class_='sub_list')
            for ul in sub_lists:
                li_tags = ul.find_all('li')
                for li in li_tags:
                    link_tag = li.find('a')
                    if link_tag and link_tag.get('href'):
                        title = link_tag.get_text(strip=True)
                        href = link_tag.get('href')
                        
                        # 提取日期并统一格式 (公告格式: a > span; 研报格式: span.date)
                        date = ""
                        date_span = li.find('span', class_='date') # 研报格式
                        if not date_span:
                            date_span = link_tag.find('span') # 公告格式 (在 a 标签内部)
                        
                        if date_span:
                            date = self._normalize_date(date_span.get_text(strip=True))
                            # 如果标题里包含了日期文本，清理一下标题
                            raw_date = date_span.get_text(strip=True).strip('[]')
                            if raw_date in title:
                                title = title.replace(raw_date, "").strip()
                        
                        if title and href:
                            news_list.append({
                                'title': title,
                                'link': href,
                                'date': date
                            })
            
            # 去重
            seen = set()
            unique_news = []
            for news in news_list:
                if news['link'] not in seen:
                    seen.add(news['link'])
                    unique_news.append(news)
            
            return unique_news
            
        except Exception as e:
            print(f"爬取页面时出错: {e}")
            return news_list
    
    def fetch_news_from_ajax(self):
        """
        通过AJAX接口获取新闻数据
        :return: 新闻列表
        """
        news_list = []
        
        try:
            response = requests.get(self.ajax_url, headers=self.headers, timeout=15)
            response.encoding = 'gbk'
            
            if response.status_code != 200:
                print(f"AJAX请求失败，状态码: {response.status_code}")
                return news_list
            
            # AJAX返回的是HTML片段
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 1. 尝试从 dt 结构获取 (热点新闻/研报)
            dt_tags = soup.find_all('dt')
            for dt in dt_tags:
                link_tag = dt.find('a')
                if link_tag and link_tag.get('href'):
                    title = link_tag.get_text(strip=True)
                    href = link_tag.get('href')
                    date_span = dt.find('span', class_='date')
                    date = self._normalize_date(date_span.get_text(strip=True)) if date_span else ''
                    
                    if title and href:
                        news_list.append({'title': title, 'link': href, 'date': date})

            # 2. 尝试从 li 结构获取 (公告/列表新闻)
            li_tags = soup.find_all('li')
            for li in li_tags:
                link_tag = li.find('a')
                if link_tag and link_tag.get('href'):
                    href = link_tag.get('href')
                    
                    # 查找日期并统一格式
                    date = ""
                    date_span = li.find('span', class_='date')
                    if not date_span:
                        date_span = link_tag.find('span')
                    
                    if date_span:
                        date = self._normalize_date(date_span.get_text(strip=True))
                    
                    # 清理标题：去掉日期 span 的文本
                    title = link_tag.get_text(strip=True)
                    raw_date = date_span.get_text(strip=True).strip('[]') if date_span else ''
                    if raw_date and raw_date in title:
                        title = title.replace(raw_date, "").strip()

                    if title and href:
                        news_list.append({'title': title, 'link': href, 'date': date})
            
            # 去重
            seen = set()
            unique_news = []
            for news in news_list:
                if news['link'] not in seen:
                    seen.add(news['link'])
                    unique_news.append(news)
            
            return unique_news
            
        except Exception as e:
            print(f"AJAX请求时出错: {e}")
            return news_list
    
    def crawl(self, only_today=False, start_date=None, end_date=None):
        """
        执行爬取，优先使用AJAX接口，失败则使用页面爬取
        :param only_today: 是否只返回当天的新闻（优先级高于日期范围）
        :param start_date: 开始日期，格式为 datetime 对象或 'YYYY-MM-DD' 字符串
        :param end_date: 结束日期，格式为 datetime 对象或 'YYYY-MM-DD' 字符串
        :return: 新闻列表
        """
        print(f"正在爬取股票 {self.stock_code} 的新闻...")
        
        # 先尝试AJAX接口
        news = self.fetch_news_from_ajax()
        
        if not news:
            print("AJAX接口无数据，尝试从页面爬取...")
            news = self.fetch_news_from_page()
        
        # 日期过滤
        if only_today:
            # 只保留当天的新闻
            today = datetime.now()
            today_str1 = today.strftime("%Y-%m-%d") # 2026-02-03
            today_str2 = today.strftime("%m/%d")    # 02/03
            
            filtered_news = []
            for item in news:
                if item['date'] == today_str1 or item['date'] == today_str2:
                    filtered_news.append(item)
            
            print(f"共获取 {len(news)} 条新闻，过滤后剩余 {len(filtered_news)} 条当天新闻")
            return filtered_news
        
        elif start_date or end_date:
            # 日期范围过滤
            filtered_news = self._filter_by_date_range(news, start_date, end_date)
            print(f"共获取 {len(news)} 条新闻，过滤后剩余 {len(filtered_news)} 条符合日期范围的新闻")
            return filtered_news
            
        print(f"共获取 {len(news)} 条新闻")
        return news
    
    def _filter_by_date_range(self, news_list, start_date, end_date):
        """
        根据日期范围过滤新闻
        :param news_list: 新闻列表
        :param start_date: 开始日期
        :param end_date: 结束日期
        :return: 过滤后的新闻列表
        """
        # 转换日期格式
        if isinstance(start_date, str):
            start_date = datetime.strptime(start_date, "%Y-%m-%d")
        if isinstance(end_date, str):
            end_date = datetime.strptime(end_date, "%Y-%m-%d")
        
        filtered_news = []
        current_year = datetime.now().year
        
        for item in news_list:
            date_str = item.get('date', '')
            if not date_str:
                continue
            
            try:
                # 解析日期
                news_date = None
                if '-' in date_str and len(date_str) == 10:  # YYYY-MM-DD
                    news_date = datetime.strptime(date_str, "%Y-%m-%d")
                elif '/' in date_str and len(date_str) == 5:  # MM/DD
                    news_date = datetime.strptime(f"{current_year}/{date_str}", "%Y/%m/%d")
                
                if news_date:
                    # 检查是否在日期范围内
                    if start_date and news_date < start_date:
                        continue
                    if end_date and news_date > end_date:
                        continue
                    filtered_news.append(item)
            except:
                # 日期解析失败，跳过
                continue
        
        return filtered_news
    
    def save_to_json(self, news_list, filename=None):
        """保存新闻到 JSON 文件（三级嵌套格式）"""
        import os
        
        if filename is None:
            filename = f'ths_{self.stock_code}_news.json'
        
        # 输出到 json 目录
        output_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'json')
        os.makedirs(output_dir, exist_ok=True)
        filepath = os.path.join(output_dir, filename)
        
        # 股票代码对应的公司名称
        stock_names = {
            "301269": "华大九天",
            "688206": "概伦电子",
            "301095": "广立微",
        }
        company_name = stock_names.get(self.stock_code, self.stock_code)
        
        # 三级嵌套格式
        data = {
            company_name: {
                "同花顺": [
                    {
                        'title': news.get('title', ''),
                        'link': news.get('link', ''),
                        'date': news.get('date', '')
                    }
                    for news in news_list
                ]
            }
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"新闻已保存到: {filepath}")
        return filepath


def main():
    """主函数 - 爬取所有股票的新闻"""
    # 股票代码列表
    stock_codes = ["301269", "688206", "301095"]  # 华大九天、概伦电子、广立微
    stock_names = {
        "301269": "华大九天",
        "688206": "概伦电子",
        "301095": "广立微",
    }
    
    all_results = {}
    
    for stock_code in stock_codes:
        company_name = stock_names.get(stock_code, stock_code)
        print("\n" + "=" * 60)
        print(f"正在爬取 {company_name}({stock_code}) 的新闻...")
        print("=" * 60)
        
        # 创建爬虫实例
        crawler = THSNewsCrawler(stock_code)
        
        # 执行爬取 (只获取当天)
        news_list = crawler.crawl(only_today=True)
        
        # 打印结果
        print(f"\n{company_name} 新闻列表:")
        for i, news in enumerate(news_list, 1):
            print(f"  {i}. {news['title']}")
            if news['date']:
                print(f"     日期: {news['date']}")
        
        if not news_list:
            print("  (当天无新闻)")
        
        # 保存到单独的文件
        crawler.save_to_json(news_list)
        
        all_results[stock_code] = news_list
    
    print("\n" + "=" * 60)
    print("所有股票爬取完成！")
    print("=" * 60)
    
    return all_results


if __name__ == "__main__":
    main()
