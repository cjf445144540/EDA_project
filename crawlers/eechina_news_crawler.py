# -*- coding: utf-8 -*-
"""
eechina新闻爬虫
爬取电子工程网上的EDA相关新闻
使用Selenium绑过WAF反爬验证
"""

import os
import sys
import requests
from bs4 import BeautifulSoup
import re
import json
from datetime import datetime, timedelta
import time

# Selenium相关
try:
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.chrome.service import Service
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    HAS_SELENIUM = True
except ImportError:
    HAS_SELENIUM = False


class EEChinaNewsCrawler:
    """eechina新闻爬虫类"""
    
    BASE_URL = "https://www.eechina.com"
    SEARCH_URL = "https://www.eechina.com/search.php"
    
    def __init__(self, keyword="EDA"):
        self.keyword = keyword
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Referer': 'https://www.eechina.com/',
        }
    
    def _init_driver(self, suppress_warning=True):
        """初始化Chrome驱动"""
        if not HAS_SELENIUM:
            return None
        
        chrome_options = Options()
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
    
    def crawl(self, max_pages=5, days=30, shared_driver=None):
        """
        爬取新闻列表（使用Selenium绑过WAF）
        :param max_pages: 最大爬取页数
        :param days: 只保留最近几天的新闻
        :param shared_driver: 共享的Chrome driver（可选）
        :return: 新闻列表
        """
        if not HAS_SELENIUM:
            print("  错误：需要安装selenium")
            return []
        
        all_news = []
        cutoff_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
        
        print(f"\n正在爬取 电子工程网 新闻（关键词: {self.keyword}，最近 {days} 天）...")
        
        # 使用共享driver或创建新driver
        use_shared = shared_driver is not None
        if use_shared:
            driver = shared_driver
        else:
            print("  正在启动Chrome...")
            driver = self._init_driver()
            if not driver:
                print(f"  Chrome启动失败")
                return []
            
            driver.set_page_load_timeout(30)
        
        try:
            for page in range(1, max_pages + 1):
                if page == 1:
                    url = f"{self.SEARCH_URL}?keyword={self.keyword}&orderby=datetime"
                else:
                    url = f"{self.SEARCH_URL}?keyword={self.keyword}&orderby=datetime&page={page}"
                
                try:
                    driver.get(url)
                    
                    # 等待页面加载（WAF验证后会自动跳转）
                    time.sleep(3)
                    
                    # 等待搜索结果出现
                    try:
                        WebDriverWait(driver, 10).until(
                            EC.presence_of_element_located((By.CSS_SELECTOR, 'li a[href*="thread-"]'))
                        )
                    except:
                        print(f"  第 {page} 页等待超时")
                        continue
                    
                    soup = BeautifulSoup(driver.page_source, 'html.parser')
                    
                    # 查找新闻项
                    news_items = soup.select('li')
                    
                    page_count = 0
                    stop_crawl = False
                    
                    for item in news_items:
                        title_elem = item.select_one('a[href*="thread-"]')
                        cite_elem = item.select_one('cite')
                        
                        if not title_elem or not cite_elem:
                            continue
                        
                        # 提取标题
                        title = title_elem.get_text(strip=True)
                        if not title or len(title) < 5:
                            continue
                        
                        # 提取链接
                        href = title_elem.get('href', '')
                        if href.startswith('http'):
                            link = href
                        else:
                            link = f"{self.BASE_URL}/{href}"
                        
                        # 提取日期
                        meta_text = cite_elem.get_text()
                        date_match = re.search(r'发表时间：(\d{4}-\d{2}-\d{2})', meta_text)
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
                            'source': '电子工程网'
                        })
                        page_count += 1
                    
                    print(f"  第 {page} 页: {page_count} 条新闻")
                    
                    if stop_crawl:
                        print(f"  已达到日期限制，停止爬取")
                        break
                    
                    time.sleep(1)
                        
                except Exception as e:
                    print(f"  第 {page} 页出错: {e}")
                    break
        
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
                'td.portal_content',       # 门户内容
                '#article-content',        # 文章容器
                '.t_f',                    # 帖子内容
                '.message',                # 消息内容
                '.article-content',
                '.post-content',
            ]
            
            # 优先尝试找postmessage_开头的元素
            for td in soup.select('td'):
                td_id = td.get('id', '')
                if td_id.startswith('postmessage_'):
                    content = td.get_text(separator='\n', strip=True)
                    if content and len(content) > 50:
                        return content
            
            for selector in content_selectors:
                content_div = soup.select_one(selector)
                if content_div:
                    # 移除脚本和样式
                    for tag in content_div.find_all(['script', 'style', 'iframe']):
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
            filename = os.path.join(os.path.dirname(__file__), '..', 'json', 'eechina_news.json')
        
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(news_list, f, ensure_ascii=False, indent=2)
        
        print(f"  已保存到 {filename}")


if __name__ == "__main__":
    crawler = EEChinaNewsCrawler()
    news = crawler.crawl(max_pages=5, days=30)
    crawler.save_to_json(news)
