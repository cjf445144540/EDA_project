# -*- coding: utf-8 -*-
"""
搜狐新闻搜索爬虫
通过关键词搜索爬取 https://search.sohu.com 的新闻

支持两种渲染方式：
1. Playwright（推荐）: pip install playwright && playwright install chromium
2. Selenium（备选）: pip install selenium webdriver-manager
"""

import requests
from bs4 import BeautifulSoup
import json
import os
import re
import urllib3
from datetime import datetime, timedelta
import time

# 禁用 SSL 警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# 检查可用的浏览器自动化库
HAS_PLAYWRIGHT = False
HAS_SELENIUM = False

try:
    from playwright.sync_api import sync_playwright
    HAS_PLAYWRIGHT = True
except ImportError:
    pass

try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.chrome.service import Service
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    try:
        from webdriver_manager.chrome import ChromeDriverManager
        HAS_SELENIUM = True
    except ImportError:
        HAS_SELENIUM = True
except ImportError:
    pass


class SohuNewsCrawler:
    """搜狐新闻搜索爬虫"""
    
    SEARCH_URL = 'https://search.sohu.com/'
    
    def __init__(self, keyword="EDA"):
        self.keyword = keyword
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        }
    
    def _parse_relative_time(self, time_str):
        """解析相对时间（如"7小时前"、"3天前"）为日期字符串"""
        now = datetime.now()
        
        if not time_str:
            return ''
        
        time_str = time_str.strip()
        
        # 已经是标准日期格式
        if re.match(r'\d{4}-\d{1,2}-\d{1,2}', time_str):
            parts = time_str.split('-')
            if len(parts) == 3:
                return f"{parts[0]}-{parts[1].zfill(2)}-{parts[2].zfill(2)}"
            return time_str
        
        # 解析相对时间
        if '分钟前' in time_str:
            minutes = int(re.search(r'(\d+)', time_str).group(1))
            date = now - timedelta(minutes=minutes)
        elif '小时前' in time_str:
            hours = int(re.search(r'(\d+)', time_str).group(1))
            date = now - timedelta(hours=hours)
        elif '天前' in time_str:
            days = int(re.search(r'(\d+)', time_str).group(1))
            date = now - timedelta(days=days)
        elif '周前' in time_str:
            weeks = int(re.search(r'(\d+)', time_str).group(1))
            date = now - timedelta(weeks=weeks)
        elif '月前' in time_str:
            months = int(re.search(r'(\d+)', time_str).group(1))
            date = now - timedelta(days=months * 30)
        elif '刚刚' in time_str or '今天' in time_str:
            date = now
        elif '昨天' in time_str:
            date = now - timedelta(days=1)
        elif '前天' in time_str:
            date = now - timedelta(days=2)
        else:
            date_match = re.search(r'(\d{1,2})[-/](\d{1,2})', time_str)
            if date_match:
                month, day = date_match.groups()
                year = now.year
                return f"{year}-{month.zfill(2)}-{day.zfill(2)}"
            return ''
        
        return date.strftime('%Y-%m-%d')
    
    def crawl(self, max_pages=1, days=7, min_content_length=500):
        """
        爬取新闻列表
        :param max_pages: 最大爬取页数
        :param days: 只保留最近几天的新闻
        :param min_content_length: 最小内容字数
        :return: 新闻列表
        """
        if not HAS_PLAYWRIGHT and not HAS_SELENIUM:
            print("⚠️  搜狐新闻爬虫需要安装浏览器自动化库：")
            print("    方案1: pip install playwright && playwright install chromium")
            print("    方案2: pip install selenium webdriver-manager")
            return []
        
        # 优先使用Playwright，不可用时使用Selenium
        if HAS_PLAYWRIGHT:
            try:
                return self._crawl_with_playwright(max_pages, days, min_content_length)
            except Exception as e:
                error_msg = str(e)
                if "Executable doesn't exist" in error_msg or "playwright install" in error_msg:
                    if HAS_SELENIUM:
                        print("  Playwright浏览器未安装，切换到Selenium...")
                        return self._crawl_with_selenium(max_pages, days, min_content_length)
                    else:
                        print("⚠️  Playwright浏览器未安装，请执行: playwright install chromium")
                        return []
                raise
        else:
            return self._crawl_with_selenium(max_pages, days, min_content_length)
    
    def _crawl_with_playwright(self, max_pages, days, min_content_length):
        """使用Playwright爬取"""
        all_news = []
        cutoff_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
        skip_keywords = ['直播', '视频直播', '在线直播']
        
        print(f"\n正在爬取 搜狐网 新闻（关键词: {self.keyword}，最近 {days} 天）...")
        
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            )
            page = context.new_page()
            
            for page_num in range(1, max_pages + 1):
                url = f"{self.SEARCH_URL}?keyword={self.keyword}&page={page_num}"
                
                try:
                    page.goto(url, wait_until='networkidle', timeout=30000)
                    page.wait_for_selector('.plain-content', timeout=10000)
                    
                    content = page.content()
                    soup = BeautifulSoup(content, 'html.parser')
                    
                    items = soup.select('.plain-content')
                    page_count = 0
                    stop_crawl = False
                    
                    for item in items:
                        title_elem = item.select_one('h4 a')
                        if not title_elem:
                            continue
                        
                        title = title_elem.get_text(strip=True)
                        link = title_elem.get('href', '')
                        
                        if not title or not link:
                            continue
                        
                        # 确保链接完整
                        if link.startswith('//'):
                            link = 'https:' + link
                        elif not link.startswith('http'):
                            link = 'https://www.sohu.com' + link
                        
                        # 标题关键词过滤
                        if any(kw in title for kw in skip_keywords):
                            continue
                        
                        # 日期 - 从p:last-child的文本内容中提取
                        date = ''
                        date_elem = item.select_one('p:last-child')
                        if date_elem:
                            # 获取文本内容，日期格式可能是多种
                            date_text = date_elem.get_text(strip=True)
                            # 匹配多种日期格式
                            import re
                            # 相对时间
                            time_match = re.search(r'(\d+[分小时天周月]+前|刚刚|今天|昨天)', date_text)
                            if time_match:
                                date = self._parse_relative_time(time_match.group(1))
                            else:
                                # 绝对日期 YYYY-MM-DD 或 YYYY-M-D
                                date_match = re.search(r'(\d{4})-(\d{1,2})-(\d{1,2})', date_text)
                                if date_match:
                                    y, m, d = date_match.groups()
                                    date = f"{y}-{m.zfill(2)}-{d.zfill(2)}"
                                else:
                                    # 中文日期 M月D日
                                    cn_match = re.search(r'(\d{1,2})月(\d{1,2})日', date_text)
                                    if cn_match:
                                        m, d = cn_match.groups()
                                        date = f"{datetime.now().year}-{m.zfill(2)}-{d.zfill(2)}"
                        
                        if date and date < cutoff_date:
                            stop_crawl = True
                            continue
                        
                        all_news.append({
                            'title': title,
                            'link': link,
                            'date': date,
                            'source': '搜狐网',
                        })
                        page_count += 1
                    
                    print(f"  第 {page_num} 页: {page_count} 条新闻")
                    
                    if stop_crawl or page_count == 0:
                        break
                    
                    time.sleep(1)
                    
                except Exception as e:
                    print(f"  第 {page_num} 页出错: {e}")
                    break
            
            browser.close()
        
        return self._filter_and_dedupe(all_news, min_content_length)
    
    def _crawl_with_selenium(self, max_pages, days, min_content_length):
        """使用Selenium爬取"""
        all_news = []
        cutoff_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
        skip_keywords = ['直播', '视频直播', '在线直播']
        
        print(f"\n正在爬取 搜狐网 新闻（关键词: {self.keyword}，最近 {days} 天，使用Selenium）...")
        
        try:
            chrome_options = Options()
            chrome_options.add_argument('--headless')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
            
            try:
                from webdriver_manager.chrome import ChromeDriverManager
                service = Service(ChromeDriverManager().install())
                driver = webdriver.Chrome(service=service, options=chrome_options)
            except:
                driver = webdriver.Chrome(options=chrome_options)
            
            for page_num in range(1, max_pages + 1):
                url = f"{self.SEARCH_URL}?keyword={self.keyword}&page={page_num}"
                
                try:
                    driver.get(url)
                    WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, '.plain-content'))
                    )
                    
                    soup = BeautifulSoup(driver.page_source, 'html.parser')
                    items = soup.select('.plain-content')
                    page_count = 0
                    stop_crawl = False
                    
                    for item in items:
                        title_elem = item.select_one('h4 a')
                        if not title_elem:
                            continue
                        
                        title = title_elem.get_text(strip=True)
                        link = title_elem.get('href', '')
                        
                        if not title or not link:
                            continue
                        
                        if link.startswith('//'):
                            link = 'https:' + link
                        elif not link.startswith('http'):
                            link = 'https://www.sohu.com' + link
                        
                        if any(kw in title for kw in skip_keywords):
                            continue
                        
                        # 日期 - 从p:last-child的文本内容中提取
                        date = ''
                        date_elem = item.select_one('p:last-child')
                        if date_elem:
                            date_text = date_elem.get_text(strip=True)
                            # 相对时间
                            time_match = re.search(r'(\d+[分小时天周月]+前|刚刚|今天|昨天)', date_text)
                            if time_match:
                                date = self._parse_relative_time(time_match.group(1))
                            else:
                                # 绝对日期 YYYY-MM-DD 或 YYYY-M-D
                                date_match = re.search(r'(\d{4})-(\d{1,2})-(\d{1,2})', date_text)
                                if date_match:
                                    y, m, d = date_match.groups()
                                    date = f"{y}-{m.zfill(2)}-{d.zfill(2)}"
                                else:
                                    # 中文日期 M月D日
                                    cn_match = re.search(r'(\d{1,2})月(\d{1,2})日', date_text)
                                    if cn_match:
                                        m, d = cn_match.groups()
                                        date = f"{datetime.now().year}-{m.zfill(2)}-{d.zfill(2)}"
                        
                        if date and date < cutoff_date:
                            stop_crawl = True
                            continue
                        
                        all_news.append({
                            'title': title,
                            'link': link,
                            'date': date,
                            'source': '搜狐网',
                        })
                        page_count += 1
                    
                    print(f"  第 {page_num} 页: {page_count} 条新闻")
                    
                    if stop_crawl or page_count == 0:
                        break
                    
                    time.sleep(1)
                    
                except Exception as e:
                    print(f"  第 {page_num} 页出错: {e}")
                    break
            
            driver.quit()
            
        except Exception as e:
            print(f"  爬取出错: {e}")
        
        return self._filter_and_dedupe(all_news, min_content_length)
    
    def _filter_and_dedupe(self, all_news, min_content_length):
        """去重并过滤内容"""
        # 去重
        unique_news = []
        seen = set()
        for news in all_news:
            if news['link'] not in seen:
                seen.add(news['link'])
                unique_news.append(news)
        
        # 获取内容并过滤
        if min_content_length > 0 and unique_news:
            print(f"  正在获取新闻内容并过滤（>={min_content_length}字）...")
            filtered_news = []
            for news in unique_news:
                content = self.fetch_news_content(news['link'])
                content_len = len(content) if content else 0
                if content_len >= min_content_length:
                    news['content'] = content
                    filtered_news.append(news)
            unique_news = filtered_news
        
        print(f"  共获取 {len(unique_news)} 条新闻")
        return unique_news
    
    def fetch_news_content(self, url):
        """获取新闻详情页的正文内容"""
        for attempt in range(3):
            try:
                response = requests.get(
                    url,
                    headers=self.headers,
                    timeout=15,
                    verify=False,
                    proxies={'http': None, 'https': None}
                )
                response.encoding = 'utf-8'
                
                if response.status_code != 200:
                    return None
                
                soup = BeautifulSoup(response.text, 'html.parser')
                
                selectors = [
                    'article.article',
                    '.article-content',
                    '#mp-editor',
                    '.content-article',
                    '.text',
                    '.main',
                    'article',
                ]
                
                for selector in selectors:
                    content_elem = soup.select_one(selector)
                    if content_elem:
                        for tag in content_elem.find_all(['script', 'style', 'nav', 'aside', 'figure', 'header', 'footer', 'iframe']):
                            if hasattr(tag, 'decompose'):
                                tag.decompose()
                        
                        paragraphs = content_elem.find_all('p')
                        if paragraphs:
                            content = '\n'.join([p.get_text(strip=True) for p in paragraphs if p.get_text(strip=True) and len(p.get_text(strip=True)) > 10])
                            if content and len(content) > 100:
                                return content
                        
                        text = content_elem.get_text(separator='\n', strip=True)
                        if text and len(text) > 100:
                            return text
                
                return None
                
            except Exception:
                if attempt < 2:
                    time.sleep(1)
                    continue
                return None
    
    def save_to_json(self, news_list, filename='sohu_news.json'):
        """保存新闻到 JSON 文件"""
        output_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'json')
        os.makedirs(output_dir, exist_ok=True)
        filepath = os.path.join(output_dir, filename)
        
        data = {
            '行业新闻': {
                '搜狐网': [
                    {'title': n.get('title', ''), 'link': n.get('link', ''), 'date': n.get('date', ''), 'content': n.get('content', '')}
                    for n in news_list
                ]
            }
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"新闻已保存到: {filepath}")
        return filepath


def main():
    print("=" * 50)
    print("搜狐新闻爬虫 (关键词: EDA)")
    print("=" * 50)
    
    crawler = SohuNewsCrawler(keyword="EDA")
    news_list = crawler.crawl(max_pages=3, days=7, min_content_length=500)
    
    if news_list:
        print("\n爬取结果预览：")
        for i, news in enumerate(news_list[:5], 1):
            content_len = len(news.get('content', '')) if news.get('content') else 0
            print(f"\n{i}. {news['title']}")
            print(f"   日期: {news['date']} | 内容: {content_len}字")
            print(f"   链接: {news['link']}")
        crawler.save_to_json(news_list)
    else:
        print("\n未获取到任何新闻")


if __name__ == '__main__':
    main()
