# -*- coding: utf-8 -*-
"""
电子工程世界新闻爬虫
爬取eeworld.com.cn上的EDA相关新闻
使用Selenium绕过WAF
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
# 禁用 selenium-manager 自动下载
os.environ['SE_MANAGER_DISABLED'] = '1'
for _name in ['WDM', 'webdriver_manager', 'webdriver_manager.core', 'urllib3', 'selenium.webdriver.common.selenium_manager']:
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


class EEWorldNewsCrawler:
    """电子工程世界新闻爬虫类"""
    
    BASE_URL = "https://www.eeworld.com.cn"
    SEARCH_URL = "https://so.eeworld.com.cn/s"
    PAGE_READY_TIMEOUT = 10
    DETAIL_READY_TIMEOUT = 6
    RETRY_WAIT_SECONDS = 1.2
    PAGE_GAP_SECONDS = 0.5
    REQUEST_TIMEOUT = 10
    
    def __init__(self, keyword="EDA"):
        self.keyword = keyword
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Referer': self.BASE_URL + '/',
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)

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

    def _build_search_url(self, page):
        if page == 1:
            return f"{self.SEARCH_URL}?wd={self.keyword}&sc=news"
        return f"{self.SEARCH_URL}?wd={self.keyword}&sc=news&pn={page}"

    def _extract_news_from_soup(self, soup, cutoff_date):
        result_table = soup.select_one('table.result')
        if not result_table:
            return None, False
        news_rows = result_table.select('tr')
        if not news_rows:
            return [], False
        page_news = []
        stop_crawl = False
        for row in news_rows:
            title_elem = row.select_one('td.f h3.t a')
            if not title_elem:
                continue
            title = title_elem.get_text(strip=True)
            link = title_elem.get('href', '')
            content_preview = ''
            preview_elem = row.select_one('td.f p')
            if preview_elem:
                preview_copy = BeautifulSoup(str(preview_elem), 'html.parser')
                for tag in preview_copy.select('span.g'):
                    tag.decompose()
                content_preview = preview_copy.get_text(' ', strip=True)
            date = title_elem.get('s_pub', '')
            if not date:
                date_span = row.select_one('td.f p span.g')
                if date_span:
                    date_text = date_span.get_text(strip=True)
                    date_match = re.search(r'(\d{4}-\d{2}-\d{2})', date_text)
                    date = date_match.group(1) if date_match else ''
            if not date or not link:
                continue
            if date < cutoff_date:
                stop_crawl = True
                break
            page_news.append({
                'title': title,
                'link': link,
                'date': date,
                'source': '电子工程世界',
                'content': content_preview
            })
        return page_news, stop_crawl
    
    def _init_driver(self, suppress_warning=True):
        """初始化Chrome驱动"""
        chrome_options = ChromeOptions()
        chrome_options.add_argument('--headless=new')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-extensions')
        chrome_options.add_argument('--disable-infobars')
        # SSL和安全相关选项
        chrome_options.add_argument('--ignore-certificate-errors')
        chrome_options.add_argument('--ignore-ssl-errors')
        chrome_options.add_argument('--allow-insecure-localhost')
        chrome_options.add_argument('--disable-web-security')
        chrome_options.add_argument('--disable-features=IsolateOrigins,site-per-process')
        chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_experimental_option('excludeSwitches', ['enable-logging', 'enable-automation'])
        chrome_options.page_load_strategy = 'eager'
        
        driver = None
        
        if suppress_warning:
            # 在操作系统层面抑制webdriver_manager警告
            _orig_stdout_fd = os.dup(1)
            _orig_stderr_fd = os.dup(2)
            _devnull_fd = os.open(os.devnull, os.O_WRONLY)
            os.dup2(_devnull_fd, 1)
            os.dup2(_devnull_fd, 2)
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
        
        driver.set_page_load_timeout(30)
        return driver
    
    def crawl(self, max_pages=10, days=30, shared_driver=None, min_content_length=500):
        """
        爬取新闻列表
        :param max_pages: 最大爬取页数
        :param days: 只保留最近几天的新闻
        :param shared_driver: 共享的Chrome driver（可选）
        :return: 新闻列表
        """
        all_news = []
        cutoff_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
        
        print(f"\n正在爬取 电子工程世界 新闻（关键词: {self.keyword}，最近 {days} 天）...")
        
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
            for page in range(1, max_pages + 1):
                page_start = time.time()
                url = self._build_search_url(page)
                page_news = None
                stop_crawl = False
                page_mode = "requests"
                try:
                    response = self.session.get(
                        url,
                        timeout=self.REQUEST_TIMEOUT,
                        verify=False,
                        proxies={'http': None, 'https': None}
                    )
                    if response.status_code == 200:
                        response.encoding = response.apparent_encoding or 'utf-8'
                        req_soup = BeautifulSoup(response.text, 'html.parser')
                        page_news, stop_crawl = self._extract_news_from_soup(req_soup, cutoff_date)
                except Exception:
                    page_news = None

                if page_news is None:
                    page_mode = "selenium"
                    max_retries = 2 if use_shared else 3
                    success = False
                    for retry in range(max_retries):
                        try:
                            driver.get(url)
                            WebDriverWait(driver, self.PAGE_READY_TIMEOUT).until(
                                EC.presence_of_element_located((By.CSS_SELECTOR, 'table.result, .search-result, .result-list'))
                            )
                            success = True
                            break
                        except Exception as e:
                            if retry < max_retries - 1:
                                print(f"  第 {page} 页加载失败，重试 {retry + 1}/{max_retries}...")
                                time.sleep(self.RETRY_WAIT_SECONDS * (retry + 1))
                            else:
                                print(f"  第 {page} 页加载失败: {e}")
                    if not success:
                        break
                    soup = BeautifulSoup(driver.page_source, 'html.parser')
                    page_news, stop_crawl = self._extract_news_from_soup(soup, cutoff_date)
                    if page_news is None:
                        print(f"  第 {page} 页没有找到新闻表格")
                        break

                page_count = len(page_news)
                all_news.extend(page_news)
                elapsed = time.time() - page_start
                print(f"  第 {page} 页: {page_count} 条新闻 | {page_mode} | {elapsed:.2f}s")
                
                if stop_crawl:
                    print(f"  已达到日期限制，停止爬取")
                    break
                
                if page_count == 0:
                    print(f"  本页无有效新闻，停止爬取")
                    break
                
                if page < max_pages:
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
            filter_start = time.time()
            filtered_news = []
            req_hit = 0
            selenium_fallback_hit = 0
            for news in unique_news:
                content = news.get('content', '')
                if not content or len(content) < min_content_length:
                    content, used_selenium = self.fetch_news_content(news['link'], fallback_driver=(driver if use_shared else None), return_meta=True)
                    if content:
                        if used_selenium:
                            selenium_fallback_hit += 1
                        else:
                            req_hit += 1
                content_len = len(content) if content else 0
                if content_len >= min_content_length:
                    news['content'] = content
                    filtered_news.append(news)
            unique_news = filtered_news
            filter_elapsed = time.time() - filter_start
            print(f"  正文过滤耗时: {filter_elapsed:.2f}s | requests命中: {req_hit} | selenium回退命中: {selenium_fallback_hit}")
        
        print(f"  共获取 {len(unique_news)} 条新闻")
        return unique_news
    
    def fetch_news_content(self, url, fallback_driver=None, return_meta=False):
        """
        获取新闻详情页的正文内容
        :param url: 新闻链接
        :return: 正文内容
        """
        for attempt in range(2):
            try:
                response = self.session.get(
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
                for selector in ['.newscc', 'article .newscc', '.article-content', '.article-body', '.content', '#content', '.news-content', '.post-content', '.entry-content', 'article']:
                    content_div = soup.select_one(selector)
                    if not content_div:
                        continue
                    for tag in content_div.find_all(['script', 'style', 'iframe', 'nav', 'footer', 'aside']):
                        tag.decompose()
                    paragraphs = content_div.find_all('p')
                    if paragraphs:
                        content = '\n'.join([p.get_text(strip=True) for p in paragraphs if p.get_text(strip=True)])
                    else:
                        content = content_div.get_text(separator='\n', strip=True)
                    if content and len(content) > 50:
                        return (content, False) if return_meta else content
            except Exception:
                pass
        driver = fallback_driver if fallback_driver is not None else self._init_driver()
        if not driver:
            return ('', False) if return_meta else ''
        
        try:
            driver.get(url)
            try:
                WebDriverWait(driver, self.DETAIL_READY_TIMEOUT).until(
                    lambda d: d.find_elements(By.CSS_SELECTOR, '.newscc, article .newscc, .article-content, .article-body, #content, .news-content, article')
                )
            except:
                pass
            
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            
            # 尝试多个内容选择器
            content_selectors = [
                '.newscc',            # 电子工程世界正文
                'article .newscc',    # 备选
                '.article-content',
                '.article-body',
                '.content',
                '#content',
                '.news-content',
                '.post-content',
                '.entry-content',
                'article',
            ]
            
            for selector in content_selectors:
                content_div = soup.select_one(selector)
                if content_div:
                    # 移除脚本和样式
                    for tag in content_div.find_all(['script', 'style', 'iframe', 'nav', 'footer', 'aside']):
                        tag.decompose()
                    
                    # 提取文本
                    paragraphs = content_div.find_all('p')
                    if paragraphs:
                        content = '\n'.join([p.get_text(strip=True) for p in paragraphs if p.get_text(strip=True)])
                    else:
                        content = content_div.get_text(separator='\n', strip=True)
                    
                    if content and len(content) > 50:
                        return (content, True) if return_meta else content
            
            return ('', True) if return_meta else ''
            
        except Exception as e:
            print(f"  获取内容出错: {e}")
            return ('', True) if return_meta else ''
        finally:
            if fallback_driver is None:
                try:
                    driver.quit()
                except:
                    pass
    
    def save_to_json(self, news_list, filename=None):
        """保存新闻列表到JSON文件"""
        if filename is None:
            filename = os.path.join(os.path.dirname(__file__), '..', 'json', 'eeworld_news.json')
        
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(news_list, f, ensure_ascii=False, indent=2)
        
        print(f"  已保存到 {filename}")


if __name__ == "__main__":
    crawler = EEWorldNewsCrawler()
    news = crawler.crawl(max_pages=10, days=30)
    crawler.save_to_json(news)
