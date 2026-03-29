# -*- coding: utf-8 -*-
import os
import re
import json
import time
from glob import glob
from datetime import datetime, timedelta
from urllib.parse import urlsplit, urlunsplit

import requests
import urllib3
from bs4 import BeautifulSoup

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class EastmoneyNewsCrawler:
    SEARCH_URL = "https://so.eastmoney.com/news/s"

    def __init__(self, keyword="EDA"):
        self.keyword = keyword
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Referer': 'https://so.eastmoney.com/',
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)

    def _build_keywords(self, keywords):
        if keywords:
            vals = [str(x).strip() for x in keywords if str(x).strip()]
            if vals:
                return vals
        key = (self.keyword or '').strip()
        if key:
            return [key]
        return ['EDA', 'synopsys', '新思科技']

    def _is_keyword_relevant(self, text, keywords):
        t = (text or '').lower()
        for k in keywords:
            k2 = (k or '').strip().lower()
            if k2 and k2 in t:
                return True
        if ('synopsys' in t) or ('新思科技' in (text or '')):
            return ('synopsys' in [k.lower() for k in keywords]) or ('新思科技' in keywords)
        if 'eda' in [k.lower() for k in keywords]:
            return ('电子设计自动化' in (text or '')) or ('ic design' in t)
        return False

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

    def _create_driver(self):
        try:
            from selenium import webdriver
            from selenium.webdriver.chrome.options import Options
            from selenium.webdriver.chrome.service import Service
        except Exception:
            return None

        chrome_options = Options()
        chrome_options.add_argument('--headless=new')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-extensions')
        chrome_options.add_argument('--proxy-server=direct://')
        chrome_options.add_argument('--proxy-bypass-list=*')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_experimental_option('excludeSwitches', ['enable-automation'])
        chrome_options.add_experimental_option('useAutomationExtension', False)

        try:
            return webdriver.Chrome(options=chrome_options)
        except Exception:
            local_driver = self._find_local_chromedriver()
            if local_driver:
                try:
                    service = Service(local_driver)
                    return webdriver.Chrome(service=service, options=chrome_options)
                except Exception:
                    pass
            return None

    def _normalize_link(self, link):
        try:
            sp = urlsplit((link or '').strip())
            return urlunsplit((sp.scheme, sp.netloc, sp.path, '', ''))
        except Exception:
            return (link or '').strip()

    def _normalize_title(self, title):
        text = ' '.join((title or '').split())
        text = re.sub(r'(?<![A-Za-z])(?:[A-Za-z]\s+){1,}[A-Za-z](?!\s*[A-Za-z])', lambda m: m.group(0).replace(' ', ''), text)
        text = re.sub(r'([\u4e00-\u9fff])\s+([A-Z]{2,})', r'\1\2', text)
        text = re.sub(r'([A-Z]{2,})\s+([\u4e00-\u9fff])', r'\1\2', text)
        return text.strip()

    def _extract_news_items(self, html):
        soup = BeautifulSoup(html or '', 'html.parser')
        items = []
        for node in soup.select('.news_list .news_item'):
            t_a = node.select_one('.news_item_t a[href]')
            if not t_a:
                continue
            title = self._normalize_title(t_a.get_text(' ', strip=True))
            link = self._normalize_link(t_a.get('href', '').strip())
            if not title or not link:
                continue
            time_text = ''
            t_node = node.select_one('.news_item_c .news_item_time')
            if t_node:
                time_text = ' '.join(t_node.get_text(' ', strip=True).split()).strip('- ').strip()
            abstract = ''
            c_node = node.select_one('.news_item_c')
            if c_node:
                c_clone = BeautifulSoup(str(c_node), 'html.parser')
                for x in c_clone.select('.news_item_time'):
                    x.decompose()
                abstract = ' '.join(c_clone.get_text(' ', strip=True).split())
            items.append({
                'title': title,
                'link': link,
                'date': time_text[:10] if re.match(r'\d{4}-\d{2}-\d{2}', time_text or '') else '',
                'source': '东方财富网',
                'abstract': abstract
            })
        return items

    def crawl(self, max_pages=1, days=7, min_content_length=0, keywords=None):
        kw_list = self._build_keywords(keywords)
        cutoff_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
        print(f"\n正在爬取 东方财富网（关键词: {', '.join(kw_list)}，最近 {days} 天）...")

        driver = self._create_driver()
        if driver is None:
            print("  初始化浏览器失败，返回空结果")
            return []

        all_news = []
        seen = set()
        try:
            for kw in kw_list:
                kw_count = 0
                for page_num in range(1, max_pages + 1):
                    url = f"{self.SEARCH_URL}?keyword={kw}&pageindex={page_num}"
                    try:
                        driver.get(url)
                        time.sleep(2.5)
                        page_news = self._extract_news_items(driver.page_source)
                    except Exception:
                        page_news = []
                    page_count = 0
                    for n in page_news:
                        title = n.get('title', '')
                        link = n.get('link', '')
                        date = n.get('date', '')
                        mix = f"{title}\n{n.get('abstract', '')}"
                        if not title or not link:
                            continue
                        if date and date < cutoff_date:
                            continue
                        if not self._is_keyword_relevant(mix, kw_list):
                            continue
                        if link in seen:
                            continue
                        seen.add(link)
                        all_news.append({
                            'title': title,
                            'link': link,
                            'date': date,
                            'source': '东方财富网'
                        })
                        page_count += 1
                        kw_count += 1
                    print(f"  关键词 {kw} 第 {page_num} 页: {page_count} 条新闻")
                    if not page_news:
                        break
                print(f"  关键词 {kw}: {kw_count} 条新闻")
        finally:
            try:
                driver.quit()
            except Exception:
                pass

        all_news.sort(key=lambda x: x.get('date', ''), reverse=True)
        if min_content_length > 0 and all_news:
            print(f"  正在获取新闻内容并过滤（>={min_content_length}字）...")
            filtered = []
            for n in all_news:
                content = self.fetch_news_content(n.get('link', ''))
                if content and len(content) >= min_content_length:
                    n['content'] = content
                    filtered.append(n)
            all_news = filtered
        print(f"  共获取 {len(all_news)} 条新闻")
        return all_news

    def fetch_news_content(self, url):
        if not url:
            return ''
        try:
            resp = self.session.get(url, timeout=20, verify=False)
            if resp.status_code != 200:
                return ''
            resp.encoding = resp.apparent_encoding or 'utf-8'
            soup = BeautifulSoup(resp.text, 'html.parser')
            lines = []
            meta_desc = soup.select_one('meta[name="Description"], meta[property="og:description"]')
            if meta_desc:
                txt = ' '.join((meta_desc.get('content', '') or '').split())
                if txt:
                    lines.append(txt)
            content = soup.select_one('#ContentBody')
            if content:
                for t in content(['script', 'style', 'noscript', 'iframe', 'form']):
                    t.decompose()
                for p in content.select('p, h2, h3'):
                    txt = ' '.join((p.get_text(' ', strip=True) or '').split())
                    if txt and len(txt) > 10:
                        lines.append(txt)
            seen = set()
            out = []
            for x in lines:
                k = x.lower()
                if k in seen:
                    continue
                seen.add(k)
                out.append(x)
            return '\n'.join(out[:180])
        except Exception:
            return ''

    def save_to_json(self, news_list, filename='eastmoney_news.json'):
        output_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'json')
        os.makedirs(output_dir, exist_ok=True)
        filepath = os.path.join(output_dir, filename)
        data = {
            '行业新闻': {
                '东方财富网': [
                    {
                        'title': n.get('title', ''),
                        'link': n.get('link', ''),
                        'date': n.get('date', ''),
                        'content': n.get('content', '')
                    }
                    for n in news_list
                ]
            }
        }
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"新闻已保存到: {filepath}")
        return filepath


def main():
    crawler = EastmoneyNewsCrawler(keyword='EDA')
    news = crawler.crawl(max_pages=1, days=7, keywords=['EDA', 'synopsys', '新思科技'])
    crawler.save_to_json(news)


if __name__ == '__main__':
    main()
