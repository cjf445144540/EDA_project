# -*- coding: utf-8 -*-
import os
import json
import re
from datetime import datetime, timedelta
from urllib.parse import urljoin, urlsplit, urlunsplit

import requests
import urllib3
from bs4 import BeautifulSoup

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class DigitimesNewsCrawler:
    BASE_URL = "https://www.digitimes.com"
    SEARCH_URL = "https://www.digitimes.com/search/results.php"

    def __init__(self, keyword="EDA"):
        self.keyword = keyword
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Referer': 'https://www.digitimes.com/',
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
        return ['EDA']

    def _is_keyword_relevant(self, text, keywords):
        t = (text or '').lower()
        for k in keywords:
            k2 = (k or '').strip().lower()
            if k2 and k2 in t:
                return True
        if 'eda' in [k.lower() for k in keywords]:
            return 'electronic design automation' in t or 'ic design' in t
        if 'synopsys' in [k.lower() for k in keywords]:
            return 'synopsys' in t or '新思' in text
        return False

    def _parse_date(self, text):
        if not text:
            return ''
        text = ' '.join(text.split())
        m = re.search(r'([A-Za-z]+)\s+(\d{1,2})\s+([A-Za-z]+)\s+(\d{4})', text)
        if not m:
            m = re.search(r'(\d{1,2})\s+([A-Za-z]+)\s+(\d{4})', text)
            if not m:
                return ''
            day, mon, year = m.groups()
        else:
            _, day, mon, year = m.groups()
        mon_map = {
            'Jan': '01', 'January': '01',
            'Feb': '02', 'February': '02',
            'Mar': '03', 'March': '03',
            'Apr': '04', 'April': '04',
            'May': '05',
            'Jun': '06', 'June': '06',
            'Jul': '07', 'July': '07',
            'Aug': '08', 'August': '08',
            'Sep': '09', 'Sept': '09', 'September': '09',
            'Oct': '10', 'October': '10',
            'Nov': '11', 'November': '11',
            'Dec': '12', 'December': '12',
        }
        mm = mon_map.get(mon, '')
        if not mm:
            return ''
        return f"{year}-{mm}-{str(day).zfill(2)}"

    def _search_page(self, keyword, page_num):
        params = {
            'h': '0',
            's': '18',
            'f': '0',
            'b': str(page_num),
            'a2': '35',
            'b2': '1',
            's2': '2',
            'p': keyword,
            'a': '',
            'o': '4',
            'ch': '18',
            'v': 'KS',
        }
        resp = self.session.get(self.SEARCH_URL, params=params, timeout=20, verify=False)
        if resp.status_code != 200:
            return []
        soup = BeautifulSoup(resp.text, 'html.parser')
        pane = soup.select_one('#result .search-pane')
        if not pane:
            return []

        rows = pane.find_all('div', class_=lambda x: x and 'row' in x.split())
        out = []
        for row in rows:
            link_el = row.select_one('a.subject[href^="/news/"]')
            if not link_el:
                continue
            title = ' '.join(link_el.get_text(' ', strip=True).split())
            href = link_el.get('href', '').strip()
            link = self._normalize_link(urljoin(self.BASE_URL, href))
            date_text = ''
            abstract = ''
            next_row = row.find_next_sibling('div')
            if next_row and next_row.get('class') and 'row' in next_row.get('class'):
                date_el = next_row.select_one('.date')
                if date_el:
                    date_text = ' '.join(date_el.get_text(' ', strip=True).split())
                next2 = next_row.find_next_sibling('div')
                if next2:
                    ab_el = next2.select_one('.abstract')
                    if ab_el:
                        abstract = ' '.join(ab_el.get_text(' ', strip=True).split())
            out.append({
                'title': title,
                'link': link,
                'date': self._parse_date(date_text),
                'abstract': abstract,
                'source': 'DIGITIMES'
            })
        return out

    def _normalize_link(self, link):
        try:
            sp = urlsplit((link or '').strip())
            return urlunsplit((sp.scheme, sp.netloc, sp.path, '', ''))
        except Exception:
            return (link or '').strip()

    def crawl(self, max_pages=1, days=7, min_content_length=0, keywords=None):
        kw_list = self._build_keywords(keywords)
        cutoff_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
        print(f"\n正在爬取 DIGITIMES（关键词: {', '.join(kw_list)}，最近 {days} 天）...")
        all_news = []
        seen = set()

        for kw in kw_list:
            kw_count = 0
            for page_num in range(1, max_pages + 1):
                try:
                    page_news = self._search_page(kw, page_num)
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
                        'source': 'DIGITIMES'
                    })
                    page_count += 1
                    kw_count += 1
                print(f"  关键词 {kw} 第 {page_num} 页: {page_count} 条新闻")
                if not page_news:
                    break
            print(f"  关键词 {kw}: {kw_count} 条新闻")

        all_news.sort(key=lambda x: x.get('date', ''), reverse=True)
        if min_content_length > 0 and all_news:
            print(f"  正在获取新闻内容并过滤（>={min_content_length}字）...")
            filtered_news = []
            for n in all_news:
                content = self.fetch_news_content(n.get('link', ''))
                if content and len(content) >= min_content_length:
                    n['content'] = content
                    filtered_news.append(n)
            all_news = filtered_news
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
            desc = soup.select_one('meta[name="Description"], meta[property="og:description"]')
            if desc:
                d = ' '.join((desc.get('content', '') or '').split())
                if d:
                    lines.append(d)
            content = soup.select_one('#content')
            if content:
                for t in content(['script', 'style', 'noscript', 'iframe', 'form']):
                    t.decompose()
                for p in content.select('p, h2, h3'):
                    txt = ' '.join((p.get_text(' ', strip=True) or '').split())
                    if txt and len(txt) > 20:
                        lines.append(txt)
            uniq = []
            seen = set()
            for x in lines:
                k = x.lower()
                if k in seen:
                    continue
                seen.add(k)
                uniq.append(x)
            return '\n'.join(uniq[:120])
        except Exception:
            return ''

    def save_to_json(self, news_list, filename='digitimes_news.json'):
        output_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'json')
        os.makedirs(output_dir, exist_ok=True)
        filepath = os.path.join(output_dir, filename)
        data = {
            '行业新闻': {
                'DIGITIMES': [
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
    crawler = DigitimesNewsCrawler(keyword='EDA')
    news = crawler.crawl(max_pages=1, days=7, keywords=['EDA', 'synopsys'])
    crawler.save_to_json(news)


if __name__ == '__main__':
    main()
