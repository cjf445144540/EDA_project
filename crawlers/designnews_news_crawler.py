# -*- coding: utf-8 -*-
import os
import json
import re
from urllib.parse import quote, urlparse, parse_qs, unquote
from xml.etree import ElementTree as ET
from datetime import datetime, timedelta
from email.utils import parsedate_to_datetime

import requests
import urllib3
from bs4 import BeautifulSoup

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class DesignNewsCrawler:
    _shared_content_hints = {}

    def __init__(self, keyword="EDA"):
        self.keyword = keyword
        self.content_hints = self.__class__._shared_content_hints
        self.rss_headers = {
            'User-Agent': 'Mozilla/5.0',
            'Accept': 'application/rss+xml,application/xml,text/xml;q=0.9,*/*;q=0.8',
        }
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Referer': 'https://www.designnews.com/',
        }
        self.jina_headers = {
            'User-Agent': 'Mozilla/5.0',
            'Accept': 'text/plain,text/markdown;q=0.9,*/*;q=0.8',
        }

    def _normalize_link(self, link):
        try:
            sp = urlparse((link or '').strip())
            return f"{sp.scheme}://{sp.netloc}{sp.path}" if sp.scheme and sp.netloc else (link or '').strip()
        except Exception:
            return (link or '').strip()

    def _clean_summary(self, text):
        raw = BeautifulSoup((text or '').strip(), 'html.parser').get_text(' ', strip=True)
        return ' '.join(raw.split())

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
        if 'synopsys' in [k.lower() for k in keywords]:
            return ('synopsys' in t) or ('新思' in text)
        if 'eda' in [k.lower() for k in keywords]:
            return ('eda' in t) or ('electronic design automation' in t)
        return False

    def _parse_rss_date(self, date_str):
        try:
            dt = parsedate_to_datetime(date_str)
            return dt.strftime('%Y-%m-%d')
        except Exception:
            pass
        m = re.search(r'(\d{1,2})\s+(\w{3})\s+(\d{4})', date_str or '')
        if not m:
            return ''
        day, mon, year = m.groups()
        mon_map = {
            'Jan': '01', 'Feb': '02', 'Mar': '03', 'Apr': '04',
            'May': '05', 'Jun': '06', 'Jul': '07', 'Aug': '08',
            'Sep': '09', 'Oct': '10', 'Nov': '11', 'Dec': '12'
        }
        return f"{year}-{mon_map.get(mon, '01')}-{day.zfill(2)}"

    def _decode_bing_link(self, link):
        try:
            if 'bing.com/news/apiclick' not in (link or '').lower():
                return (link or '').strip()
            q = parse_qs(urlparse(link).query)
            target = q.get('url', [''])[0]
            target = unquote(target).strip()
            return target or (link or '').strip()
        except Exception:
            return (link or '').strip()

    def _is_news_like_link(self, link):
        u = (link or '').lower()
        if 'designnews.com' not in u:
            return False
        bad_parts = ['/author/', '/industry/', '/about', '/contact', '/tag/', '/topic/', '/events']
        if any(x in u for x in bad_parts):
            return False
        return True

    def _extract_from_html_search(self, html, cutoff_date):
        out = []
        seen = set()
        soup = BeautifulSoup(html or '', 'html.parser')
        for a in soup.find_all('a', href=True):
            raw = (a.get('href') or '').strip()
            if not raw:
                continue
            if raw.startswith('/news/apiclick'):
                raw = 'https://www.bing.com' + raw
            link = self._decode_bing_link(raw)
            if not self._is_news_like_link(link):
                continue
            title = ' '.join((a.get_text(' ', strip=True) or '').split())
            if len(title) < 8:
                continue
            key = f"{title}|{link}"
            if key in seen:
                continue
            seen.add(key)
            out.append({
                'title': title,
                'link': link,
                'date': '' if cutoff_date else '',
                'source': 'Design News',
            })
        return out

    def _fallback_seed_news(self):
        return [
            {
                'title': 'Data Analytics Becomes Staple of New EDA Tools',
                'link': 'https://www.designnews.com/design-software/data-analytics-becomes-staple-of-new-eda-tools',
                'date': '',
                'source': 'Design News',
            },
            {
                'title': 'EDA Analytics Tool Boosts SoC Design Productivity',
                'link': 'https://www.designnews.com/design-software/eda-analytics-tool-boosts-soc-design-productivity',
                'date': '',
                'source': 'Design News',
            },
            {
                'title': 'New Synopsys CEO Says Ansys Merger Gives Engineers Seamless Design Path',
                'link': 'https://www.designnews.com/electronics/new-synopsys-ceo-says-ansys-merger-gives-engineers-seamless-design-path',
                'date': '',
                'source': 'Design News',
            },
        ]

    def _fetch_rss(self, keyword, cutoff_date):
        queries = [
            f"site:designnews.com {keyword}",
            f"site:designnews.com {keyword} EDA",
            f"site:designnews.com {keyword} synopsys",
        ]
        urls = [
            f"https://www.bing.com/news/search?q={quote(q)}&format=rss&setmkt=en-US&setlang=en-US&qft=sortbydate%3d%221%22&form=YFNR"
            for q in queries
        ]
        out = []
        seen = set()
        for url in urls:
            try:
                resp = requests.get(
                    url,
                    headers=self.rss_headers,
                    timeout=12,
                    verify=False,
                    allow_redirects=True
                )
                txt = (resp.text or '').strip()
                if not txt:
                    continue
                if ('<rss' in txt[:240].lower()) or ('<?xml' in txt[:240].lower()):
                    root = ET.fromstring(txt)
                    items = root.findall('./channel/item')
                    for item in items:
                        title = (item.findtext('title') or '').strip()
                        link = self._decode_bing_link((item.findtext('link') or '').strip())
                        if not title or not link:
                            continue
                        if not self._is_news_like_link(link):
                            continue
                        date = self._parse_rss_date((item.findtext('pubDate') or '').strip())
                        if cutoff_date and date and date < cutoff_date:
                            continue
                        key = f"{title}|{link}"
                        if key in seen:
                            continue
                        seen.add(key)
                        summary = self._clean_summary(item.findtext('description') or '')
                        out.append({
                            'title': title,
                            'link': link,
                            'date': date,
                            'source': 'Design News',
                            'summary': summary,
                        })
                        if summary:
                            self.content_hints[self._normalize_link(link)] = summary
                else:
                    for n in self._extract_from_html_search(txt, cutoff_date):
                        key = f"{n.get('title', '')}|{n.get('link', '')}"
                        if key in seen:
                            continue
                        seen.add(key)
                        out.append(n)
            except Exception:
                continue
        return out

    def _fetch_bing_summary_by_url(self, url):
        try:
            p = urlparse((url or '').strip())
            slug = (p.path.split('/')[-1] if p.path else '').replace('-', ' ').strip()
            if not slug:
                return ''
            query = f"site:designnews.com {slug}"
            rss_url = f"https://www.bing.com/news/search?q={quote(query)}&format=rss&setmkt=en-US&setlang=en-US&qft=sortbydate%3d%221%22&form=YFNR"
            resp = requests.get(
                rss_url,
                headers=self.rss_headers,
                timeout=5,
                verify=False,
                allow_redirects=True
            )
            if resp.status_code != 200 or not (resp.text or '').strip():
                return ''
            rss_text = resp.text or ''
            soup = BeautifulSoup(rss_text, 'xml')
            items = soup.find_all('item')
            best = ''
            best_score = -1
            for item in items[:8]:
                link = self._decode_bing_link((item.find('link').get_text(strip=True) if item.find('link') else '').strip())
                desc_raw = (item.find('description').get_text(strip=True) if item.find('description') else '').strip()
                if not desc_raw:
                    continue
                desc = BeautifulSoup(desc_raw, 'html.parser').get_text(' ', strip=True)
                desc = ' '.join((desc or '').split())
                score = len(desc)
                if link and 'designnews.com' in link.lower():
                    score += 1000
                    if p.path and p.path.lower() in link.lower():
                        score += 1000
                if score > best_score:
                    best_score = score
                    best = desc
            if best:
                return best
            channel = (p.path.split('/')[1] if len(p.path.split('/')) > 1 else '').replace('-', ' ').strip()
            if not channel:
                return ''
            query2 = f"site:designnews.com {channel}"
            rss_url2 = f"https://www.bing.com/news/search?q={quote(query2)}&format=rss&setmkt=en-US&setlang=en-US&qft=sortbydate%3d%221%22&form=YFNR"
            resp2 = requests.get(
                rss_url2,
                headers=self.rss_headers,
                timeout=5,
                verify=False,
                allow_redirects=True
            )
            txt2 = resp2.text or ''
            if not (('<rss' in txt2[:240].lower()) or ('<?xml' in txt2[:240].lower())):
                return ''
            root2 = ET.fromstring(txt2)
            slug_tokens = {t for t in re.findall(r'[a-z0-9]+', slug.lower()) if len(t) > 2}
            best2 = ''
            best2_score = -1
            for item in root2.findall('./channel/item')[:20]:
                title_text = (item.findtext('title') or '').lower()
                desc = self._clean_summary(item.findtext('description') or '')
                if not desc:
                    continue
                title_tokens = {t for t in re.findall(r'[a-z0-9]+', title_text) if len(t) > 2}
                overlap = len(slug_tokens & title_tokens)
                score = overlap * 100 + len(desc)
                if score > best2_score:
                    best2_score = score
                    best2 = desc
            return best2
        except Exception:
            return ''

    def _fetch_bing_summary_by_title(self, title, expect_link=''):
        try:
            query = f"site:designnews.com {title}"
            rss_url = f"https://www.bing.com/news/search?q={quote(query)}&format=rss&setmkt=en-US&setlang=en-US&qft=sortbydate%3d%221%22&form=YFNR"
            resp = requests.get(
                rss_url,
                headers=self.rss_headers,
                timeout=8,
                verify=False,
                allow_redirects=True
            )
            if resp.status_code != 200 or not (resp.text or '').strip():
                return ''
            rss_text = resp.text or ''
            soup = BeautifulSoup(rss_text, 'xml')
            items = soup.find_all('item')
            expected = self._normalize_link(expect_link)
            best = ''
            best_score = -1
            for item in items[:8]:
                desc = self._clean_summary(item.find('description').get_text(strip=True) if item.find('description') else '')
                if not desc:
                    continue
                link = self._normalize_link(self._decode_bing_link((item.find('link').get_text(strip=True) if item.find('link') else '').strip()))
                score = len(desc)
                if link and 'designnews.com' in link.lower():
                    score += 1000
                if expected and link and expected == link:
                    score += 2000
                if score > best_score:
                    best_score = score
                    best = desc
            return best
        except Exception:
            return ''

    def _fetch_topic_summary(self, target_title):
        target = (target_title or '').lower()
        if not target:
            return ''
        token_set = {t for t in re.findall(r'[a-z0-9]+', target) if len(t) > 2}
        if not token_set:
            return ''
        topics = ['EDA', 'synopsys', 'design software']
        best = ''
        best_score = -1
        for topic in topics:
            try:
                query = f"site:designnews.com {topic}"
                rss_url = f"https://www.bing.com/news/search?q={quote(query)}&format=rss&setmkt=en-US&setlang=en-US&qft=sortbydate%3d%221%22&form=YFNR"
                resp = requests.get(rss_url, headers=self.rss_headers, timeout=8, verify=False, allow_redirects=True)
                txt = (resp.text or '')
                if not (('<rss' in txt[:240].lower()) or ('<?xml' in txt[:240].lower())):
                    continue
                root = ET.fromstring(txt)
                for item in root.findall('./channel/item')[:20]:
                    it_title = (item.findtext('title') or '').strip().lower()
                    if not it_title:
                        continue
                    it_tokens = {t for t in re.findall(r'[a-z0-9]+', it_title) if len(t) > 2}
                    overlap = len(token_set & it_tokens)
                    if overlap <= 0:
                        continue
                    desc = self._clean_summary(item.findtext('description') or '')
                    if not desc:
                        continue
                    score = overlap * 100 + len(desc)
                    if score > best_score:
                        best_score = score
                        best = desc
            except Exception:
                continue
        return best

    def crawl(self, max_pages=1, days=7, min_content_length=0, keywords=None):
        kw_list = self._build_keywords(keywords)
        cutoff_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
        print(f"\n正在爬取 Design News（关键词: {', '.join(kw_list)}，最近 {days} 天）...")
        all_news = []
        seen = set()
        for kw in kw_list:
            try:
                news = self._fetch_rss(kw, cutoff_date)
            except Exception:
                news = []
            page_count = 0
            for n in news:
                title = n.get('title', '')
                link = n.get('link', '')
                if not title or not link:
                    continue
                if not self._is_keyword_relevant(title, kw_list):
                    continue
                if link in seen:
                    continue
                seen.add(link)
                hint = self._clean_summary(n.get('summary', ''))
                if len(hint) >= 60:
                    self.content_hints[self._normalize_link(link)] = hint
                all_news.append(n)
                page_count += 1
            print(f"  关键词 {kw}: {page_count} 条新闻")

        if not all_news:
            print("  最近时间窗内未命中，回退为全量时间检索...")
            for kw in kw_list:
                try:
                    news = self._fetch_rss(kw, '')
                except Exception:
                    news = []
                page_count = 0
                for n in news:
                    title = n.get('title', '')
                    link = n.get('link', '')
                    if not title or not link:
                        continue
                    if not self._is_keyword_relevant(title, kw_list):
                        continue
                    if link in seen:
                        continue
                    seen.add(link)
                    hint = self._clean_summary(n.get('summary', ''))
                    if len(hint) >= 60:
                        self.content_hints[self._normalize_link(link)] = hint
                    all_news.append(n)
                    page_count += 1
                print(f"  关键词 {kw}（全量）: {page_count} 条新闻")

        if not all_news:
            print("  在线检索未命中，回退到站点已知新闻位置...")
            for n in self._fallback_seed_news():
                title = n.get('title', '')
                link = n.get('link', '')
                if not title or not link:
                    continue
                if not self._is_keyword_relevant(title, kw_list):
                    continue
                if link in seen:
                    continue
                seen.add(link)
                all_news.append(n)

        all_news.sort(key=lambda x: x.get('date', ''), reverse=True)
        if all_news:
            if min_content_length > 0:
                print(f"  正在获取新闻内容并过滤（>={min_content_length}字）...")
            else:
                print("  正在获取新闻内容...")
            filtered = []
            for n in all_news:
                content = self.fetch_news_content(n.get('link', ''))
                if content:
                    n['content'] = content
                if min_content_length <= 0 or (content and len(content) >= min_content_length):
                    filtered.append(n)
            all_news = filtered
        print(f"  共获取 {len(all_news)} 条新闻")
        return all_news

    def fetch_news_content(self, url):
        if not url:
            return ''
        normalized_url = self._normalize_link(url)
        hint = self.content_hints.get(normalized_url, '')
        if hint and len(hint) >= 100:
            return hint

        def extract_from_jina_markdown(md_text):
            """从 Jina Reader 返回的 Markdown 中提取文章正文"""
            if not md_text:
                return ''
            lines = md_text.splitlines()
            
            # 收集有效的文章段落
            out = []
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                # 跳过短行
                if len(line) < 80:
                    continue
                # 跳过图片
                if line.startswith('!['):
                    continue
                # 跳过纯链接行
                if line.startswith('[') and (line.endswith(')') or '](' in line):
                    continue
                # 跳过包含 URL 的行
                if 'http://' in line or 'https://' in line:
                    continue
                # 跳过列表项链接
                if line.startswith('*   ['):
                    continue
                # 跳过导航/元数据行
                if any(x in line.lower() for x in ['informa plc', 'cookie', 'privacy', 'terms of', 'copyright', 'registered office']):
                    continue
                # 跳过作者行
                if line.startswith('by[') or line.startswith('By['):
                    continue
                # 处理列表项（可能是文章要点）
                if line.startswith('*   '):
                    line = line[4:].strip()
                    if len(line) < 50:
                        continue
                # 添加有效段落
                out.append(line)
                if len(out) >= 30:
                    break
            
            if out:
                return '\n'.join(out)
            return ''

        # 方法1: 从 Bing 摘要获取（更稳定）
        try:
            summary = self._fetch_bing_summary_by_url(url)
            if summary and len(summary) >= 60:
                self.content_hints[normalized_url] = summary
                return summary
        except Exception:
            pass

        # 方法2: 按标题搜索 Bing
        try:
            p = urlparse(url)
            slug = (p.path.split('/')[-1] if p.path else '').replace('-', ' ').strip()
            if slug:
                summary = self._fetch_bing_summary_by_title(slug, url)
                if summary and len(summary) >= 60:
                    self.content_hints[normalized_url] = summary
                    return summary
        except Exception:
            pass

        # 方法3: 使用 Jina Reader API（备选，可能超时）
        try:
            jina_url = f"https://r.jina.ai/{url}"
            resp = requests.get(
                jina_url,
                headers=self.jina_headers,
                timeout=20,
                verify=False,
                allow_redirects=True,
                proxies={'http': None, 'https': None}
            )
            if resp.status_code == 200 and resp.text:
                content = extract_from_jina_markdown(resp.text)
                if content and len(content) >= 100:
                    self.content_hints[normalized_url] = content
                    return content
        except Exception:
            pass

        hint = self.content_hints.get(normalized_url, '')
        return hint if len(hint) >= 60 else ''

    def save_to_json(self, news_list, filename='designnews_news.json'):
        output_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'json')
        os.makedirs(output_dir, exist_ok=True)
        filepath = os.path.join(output_dir, filename)
        data = {
            '行业新闻': {
                'Design News': [
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
    crawler = DesignNewsCrawler(keyword='EDA')
    news = crawler.crawl(days=7, keywords=['EDA', 'synopsys'])
    crawler.save_to_json(news)


if __name__ == '__main__':
    main()
