# -*- coding: utf-8 -*-
"""
电子工程世界新闻爬虫
爬取eeworld.com.cn上的EDA相关新闻
使用Selenium绕过WAF
"""

import os
import sys

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
    
    def __init__(self, keyword="EDA"):
        self.keyword = keyword
    
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
            try:
                driver = webdriver.Chrome(options=chrome_options)
            except Exception:
                from webdriver_manager.chrome import ChromeDriverManager
                service = Service(ChromeDriverManager().install())
                driver = webdriver.Chrome(service=service, options=chrome_options)
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
    
    def crawl(self, max_pages=10, days=30, shared_driver=None):
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
                # 构建URL
                if page == 1:
                    url = f"{self.SEARCH_URL}?wd={self.keyword}&sc=news"
                else:
                    url = f"{self.SEARCH_URL}?wd={self.keyword}&sc=news&pn={page}"
                
                # 加载页面（重试机制）
                max_retries = 3
                success = False
                for retry in range(max_retries):
                    try:
                        driver.get(url)
                        # 等待表格加载
                        WebDriverWait(driver, 20).until(
                            EC.presence_of_element_located((By.CSS_SELECTOR, 'table.result, .search-result, .result-list'))
                        )
                        success = True
                        break
                    except Exception as e:
                        if retry < max_retries - 1:
                            print(f"  第 {page} 页加载失败，重试 {retry + 1}/{max_retries}...")
                            time.sleep(2)
                        else:
                            print(f"  第 {page} 页加载失败: {e}")
                
                if not success:
                    break
                
                # 解析页面
                soup = BeautifulSoup(driver.page_source, 'html.parser')
                
                # 查找新闻表格
                result_table = soup.select_one('table.result')
                if not result_table:
                    print(f"  第 {page} 页没有找到新闻表格")
                    break
                
                # 获取所有新闻行
                news_rows = result_table.select('tr')
                
                if not news_rows:
                    print(f"  第 {page} 页没有找到新闻")
                    break
                
                page_count = 0
                stop_crawl = False
                
                for row in news_rows:
                    # 提取标题和链接
                    title_elem = row.select_one('td.f h3.t a')
                    if not title_elem:
                        continue
                    
                    title = title_elem.get_text(strip=True)
                    link = title_elem.get('href', '')
                    
                    # 从a标签的s_pub属性获取日期
                    date = title_elem.get('s_pub', '')
                    
                    if not date:
                        # 备选：从文本中提取日期
                        date_span = row.select_one('td.f p span.g')
                        if date_span:
                            date_text = date_span.get_text(strip=True)
                            date_match = re.search(r'(\d{4}-\d{2}-\d{2})', date_text)
                            date = date_match.group(1) if date_match else ''
                    
                    if not date or not link:
                        continue
                    
                    # 日期过滤
                    if date < cutoff_date:
                        stop_crawl = True
                        break
                    
                    all_news.append({
                        'title': title,
                        'link': link,
                        'date': date,
                        'source': '电子工程世界'
                    })
                    page_count += 1
                
                print(f"  第 {page} 页: {page_count} 条新闻")
                
                if stop_crawl:
                    print(f"  已达到日期限制，停止爬取")
                    break
                
                if page_count == 0:
                    print(f"  本页无有效新闻，停止爬取")
                    break
                
                time.sleep(1.5)  # 延迟1.5秒
        
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
        
        print(f"  共获取 {len(unique_news)} 条新闻")
        return unique_news
    
    def fetch_news_content(self, url):
        """
        获取新闻详情页的正文内容
        :param url: 新闻链接
        :return: 正文内容
        """
        # 使用Selenium获取内容（该网站有WAF）
        driver = self._init_driver()
        if not driver:
            return ''
        
        try:
            driver.get(url)
            time.sleep(2)  # 等待页面加载
            
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
            filename = os.path.join(os.path.dirname(__file__), '..', 'json', 'eeworld_news.json')
        
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(news_list, f, ensure_ascii=False, indent=2)
        
        print(f"  已保存到 {filename}")


if __name__ == "__main__":
    crawler = EEWorldNewsCrawler()
    news = crawler.crawl(max_pages=10, days=30)
    crawler.save_to_json(news)
