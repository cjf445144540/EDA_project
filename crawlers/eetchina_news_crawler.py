# -*- coding: utf-8 -*-
"""
电子工程专辑新闻爬虫
爬取eet-china.com上的EDA相关新闻
使用Selenium绕过网络问题
"""

import os
import sys
import logging
from glob import glob

# 禁用 webdriver_manager 网络请求
os.environ['WDM_LOG'] = '0'
os.environ['WDM_LOG_LEVEL'] = '0'
os.environ['WDM_LOCAL'] = '1'
os.environ['WDM_SSL_VERIFY'] = '0'
os.environ['WDM_OFFLINE'] = '1'
os.environ['NO_PROXY'] = '*'
os.environ['no_proxy'] = '*'
for _name in ['WDM', 'webdriver_manager', 'webdriver_manager.core', 'urllib3']:
    logging.getLogger(_name).setLevel(logging.CRITICAL)
    logging.getLogger(_name).propagate = False
    logging.getLogger(_name).disabled = True

import requests

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import re
import json
from datetime import datetime, timedelta
import time


class EETChinaNewsCrawler:
    """电子工程专辑新闻爬虫类"""
    
    BASE_URL = "https://www.eet-china.com"
    SEARCH_URL = "https://www.eet-china.com/e/sch/index.php"
    PAGE_READY_TIMEOUT = 12
    DETAIL_READY_TIMEOUT = 8
    RETRY_WAIT_SECONDS = 1.2
    PAGE_GAP_SECONDS = 0.4
    
    def __init__(self, keyword="eda"):
        self.keyword = keyword
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Referer': self.BASE_URL + '/',
        }

    def _find_local_chromedriver(self):
        roots = [
            os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.wdm', 'drivers', 'chromedriver'),
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
    
    def _init_driver(self, suppress_warning=True):
        """初始化Chrome驱动"""
        chrome_options = ChromeOptions()
        chrome_options.add_argument('--headless=new')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-extensions')
        chrome_options.add_argument('--disable-infobars')
        # SSL和安全相关选项（解决eet-china.com连接问题）
        chrome_options.add_argument('--ignore-certificate-errors')
        chrome_options.add_argument('--ignore-ssl-errors')
        chrome_options.add_argument('--allow-insecure-localhost')
        chrome_options.add_argument('--disable-web-security')
        chrome_options.add_argument('--disable-features=IsolateOrigins,site-per-process')
        chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        chrome_options.add_experimental_option('excludeSwitches', ['enable-logging', 'enable-automation'])
        # 使用eager加载策略：只等待DOM加载完成
        chrome_options.page_load_strategy = 'eager'
        
        driver = None
        
        if suppress_warning:
            # 在操作系统层面抑制webdriver_manager警告
            _orig_stdout_fd = os.dup(1)
            _orig_stderr_fd = os.dup(2)
            _devnull_fd = os.open(os.devnull, os.O_WRONLY)
            os.dup2(_devnull_fd, 1)
            os.dup2(_devnull_fd, 2)
            _old_stdout, _old_stderr = sys.stdout, sys.stderr
            sys.stdout = sys.stderr = open(os.devnull, 'w')
        
        try:
            # 优先使用本地缓存的 chromedriver
            local_driver = self._find_local_chromedriver()
            if local_driver:
                try:
                    service = Service(local_driver)
                    driver = webdriver.Chrome(service=service, options=chrome_options)
                except Exception:
                    driver = None
            
            # 尝试不指定 service 直接创建
            if driver is None:
                try:
                    driver = webdriver.Chrome(options=chrome_options)
                except Exception:
                    driver = None
        except Exception as e:
            if suppress_warning:
                os.dup2(_orig_stdout_fd, 1)
                os.dup2(_orig_stderr_fd, 2)
                os.close(_orig_stdout_fd)
                os.close(_orig_stderr_fd)
                os.close(_devnull_fd)
                sys.stdout, sys.stderr = sys.__stdout__, sys.__stderr__
            print(f"  Chrome驱动初始化失败: {e}")
            return None
        finally:
            if suppress_warning:
                os.dup2(_orig_stdout_fd, 1)
                os.dup2(_orig_stderr_fd, 2)
                os.close(_orig_stdout_fd)
                os.close(_orig_stderr_fd)
                os.close(_devnull_fd)
                sys.stdout, sys.stderr = sys.__stdout__, sys.__stderr__
        
        # 设置较短的超时（因为用了eager策略，加载会快很多）
        driver.set_page_load_timeout(30)
        return driver
    
    def crawl(self, max_pages=10, days=90, shared_driver=None, min_content_length=500):
        """
        爬取新闻列表
        :param max_pages: 最大爬取页数
        :param days: 只保留最近几天的新闻
        :param shared_driver: 共享的Chrome driver（可选）
        :return: 新闻列表
        """
        all_news = []
        cutoff_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
        
        print(f"\n正在爬取 电子工程专辑 新闻（关键词: {self.keyword}，最近 {days} 天）...")
        
        # 使用共享driver或创建新driver
        use_shared = shared_driver is not None
        if use_shared:
            driver = shared_driver
        else:
            print("  正在启动Chrome...")
            driver = self._init_driver()
            if not driver:
                print("  Chrome驱动初始化失败")
                return []
        
        try:
            for page in range(0, max_pages):
                # 构建URL
                if page == 0:
                    url = f"{self.SEARCH_URL}?keyboard={self.keyword}&field=2"
                else:
                    url = f"{self.SEARCH_URL}?page={page}&keyboard={self.keyword}&field=2&sear=1"
                
                # 加载页面（重试机制）
                max_retries = 2 if use_shared else 3
                success = False
                for retry in range(max_retries):
                    try:
                        driver.get(url)
                        WebDriverWait(driver, self.PAGE_READY_TIMEOUT).until(
                            EC.presence_of_element_located((By.CSS_SELECTOR, 'ul.main_list, li.search-article-item'))
                        )
                        success = True
                        break
                    except Exception as e:
                        if retry < max_retries - 1:
                            print(f"  第 {page + 1} 页加载失败，重试 {retry + 1}/{max_retries}...")
                            time.sleep(self.RETRY_WAIT_SECONDS * (retry + 1))
                        else:
                            error_msg = str(e)
                            if 'timeout' in error_msg.lower() or 'Timed out' in error_msg:
                                print(f"  第 {page + 1} 页加载超时")
                            else:
                                print(f"  第 {page + 1} 页加载失败")
                
                if not success:
                    break
                
                # 解析页面
                soup = BeautifulSoup(driver.page_source, 'html.parser')
                news_items = soup.select('ul.main_list > li.search-article-item')
                
                if not news_items:
                    print(f"  第 {page + 1} 页没有找到新闻")
                    break
                
                page_count = 0
                stop_crawl = False
                
                for item in news_items:
                    # 提取标题和链接
                    title_elem = item.select_one('div.search-article-item-name > a')
                    if not title_elem:
                        continue
                    
                    title = title_elem.get_text(strip=True)
                    href = title_elem.get('href', '')
                    if not href.startswith('http'):
                        link = f"{self.BASE_URL}{href}" if href.startswith('/') else f"{self.BASE_URL}/{href}"
                    else:
                        link = href
                    
                    # 提取日期
                    date_elem = item.select_one('span.search-article-item-date')
                    date = ''
                    if date_elem:
                        date_text = date_elem.get_text(strip=True)
                        # 格式: 2026-03-18 10:30:00
                        date_match = re.search(r'(\d{4}-\d{2}-\d{2})', date_text)
                        date = date_match.group(1) if date_match else ''
                    
                    if not date:
                        continue
                    
                    # 日期过滤
                    if date < cutoff_date:
                        stop_crawl = True
                        break
                    
                    all_news.append({
                        'title': title,
                        'link': link,
                        'date': date,
                        'source': '电子工程专辑'
                    })
                    page_count += 1
                
                print(f"  第 {page + 1} 页: {page_count} 条新闻")
                
                if stop_crawl:
                    print(f"  已达到日期限制，停止爬取")
                    break
                
                if page < max_pages - 1:
                    time.sleep(self.PAGE_GAP_SECONDS)
        
        except Exception as e:
            print(f"  爬取出错: {e}")
        finally:
            # 只有非共享driver才关闭
            if not use_shared:
                try:
                    driver.quit()
                except:
                    pass
        
        # 去重
        unique_news = []
        seen_links = set()
        for news in all_news:
            if news['link'] not in seen_links:
                seen_links.add(news['link'])
                unique_news.append(news)
        
        if min_content_length > 0 and unique_news:
            print(f"  正在获取新闻内容并过滤（>={min_content_length}字）...")
            filtered_news = []
            for news in unique_news:
                content = news.get('content', '')
                if not content or len(content) < min_content_length:
                    content = self.fetch_news_content(news['link'])
                content_len = len(content) if content else 0
                if content_len >= min_content_length:
                    news['content'] = content
                    filtered_news.append(news)
            unique_news = filtered_news
        
        print(f"  共获取 {len(unique_news)} 条新闻")
        return unique_news
    
    def fetch_news_content(self, url):
        """
        获取新闻详情页的正文内容
        :param url: 新闻链接
        :return: 正文内容
        """
        for attempt in range(2):
            try:
                response = requests.get(
                    url,
                    headers=self.headers,
                    timeout=12,
                    verify=False,
                    proxies={'http': None, 'https': None}
                )
                if response.status_code != 200:
                    continue
                response.encoding = response.apparent_encoding or 'utf-8'
                soup = BeautifulSoup(response.text, 'html.parser')
                for tag in soup.select('.partner-content, .recommend, .hot-article, .related, aside, .sidebar, .ad, .share, .comment'):
                    tag.decompose()
                for selector in ['.article-con', '.article-detail', '.article-detail-content', '.article-content', '.detail-content', '.news-content', '.article-body', '#article-content']:
                    content_div = soup.select_one(selector)
                    if not content_div:
                        continue
                    for tag in content_div.find_all(['script', 'style', 'iframe', 'nav', 'footer']):
                        tag.decompose()
                    paragraphs = content_div.find_all('p')
                    if paragraphs:
                        content = '\n'.join([p.get_text(strip=True) for p in paragraphs if p.get_text(strip=True)])
                    else:
                        content = content_div.get_text(separator='\n', strip=True)
                    if content and len(content) > 50:
                        return content
            except Exception:
                pass
        driver = self._init_driver()
        if not driver:
            return ''
        
        try:
            driver.get(url)
            WebDriverWait(driver, self.DETAIL_READY_TIMEOUT).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, '.article-con, .article-detail, .article-content, .article-body, #article-content'))
            )
            
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            
            # 尝试多个内容选择器
            content_selectors = [
                '.article-con',       # 电子工程专辑正文
                '.article-detail',    # 文章详情
                '.news-content',      # 新闻内容
                '.article-content',
                '.article-body',
                '.content-article',
                '.post-content',
                '#article-content',
                '.entry-content',
            ]
            
            for selector in content_selectors:
                content_div = soup.select_one(selector)
                if content_div:
                    # 移除脚本和样式
                    for tag in content_div.find_all(['script', 'style', 'iframe', 'nav', 'footer']):
                        tag.decompose()
                    
                    # 提取文本
                    paragraphs = content_div.find_all('p')
                    if paragraphs:
                        content = '\n'.join([p.get_text(strip=True) for p in paragraphs if p.get_text(strip=True)])
                    else:
                        content = content_div.get_text(separator='\n', strip=True)
                    
                    if content and len(content) > 50:
                        return content
            
            return ''
            
        except Exception as e:
            print(f"  获取内容出错: {e}")
            return ''
        finally:
            try:
                driver.quit()
            except:
                pass
    
    def save_to_json(self, news_list, filename=None):
        """保存新闻列表到JSON文件"""
        if filename is None:
            filename = os.path.join(os.path.dirname(__file__), '..', 'json', 'eetchina_news.json')
        
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(news_list, f, ensure_ascii=False, indent=2)
        
        print(f"  已保存到 {filename}")


if __name__ == "__main__":
    crawler = EETChinaNewsCrawler()
    news = crawler.crawl(max_pages=10, days=90)
    crawler.save_to_json(news)
