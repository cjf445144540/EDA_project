# -*- coding: utf-8 -*-
"""
腾讯新闻搜索爬虫
通过关键词搜索爬取 https://news.qq.com/search 的新闻

支持两种渲染方式：
1. Playwright（推荐）: pip install playwright && playwright install chromium
2. Selenium（备选）: pip install selenium webdriver-manager
"""

import os
import logging
# 在任何import前禁用webdriver_manager日志和代理
os.environ['WDM_LOG'] = '0'
os.environ['WDM_LOG_LEVEL'] = '0'
os.environ['WDM_LOCAL'] = '1'
os.environ['WDM_SSL_VERIFY'] = '0'
os.environ['NO_PROXY'] = '*'
os.environ['no_proxy'] = '*'
for _name in ['WDM', 'webdriver_manager', 'webdriver_manager.core', 'urllib3']:
    logging.getLogger(_name).setLevel(logging.CRITICAL)
    logging.getLogger(_name).propagate = False
    logging.getLogger(_name).disabled = True

import requests
from bs4 import BeautifulSoup
import json
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
        # 尝试不使用webdriver_manager
        HAS_SELENIUM = True
except ImportError:
    pass


class QQNewsCrawler:
    """腾讯新闻搜索爬虫"""
    
    SEARCH_URL = 'https://news.qq.com/search'
    
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
        elif '昨天' in time_str:
            date = now - timedelta(days=1)
        elif '前天' in time_str:
            date = now - timedelta(days=2)
        else:
            return ''
        
        return date.strftime('%Y-%m-%d')
    
    def _extract_date_from_url(self, url):
        """从腾讯新闻URL中提取日期，支持多种格式"""
        if not url:
            return ''
        # 格式1: /rain/a/20260210A01U3Y00
        match = re.search(r'/a/(\d{8})', url)
        if match:
            date_str = match.group(1)
            return f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:8]}"
        # 格式2: /rain/a/LNK2026011406931000
        match = re.search(r'/a/LNK(\d{8})', url)
        if match:
            date_str = match.group(1)
            return f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:8]}"
        return ''

    def _is_keyword_relevant(self, text):
        if not text:
            return False
        text_lower = text.lower()
        keyword_lower = (self.keyword or '').strip().lower()
        if not keyword_lower:
            return True
        if keyword_lower in text_lower:
            return True
        if keyword_lower == 'eda':
            if '电子设计自动化' in text or '芯片设计' in text or 'ic设计' in text_lower:
                return True
        parts = [p for p in re.split(r'[\s,，/|]+', keyword_lower) if p]
        for p in parts:
            if p in text_lower:
                return True
        return False

    def _extract_news_from_html_fallback(self, html, cutoff_date, skip_keywords):
        """当页面结构变化导致主选择器失效时，回退到全页链接提取"""
        soup = BeautifulSoup(html, 'html.parser')
        result = []
        seen = set()
        anchors = soup.select('a[href]')
        for a in anchors:
            href = (a.get('href') or '').strip()
            if not href:
                continue
            if href.startswith('//'):
                href = 'https:' + href
            elif href.startswith('/'):
                href = 'https://news.qq.com' + href
            if not href.startswith('http'):
                continue
            if 'qq.com' not in href:
                continue
            if '/a/' not in href:
                continue
            date = self._extract_date_from_url(href)
            if not date:
                continue
            if date < cutoff_date:
                continue
            title = a.get_text(strip=True) or (a.get('title') or '').strip()
            if not title or len(title) < 8:
                continue
            if not self._is_keyword_relevant(title):
                continue
            if any(kw in title for kw in skip_keywords):
                continue
            key = (href, title)
            if key in seen:
                continue
            seen.add(key)
            result.append({
                'title': title,
                'link': href,
                'date': date,
                'source': '腾讯网',
            })
        return result

    def _extract_news_from_script_fallback(self, html, cutoff_date, skip_keywords):
        soup = BeautifulSoup(html, 'html.parser')
        result = []
        seen = set()
        patterns = [
            r'"url"\s*:\s*"(?P<url>https?:\\?/\\?/[^"]*?qq\.com[^"]*?/a/[^"]+)"[^{}]{0,600}"title"\s*:\s*"(?P<title>[^"]{6,200})"',
            r'"title"\s*:\s*"(?P<title>[^"]{6,200})"[^{}]{0,600}"url"\s*:\s*"(?P<url>https?:\\?/\\?/[^"]*?qq\.com[^"]*?/a/[^"]+)"',
        ]
        for script in soup.find_all('script'):
            content = script.string or script.get_text() or ''
            if not content:
                continue
            if '/a/' not in content and '\\/a\\/' not in content:
                continue
            for pattern in patterns:
                for m in re.finditer(pattern, content, flags=re.IGNORECASE):
                    href = (m.group('url') or '').replace('\\/', '/').replace('\\u002F', '/')
                    title = (m.group('title') or '').replace('\\"', '"').strip()
                    try:
                        title = title.encode('utf-8').decode('unicode_escape')
                    except Exception:
                        pass
                    if not href.startswith('http'):
                        continue
                    date = self._extract_date_from_url(href)
                    if not date or date < cutoff_date:
                        continue
                    if not title or len(title) < 8:
                        continue
                    if not self._is_keyword_relevant(title):
                        continue
                    if any(kw in title for kw in skip_keywords):
                        continue
                    key = (href, title)
                    if key in seen:
                        continue
                    seen.add(key)
                    result.append({
                        'title': title,
                        'link': href,
                        'date': date,
                        'source': '腾讯网',
                    })
        return result

    def _extract_news_from_search_engine_fallback(self, cutoff_date, skip_keywords):
        result = []
        seen = set()
        query = f"site:news.qq.com {self.keyword}"
        search_urls = [
            f"https://cn.bing.com/search?q={query}",
            f"https://www.bing.com/search?q={query}",
        ]
        for search_url in search_urls:
            try:
                resp = requests.get(search_url, headers=self.headers, timeout=12, verify=False, proxies={'http': None, 'https': None})
                if resp.status_code != 200:
                    continue
                soup = BeautifulSoup(resp.text, 'html.parser')
                for a in soup.select('li.b_algo h2 a, h2 a[href]'):
                    href = (a.get('href') or '').strip()
                    title = a.get_text(strip=True)
                    if not href or not title:
                        continue
                    if 'qq.com' not in href or '/a/' not in href:
                        continue
                    if not self._is_keyword_relevant(title):
                        continue
                    date = self._extract_date_from_url(href)
                    if not date or date < cutoff_date:
                        continue
                    if any(kw in title for kw in skip_keywords):
                        continue
                    key = (href, title)
                    if key in seen:
                        continue
                    seen.add(key)
                    result.append({
                        'title': title,
                        'link': href,
                        'date': date,
                        'source': '腾讯网',
                    })
                if result:
                    return result
            except Exception:
                continue
        return result
    
    def crawl(self, max_pages=3, days=7, min_content_length=500):
        """
        爬取新闻列表
        :param max_pages: 最大爬取页数
        :param days: 只保留最近几天的新闻
        :param min_content_length: 最小内容字数
        :return: 新闻列表
        """
        if not HAS_PLAYWRIGHT and not HAS_SELENIUM:
            print("[!] 腾讯新闻爬虫需要安装浏览器自动化库：")
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
                        print("[!] Playwright浏览器未安装，请执行: playwright install chromium")
                        print("    或安装Selenium: pip install selenium webdriver-manager")
                        return []
                raise
        else:
            return self._crawl_with_selenium(max_pages, days, min_content_length)
    
    def _crawl_with_playwright(self, max_pages, days, min_content_length):
        """使用Playwright爬取"""
        all_news = []
        cutoff_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
        
        # 过滤关键词
        skip_keywords = ['直播', '视频直播', '在线直播']
        
        print(f"\n正在爬取 腾讯网 新闻（关键词: {self.keyword}，最近 {days} 天）...")
        
        # 直接启动浏览器，让错误向上传播以便切换到Selenium
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            )
            page = context.new_page()
            
            for page_num in range(1, max_pages + 1):
                # 构建分页URL
                if page_num == 1:
                    url = f"{self.SEARCH_URL}?query={self.keyword}"
                else:
                    url = f"{self.SEARCH_URL}?query={self.keyword}&page={page_num}"
                
                page.goto(url, wait_until='networkidle', timeout=30000)
                
                # 等待新闻列表加载
                try:
                    page.wait_for_selector('div.card-margin.img-text-card', timeout=10000)
                except:
                    pass
                
                # 获取新闻列表
                news_items = page.query_selector_all('div.card-margin.img-text-card:not(.wiki-card)')
                
                if not news_items:
                    fallback_news = self._extract_news_from_html_fallback(page.content(), cutoff_date, skip_keywords)
                    if fallback_news:
                        all_news.extend(fallback_news)
                        print(f"  第 {page_num} 页: {len(fallback_news)} 条新闻（fallback）")
                        continue
                    fallback_news_script = self._extract_news_from_script_fallback(page.content(), cutoff_date, skip_keywords)
                    if fallback_news_script:
                        all_news.extend(fallback_news_script)
                        print(f"  第 {page_num} 页: {len(fallback_news_script)} 条新闻（script-fallback）")
                        continue
                    if page_num == 1:
                        fallback_news_search = self._extract_news_from_search_engine_fallback(cutoff_date, skip_keywords)
                        if fallback_news_search:
                            all_news.extend(fallback_news_search)
                            print(f"  第 {page_num} 页: {len(fallback_news_search)} 条新闻（search-fallback）")
                            break
                    print(f"  第 {page_num} 页没有新闻")
                    break
                
                page_count = 0
                stop_crawl = False
                
                for item in news_items:
                    try:
                        # 获取标题和链接
                        link_elem = item.query_selector('a.hover-link')
                        title_elem = item.query_selector('p.title')
                        time_elem = item.query_selector('span.time')
                        
                        if not link_elem or not title_elem:
                            continue
                        
                        title = title_elem.text_content().strip()
                        link = link_elem.get_attribute('href')
                        time_str = time_elem.text_content().strip() if time_elem else ''
                        
                        if not title or not link:
                            continue
                        
                        # 解析日期（先从URL提取，失败再用时间元素）
                        date = self._extract_date_from_url(link)
                        if not date:
                            date = self._parse_relative_time(time_str)
                        
                        # 日期过滤
                        if date and date < cutoff_date:
                            stop_crawl = True
                            continue
                        
                        # 标题关键词过滤
                        if any(kw in title for kw in skip_keywords):
                            continue
                        
                        all_news.append({
                            'title': title,
                            'link': link,
                            'date': date,
                            'source': '腾讯网',
                        })
                        page_count += 1
                        
                    except Exception:
                        continue
                
                print(f"  第 {page_num} 页: {page_count} 条新闻")
                
                if stop_crawl or page_count == 0:
                    break
                
                time.sleep(1)
            
            browser.close()
        
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
    
    def _crawl_with_selenium(self, max_pages, days, min_content_length):
        """使用Selenium爬取"""
        all_news = []
        cutoff_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
        skip_keywords = ['直播', '视频直播', '在线直播']
        
        print(f"\n正在爬取 腾讯网 新闻（关键词: {self.keyword}，最近 {days} 天，使用Selenium）...")
        
        try:
            # 配置Chrome选项（增强稳定性）
            chrome_options = Options()
            chrome_options.add_argument('--headless=new')  # 使用新版headless模式，更稳定
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-extensions')
            chrome_options.add_argument('--disable-software-rasterizer')
            chrome_options.add_argument('--disable-background-networking')
            chrome_options.add_argument('--disable-sync')
            chrome_options.add_argument('--proxy-server=direct://')  # 禁用代理
            chrome_options.add_argument('--proxy-bypass-list=*')
            chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
            
            # 尝试启动Chrome（在操作系统层面抑制webdriver_manager警告）
            print("  正在启动Chrome...")
            import sys
            
            # 保存原始文件描述符
            _orig_stdout_fd = os.dup(1)
            _orig_stderr_fd = os.dup(2)
            _devnull_fd = os.open(os.devnull, os.O_WRONLY)
            
            # 在OS层面重定向stdout和stderr到devnull
            os.dup2(_devnull_fd, 1)
            os.dup2(_devnull_fd, 2)
            sys.stdout = open(os.devnull, 'w')
            sys.stderr = open(os.devnull, 'w')
            
            driver = None
            startup_error = None
            try:
                try:
                    driver = webdriver.Chrome(options=chrome_options)
                except Exception:
                    # 系统Chrome失败，尝试webdriver_manager
                    from webdriver_manager.chrome import ChromeDriverManager
                    service = Service(ChromeDriverManager().install())
                    driver = webdriver.Chrome(service=service, options=chrome_options)
            except Exception as e:
                startup_error = e
            finally:
                # 恢复原始文件描述符
                os.dup2(_orig_stdout_fd, 1)
                os.dup2(_orig_stderr_fd, 2)
                os.close(_orig_stdout_fd)
                os.close(_orig_stderr_fd)
                os.close(_devnull_fd)
                sys.stdout = sys.__stdout__
                sys.stderr = sys.__stderr__
            
            if startup_error:
                print(f"  Selenium启动失败: {startup_error}")
                return []
            
            # 设置页面加载超时
            driver.set_page_load_timeout(30)
            
            for page_num in range(1, max_pages + 1):
                if page_num == 1:
                    url = f"{self.SEARCH_URL}?query={self.keyword}"
                else:
                    url = f"{self.SEARCH_URL}?query={self.keyword}&page={page_num}"
                
                driver.get(url)
                
                # 等待新闻列表加载
                try:
                    WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, 'div.card-margin.img-text-card'))
                    )
                except:
                    pass
                
                # 获取新闻列表
                news_items = driver.find_elements(By.CSS_SELECTOR, 'div.card-margin.img-text-card:not(.wiki-card)')
                
                if not news_items:
                    fallback_news = self._extract_news_from_html_fallback(driver.page_source, cutoff_date, skip_keywords)
                    if fallback_news:
                        all_news.extend(fallback_news)
                        print(f"  第 {page_num} 页: {len(fallback_news)} 条新闻（fallback）")
                        continue
                    fallback_news_script = self._extract_news_from_script_fallback(driver.page_source, cutoff_date, skip_keywords)
                    if fallback_news_script:
                        all_news.extend(fallback_news_script)
                        print(f"  第 {page_num} 页: {len(fallback_news_script)} 条新闻（script-fallback）")
                        continue
                    if page_num == 1:
                        fallback_news_search = self._extract_news_from_search_engine_fallback(cutoff_date, skip_keywords)
                        if fallback_news_search:
                            all_news.extend(fallback_news_search)
                            print(f"  第 {page_num} 页: {len(fallback_news_search)} 条新闻（search-fallback）")
                            break
                    print(f"  第 {page_num} 页没有新闻")
                    break
                
                page_count = 0
                stop_crawl = False
                
                for item in news_items:
                    try:
                        link_elem = item.find_element(By.CSS_SELECTOR, 'a.hover-link')
                        title_elem = item.find_element(By.CSS_SELECTOR, 'p.title')
                        
                        try:
                            time_elem = item.find_element(By.CSS_SELECTOR, 'span.time')
                            time_str = time_elem.text.strip()
                        except:
                            time_str = ''
                        
                        title = title_elem.text.strip()
                        link = link_elem.get_attribute('href')
                        
                        if not title or not link:
                            continue
                        
                        # 解析日期（先从URL提取，失败再用时间元素）
                        date = self._extract_date_from_url(link)
                        if not date:
                            date = self._parse_relative_time(time_str)
                        
                        if date and date < cutoff_date:
                            stop_crawl = True
                            continue
                        
                        if any(kw in title for kw in skip_keywords):
                            continue
                        
                        all_news.append({
                            'title': title,
                            'link': link,
                            'date': date,
                            'source': '腾讯网',
                        })
                        page_count += 1
                        
                    except Exception:
                        continue
                
                print(f"  第 {page_num} 页: {page_count} 条新闻")
                
                if stop_crawl or page_count == 0:
                    break
                
                time.sleep(1)
            
        except Exception as e:
            print(f"  爬取出错: {e}")
        finally:
            # 确保Chrome正确关闭
            try:
                driver.quit()
            except:
                pass
        
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
                
                # 腾讯新闻详情页正文选择器
                selectors = [
                    'div.content-article',
                    'div.Cnt-Main-Article-QQ',
                    'div.LEFT div.content',
                    '.article-content',
                    '#Cnt-Main-Article-QQ',
                    'article',
                    '.content',
                ]
                
                for selector in selectors:
                    content_elem = soup.select_one(selector)
                    if content_elem:
                        # 移除无关标签
                        for tag in content_elem.find_all(['script', 'style', 'nav', 'aside', 'figure', 'header', 'footer', 'iframe']):
                            if hasattr(tag, 'decompose'):
                                tag.decompose()
                        
                        # 从 <p> 标签获取内容
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
    
    def save_to_json(self, news_list, filename='qq_news.json'):
        """保存新闻到 JSON 文件"""
        output_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'json')
        os.makedirs(output_dir, exist_ok=True)
        filepath = os.path.join(output_dir, filename)
        
        data = {
            '行业新闻': {
                '腾讯网': [
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
    print("腾讯新闻爬虫 (关键词: EDA)")
    print("=" * 50)
    
    crawler = QQNewsCrawler(keyword="EDA")
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
