# -*- coding: utf-8 -*-
import os
import json
import re
import time
import uuid
import logging
from glob import glob
from datetime import datetime, timedelta
from email.utils import parsedate_to_datetime
from urllib.parse import quote
from xml.etree import ElementTree as ET

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
import urllib3
from bs4 import BeautifulSoup

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class IWenCaiNewsCrawler:
    SEARCH_URL = "https://www.iwencai.com/unifiedwap/search/result"

    def __init__(self, keyword="synopsys"):
        self.keyword = keyword
        self.enable_selenium = True
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Referer': 'https://www.iwencai.com/',
        }
        self.query_candidates = self._build_query_candidates()

    def _build_query_candidates(self):
        keyword = (self.keyword or '').strip()
        candidates = [keyword]
        dedup = []
        seen = set()
        for q in candidates:
            q2 = (q or '').strip()
            if q2 and q2 not in seen:
                seen.add(q2)
                dedup.append(q2)
        return dedup

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

    def _is_keyword_relevant(self, text):
        if not text:
            return False
        t = text.lower()
        keyword = (self.keyword or '').strip().lower()
        if keyword and keyword in t:
            return True
        if keyword == 'synopsys':
            return ('新思科技' in text) or ('synopsys' in t)
        return False

    def _is_real_news_url(self, url):
        u = (url or '').strip()
        if not u.startswith('http'):
            return False
        bad = [
            '/unifiedwap/search/result',
            '/unifiedwap/home/index',
            '/search/result',
            'javascript:',
            '#',
        ]
        ul = u.lower()
        if any(x in ul for x in bad):
            return False
        return True

    def _extract_news_from_html(self, html):
        soup = BeautifulSoup(html, 'html.parser')
        today = datetime.now().strftime('%Y-%m-%d')
        result = []
        seen = set()
        anchors = soup.select('a[href]')
        for a in anchors:
            href = (a.get('href') or '').strip()
            title = a.get_text(' ', strip=True)
            if not href or not title:
                continue
            if href.startswith('//'):
                href = 'https:' + href
            elif href.startswith('/'):
                href = 'https://www.iwencai.com' + href
            if not href.startswith('http'):
                continue
            if not self._is_real_news_url(href):
                continue
            if not self._is_keyword_relevant(title) and not self._is_keyword_relevant(href):
                continue
            key = (title, href)
            if key in seen:
                continue
            seen.add(key)
            result.append({
                'title': title,
                'link': href,
                'date': today,
                'source': '问财网',
            })

        if result:
            return result

        return result

    def _extract_news_from_anchor_pairs(self, pairs):
        today = datetime.now().strftime('%Y-%m-%d')
        result = []
        seen = set()
        for title, href in pairs:
            title = (title or '').strip()
            href = (href or '').strip()
            if not href or not title:
                continue
            if href.startswith('//'):
                href = 'https:' + href
            elif href.startswith('/'):
                href = 'https://www.iwencai.com' + href
            if not href.startswith('http'):
                continue
            if not self._is_real_news_url(href):
                continue
            if not self._is_keyword_relevant(title) and not self._is_keyword_relevant(href):
                continue
            key = (title, href)
            if key in seen:
                continue
            seen.add(key)
            result.append({
                'title': title,
                'link': href,
                'date': today,
                'source': '问财网',
            })
        return result

    def _fetch_html_requests(self, query):
        query_enc = quote(query)
        url = f"{self.SEARCH_URL}?w={query_enc}"
        resp = requests.get(url, headers=self.headers, timeout=15, verify=False)
        if resp.status_code != 200:
            return ''
        resp.encoding = resp.apparent_encoding or 'utf-8'
        return resp.text

    def _create_chrome_driver(self):
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options

        chrome_options = Options()
        chrome_options.add_argument('--headless=new')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_experimental_option('excludeSwitches', ['enable-automation'])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        # 优先使用本地缓存的 chromedriver
        from selenium.webdriver.chrome.service import Service
        local_driver = self._find_local_chromedriver()
        if local_driver:
            try:
                service = Service(local_driver)
                return webdriver.Chrome(service=service, options=chrome_options)
            except Exception:
                pass
        
        # 尝试不指定 service 直接创建
        try:
            return webdriver.Chrome(options=chrome_options)
        except Exception:
            return None

    def _fetch_by_selenium(self, query):
        try:
            from selenium.webdriver.common.by import By
            from selenium.webdriver.support.ui import WebDriverWait
        except Exception:
            return [], ''
        driver = None
        try:
            driver = self._create_chrome_driver()
            if not driver:
                return [], ''
            query_enc = quote(query)
            url = f"{self.SEARCH_URL}?w={query_enc}"
            try:
                driver.set_page_load_timeout(8)
            except Exception:
                pass
            try:
                driver.get(url)
            except Exception:
                pass
            try:
                WebDriverWait(driver, 6).until(lambda x: x.execute_script('return document.readyState') == 'complete')
            except Exception:
                pass
            time.sleep(1)
            for _ in range(2):
                try:
                    driver.execute_script('window.scrollTo(0, document.body.scrollHeight);')
                except Exception:
                    pass
                time.sleep(0.6)
            anchors = driver.find_elements(By.CSS_SELECTOR, 'a[href]')
            pairs = []
            for a in anchors:
                try:
                    title = (a.text or '').strip()
                    href = (a.get_attribute('href') or '').strip()
                except Exception:
                    continue
                if title and href:
                    pairs.append((title, href))
            page_source = driver.page_source or ''
            return pairs, page_source
        except Exception:
            return [], ''
        finally:
            if driver:
                try:
                    driver.quit()
                except Exception:
                    pass

    def _normalize_date(self, value):
        if value is None:
            return ''
        if isinstance(value, (int, float)):
            ts = int(value)
            if ts > 10**12:
                ts = ts // 1000
            if ts > 10**9:
                try:
                    return datetime.fromtimestamp(ts).strftime('%Y-%m-%d')
                except Exception:
                    return ''
            return ''
        text = str(value).strip()
        if not text:
            return ''
        m = re.search(r'(\d{4})[-/.年](\d{1,2})[-/.月](\d{1,2})', text)
        if m:
            try:
                y, mo, d = int(m.group(1)), int(m.group(2)), int(m.group(3))
                return datetime(y, mo, d).strftime('%Y-%m-%d')
            except Exception:
                pass
        try:
            return parsedate_to_datetime(text).strftime('%Y-%m-%d')
        except Exception:
            pass
        return ''

    def _extract_news_from_captured_json(self, captured_payloads, cutoff_date):
        today = datetime.now().strftime('%Y-%m-%d')
        result = []
        seen = set()
        stack = []
        for item in captured_payloads:
            if isinstance(item, dict):
                body = item.get('body')
                if isinstance(body, str):
                    try:
                        body = json.loads(body)
                    except Exception:
                        body = None
                if body is not None:
                    stack.append(body)
        while stack:
            node = stack.pop()
            if isinstance(node, dict):
                title = ''
                for k in ['title', 'newsTitle', 'news_title', 'headline', 'name', 'question', 'title_highlight']:
                    v = node.get(k)
                    if isinstance(v, str) and v.strip():
                        title = BeautifulSoup(v.strip(), 'html.parser').get_text(' ', strip=True)
                        break
                link = ''
                for k in ['link', 'url', 'newsUrl', 'sourceUrl', 'articleUrl', 'share_url']:
                    v = node.get(k)
                    if isinstance(v, str) and v.strip():
                        link = v.strip()
                        break
                if not link:
                    news_id = node.get('news_id') or node.get('newsId')
                    if news_id:
                        link = f"https://www.iwencai.com/unifiedwap/home/index?newsid={news_id}"
                if title and link and link.startswith('http'):
                    if not self._is_real_news_url(link):
                        pass
                    else:
                        if self._is_keyword_relevant(title) or self._is_keyword_relevant(link):
                            date = ''
                            for dk in ['date', 'pubDate', 'publishDate', 'publishTime', 'publish_time', 'time', 'ctime', 'updateTime', 'update_time']:
                                if dk in node:
                                    date = self._normalize_date(node.get(dk))
                                    if date:
                                        break
                            if not date:
                                date = today
                            if date >= cutoff_date:
                                key = (title, link)
                                if key not in seen:
                                    seen.add(key)
                                    result.append({
                                        'title': title,
                                        'link': link,
                                        'date': date,
                                        'source': '问财网',
                                    })
                for v in node.values():
                    if isinstance(v, (dict, list)):
                        stack.append(v)
            elif isinstance(node, list):
                for it in node:
                    if isinstance(it, (dict, list)):
                        stack.append(it)
        return result[:30]

    def _fetch_api_by_selenium(self, query, cutoff_date):
        driver = None
        try:
            driver = self._create_chrome_driver()
            if not driver:
                return []
            inject_script = """
            (function(){
              if(window.__iwencai_capture_installed__) return;
              window.__iwencai_capture_installed__ = true;
              window.__iwencai_capture__ = [];
              var pushPayload = function(url, text){
                try{
                  if(!text || text.length > 600000) return;
                  var j = JSON.parse(text);
                  window.__iwencai_capture__.push({url: url || '', body: j});
                }catch(e){}
              };
              try{
                var _fetch = window.fetch;
                if(_fetch){
                  window.fetch = function(){
                    return _fetch.apply(this, arguments).then(function(resp){
                      try{
                        var c = resp.clone();
                        c.text().then(function(t){ pushPayload(resp.url || '', t); });
                      }catch(e){}
                      return resp;
                    });
                  };
                }
              }catch(e){}
              try{
                var _open = XMLHttpRequest.prototype.open;
                var _send = XMLHttpRequest.prototype.send;
                XMLHttpRequest.prototype.open = function(method, url){
                  this.__iwencai_url__ = url || '';
                  return _open.apply(this, arguments);
                };
                XMLHttpRequest.prototype.send = function(){
                  this.addEventListener('readystatechange', function(){
                    try{
                      if(this.readyState === 4){
                        pushPayload(this.__iwencai_url__ || '', this.responseText || '');
                      }
                    }catch(e){}
                  });
                  return _send.apply(this, arguments);
                };
              }catch(e){}
            })();
            """
            try:
                driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {"source": inject_script})
            except Exception:
                pass
            query_enc = quote(query)
            url = f"{self.SEARCH_URL}?w={query_enc}"
            try:
                driver.set_page_load_timeout(10)
            except Exception:
                pass
            try:
                driver.get(url)
            except Exception:
                pass
            for _ in range(8):
                time.sleep(0.7)
                try:
                    driver.execute_script('window.scrollTo(0, document.body.scrollHeight);')
                except Exception:
                    pass
            captured = []
            try:
                captured = driver.execute_script("return window.__iwencai_capture__ || [];")
            except Exception:
                captured = []
            return self._extract_news_from_captured_json(captured, cutoff_date)
        except Exception:
            return []
        finally:
            if driver:
                try:
                    driver.quit()
                except Exception:
                    pass

    def _fetch_news_from_iwencai_stream_search(self, query, cutoff_date):
        stream_url = "https://www.iwencai.com/gateway/comprehensive/rag/v1/stream/search"
        headers = {
            'User-Agent': self.headers['User-Agent'],
            'Content-Type': 'application/json',
            'Accept': 'text/event-stream',
            'X-Comefrom': 'iwc',
            'X-Source': 'Ths_iwencai_Xuangu',
            'Referer': f"{self.SEARCH_URL}?w={quote(query)}",
        }
        payload = {
            'question': f'请仅列出5条与{query}相关的新闻标题，每行一条，不要解释',
            'query': query,
            'channels': ['news'],
            'qid': (uuid.uuid4().hex + uuid.uuid4().hex)[:32],
            'scroll_mode': 'web',
            'platform': 'pc',
        }
        rich_chunks = []
        try:
            resp = requests.post(
                stream_url,
                headers=headers,
                json=payload,
                timeout=(10, 3),
                verify=False,
                stream=True
            )
            if resp.status_code != 200:
                return []
            begin_at = time.time()
            data_line_count = 0
            try:
                for line in resp.iter_lines(decode_unicode=False):
                    if time.time() - begin_at > 8:
                        break
                    if not line or not line.startswith(b'data:'):
                        continue
                    data_line_count += 1
                    try:
                        obj = json.loads(line[5:].decode('utf-8', 'ignore'))
                    except Exception:
                        continue
                    section = obj.get('section') or {}
                    rich_text = section.get('rich_text')
                    if isinstance(rich_text, str) and rich_text.strip():
                        rich_chunks.append(rich_text)
                    if section.get('is_last') is True and data_line_count > 20:
                        break
                    if data_line_count >= 120:
                        break
            except Exception:
                pass
            try:
                resp.close()
            except Exception:
                pass
            if not rich_chunks:
                return []
            text = ''.join(rich_chunks)
            text = text.replace('\\n', '\n')
            text = BeautifulSoup(text, 'html.parser').get_text('\n', strip=True)
            text = text.replace('```', '').strip()
            links = re.findall(r'https?://[^\s)>\]"]+', text)
            real_links = []
            for u in links:
                if self._is_real_news_url(u) and u not in real_links:
                    real_links.append(u)
            if not real_links:
                return []
            title_candidates = []
            quoted = re.findall(r'文档\^?\d+中提到[:：]?[“"]([^”"\n]{12,200})[”"]', text)
            title_candidates.extend(quoted)
            en_hits = re.findall(r'(Synopsys[^。！？\n]{12,200})', text, flags=re.I)
            zh_hits = re.findall(r'(新思科技[^。！？\n]{8,120})', text)
            title_candidates.extend(en_hits)
            title_candidates.extend(zh_hits)
            for ln in text.splitlines():
                ln2 = ln.strip(' -\t\r\n')
                if len(ln2) < 16 or len(ln2) > 160:
                    continue
                if '“' in ln2 and ('文档' in ln2 or '提到' in ln2):
                    ln3 = ln2.split('“', 1)[1].strip(' ”"')
                    if len(ln3) >= 10:
                        title_candidates.append(ln3)
                if self._is_keyword_relevant(ln2):
                    title_candidates.append(ln2)
            today = datetime.now().strftime('%Y-%m-%d')
            result = []
            seen = set()
            idx = 0
            for title in title_candidates:
                title = re.sub(r'\s+', ' ', title).strip(' ，。;；')
                if not title:
                    continue
                if any(x in title for x in ['我现在需要', '根据原则', '不能编造', '用户的问题', '查看提供的文档', '文档编号', '文档列表', '相关信息，或者可能']):
                    continue
                if '文档' in title and not (title.lower().startswith('synopsys') or title.startswith('新思科技')):
                    continue
                if not self._is_keyword_relevant(title):
                    continue
                if idx >= len(real_links):
                    break
                link = real_links[idx]
                idx += 1
                key = (title, link)
                if key in seen:
                    continue
                seen.add(key)
                result.append({
                    'title': title,
                    'link': link,
                    'date': today,
                    'source': '问财网',
                })
                if len(result) >= 10:
                    break
            return [n for n in result if n.get('date', '') >= cutoff_date]
        except Exception:
            return []

    def _parse_pubdate(self, pub_date_text):
        if not pub_date_text:
            return ''
        try:
            dt = parsedate_to_datetime(pub_date_text)
            return dt.strftime('%Y-%m-%d')
        except Exception:
            return ''

    def _fetch_fallback_rss(self, query, cutoff_date):
        rss_url = f"https://www.bing.com/news/search?format=rss&q={quote(query)}&setmkt=en-US&setlang=en-US&qft=sortbydate%3d%221%22&form=YFNR"
        try:
            resp = requests.get(
                rss_url,
                headers={
                    'User-Agent': self.headers['User-Agent'],
                    'Accept': 'application/rss+xml,application/xml,text/xml;q=0.9,*/*;q=0.8',
                    'Referer': 'https://www.bing.com/'
                },
                timeout=12,
                verify=False,
                allow_redirects=True
            )
            text = (resp.text or '').lstrip()
            if not (text.startswith('<?xml') or text.startswith('<rss')):
                soup = BeautifulSoup(resp.text, 'html.parser')
                today = datetime.now().strftime('%Y-%m-%d')
                html_items = []
                seen = set()
                for a in soup.select('a[href]'):
                    title = a.get_text(' ', strip=True)
                    link = (a.get('href') or '').strip()
                    if not title or not link:
                        continue
                    if link.startswith('/'):
                        link = 'https://www.bing.com' + link
                    if not link.startswith('http'):
                        continue
                    if not self._is_keyword_relevant(title) and query.lower() not in title.lower():
                        continue
                    key = (title, link)
                    if key in seen:
                        continue
                    seen.add(key)
                    html_items.append({
                        'title': title,
                        'link': link,
                        'date': today,
                        'source': '问财网',
                    })
                return html_items[:8]
            root = ET.fromstring(text)
            items = root.findall('./channel/item')
            result = []
            seen = set()
            for item in items:
                title = (item.findtext('title') or '').strip()
                link = (item.findtext('link') or '').strip()
                pub_date = (item.findtext('pubDate') or '').strip()
                date = self._parse_pubdate(pub_date)
                if not title or not link or not date:
                    continue
                if date < cutoff_date:
                    continue
                if not self._is_keyword_relevant(title):
                    continue
                key = (title, link)
                if key in seen:
                    continue
                seen.add(key)
                result.append({
                    'title': title,
                    'link': link,
                    'date': date,
                    'source': '问财网',
                })
            return result[:8]
        except Exception:
            return []
        return []

    def _fetch_google_rss(self, query, cutoff_date):
        rss_url = f"https://news.google.com/rss/search?q={quote(query)}&hl=en-US&gl=US&ceid=US:en"
        try:
            resp = requests.get(
                rss_url,
                headers={
                    'User-Agent': self.headers['User-Agent'],
                    'Accept': 'application/rss+xml,application/xml,text/xml;q=0.9,*/*;q=0.8'
                },
                timeout=12,
                verify=False
            )
            text = (resp.text or '').lstrip()
            if not (text.startswith('<?xml') or text.startswith('<rss')):
                return []
            root = ET.fromstring(text)
            items = root.findall('./channel/item')
            result = []
            seen = set()
            for item in items:
                title = (item.findtext('title') or '').strip()
                link = (item.findtext('link') or '').strip()
                pub_date = (item.findtext('pubDate') or '').strip()
                date = self._parse_pubdate(pub_date)
                if not title or not link or not date:
                    continue
                if date < cutoff_date:
                    continue
                if not self._is_keyword_relevant(title):
                    continue
                key = (title, link)
                if key in seen:
                    continue
                seen.add(key)
                result.append({
                    'title': title,
                    'link': link,
                    'date': date,
                    'source': '问财网',
                })
                if len(result) >= 8:
                    break
            return result
        except Exception:
            return []

    def _fetch_bing_news_html(self, query, cutoff_date):
        url = f"https://www.bing.com/news/search?q={quote(query)}&setlang=en-US&qft=sortbydate%3d%221%22"
        def parse_html(html_text):
            soup = BeautifulSoup(html_text, 'html.parser')
            parsed = []
            seen_local = set()
            today_local = datetime.now().strftime('%Y-%m-%d')
            for a in soup.select('a[href]'):
                title = a.get_text(' ', strip=True)
                link = (a.get('href') or '').strip()
                if not title or not link:
                    continue
                if link.startswith('//'):
                    link = 'https:' + link
                if not link.startswith('http'):
                    continue
                if 'bing.com/ck/a' in link or 'javascript:' in link:
                    continue
                if not self._is_keyword_relevant(title):
                    continue
                if today_local < cutoff_date:
                    continue
                key = (title, link)
                if key in seen_local:
                    continue
                seen_local.add(key)
                parsed.append({
                    'title': title,
                    'link': link,
                    'date': today_local,
                    'source': '问财网',
                })
                if len(parsed) >= 12:
                    break
            return parsed
        try:
            for _ in range(3):
                resp = requests.get(
                    url,
                    headers={
                        'User-Agent': self.headers['User-Agent'],
                        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                        'Referer': 'https://www.bing.com/'
                    },
                    timeout=12,
                    verify=False
                )
                if resp.status_code == 200:
                    result = parse_html(resp.text or '')
                    if result:
                        return result
                resp2 = requests.get(url, timeout=12, verify=False)
                if resp2.status_code == 200:
                    result2 = parse_html(resp2.text or '')
                    if result2:
                        return result2
                time.sleep(0.6)
            return []
        except Exception:
            return []

    def _fetch_bing_web_news(self, query, cutoff_date):
        url = f"https://www.bing.com/search?q={quote(query + ' news')}"
        try:
            resp = requests.get(url, timeout=12, verify=False)
            if resp.status_code != 200:
                return []
            soup = BeautifulSoup(resp.text, 'html.parser')
            result = []
            seen = set()
            today = datetime.now().strftime('%Y-%m-%d')
            news_domains = ['msn.com', 'reuters.com', 'yahoo.com', 'forbes.com', 'fool.com', 'benzinga.com', 'investing.com']
            for a in soup.select('li.b_algo h2 a[href]'):
                title = a.get_text(' ', strip=True)
                link = (a.get('href') or '').strip()
                if not title or not link or not link.startswith('http'):
                    continue
                if not self._is_keyword_relevant(title) and not self._is_keyword_relevant(link):
                    continue
                link_l = link.lower()
                title_l = title.lower()
                is_news_like = ('news' in title_l) or ('stock' in title_l) or ('shares' in title_l) or ('earnings' in title_l) or ('stake' in title_l) or any(d in link_l for d in news_domains) or ('/news' in link_l)
                if not is_news_like:
                    continue
                if today < cutoff_date:
                    continue
                key = (title, link)
                if key in seen:
                    continue
                seen.add(key)
                result.append({
                    'title': title,
                    'link': link,
                    'date': today,
                    'source': '问财网',
                })
                if len(result) >= 10:
                    break
            return result
        except Exception:
            return []

    def _fetch_synopsys_official_news(self, cutoff_date):
        url = "https://news.synopsys.com/"
        try:
            resp = requests.get(
                url,
                headers={
                    'User-Agent': self.headers['User-Agent'],
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
                },
                timeout=15,
                verify=False
            )
            if resp.status_code != 200:
                return []
            soup = BeautifulSoup(resp.text, 'html.parser')
            result = []
            seen = set()
            for a in soup.select('a[href]'):
                title = a.get_text(' ', strip=True)
                link = (a.get('href') or '').strip()
                if not title or not link:
                    continue
                if link.startswith('/'):
                    link = 'https://news.synopsys.com' + link
                if not link.startswith('http'):
                    continue
                if 'news.synopsys.com/' not in link:
                    continue
                if not self._is_keyword_relevant(title):
                    continue
                m = re.search(r'/(\d{4})-(\d{2})-(\d{2})-', link)
                if m:
                    date = f"{m.group(1)}-{m.group(2)}-{m.group(3)}"
                else:
                    date = datetime.now().strftime('%Y-%m-%d')
                if date < cutoff_date:
                    continue
                key = (title, link)
                if key in seen:
                    continue
                seen.add(key)
                result.append({
                    'title': title,
                    'link': link,
                    'date': date,
                    'source': '问财网',
                })
                if len(result) >= 12:
                    break
            return result
        except Exception:
            return []

    def crawl(self, max_pages=1, days=7, min_content_length=0):
        cutoff_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
        all_news = []
        print(f"\n正在爬取 问财网（关键词: {self.keyword}，最近 {days} 天）...")
        attempts = self.query_candidates[:max(1, max_pages)]
        for idx, query in enumerate(attempts, 1):
            page_news = []
            try:
                html = self._fetch_html_requests(query)
                if html:
                    page_news = self._extract_news_from_html(html)
            except Exception:
                page_news = []
            if not page_news:
                page_news = self._fetch_news_from_iwencai_stream_search(query, cutoff_date)
            if not page_news and self.enable_selenium:
                page_news = self._fetch_api_by_selenium(query, cutoff_date)
            if not page_news and self.enable_selenium:
                anchor_pairs, rendered_html = self._fetch_by_selenium(query)
                if anchor_pairs:
                    page_news = self._extract_news_from_anchor_pairs(anchor_pairs)
                if not page_news and rendered_html:
                    page_news = self._extract_news_from_html(rendered_html)
            if not page_news:
                print(f"  第 {idx} 次检索（{query}）没有新闻")
                continue
            page_news = [n for n in page_news if n.get('date', '') >= cutoff_date]
            all_news.extend(page_news)
            print(f"  第 {idx} 次检索（{query}）: {len(page_news)} 条新闻")
            if len(all_news) >= 5:
                break

        unique_news = []
        seen_keys = set()
        for news in all_news:
            title = news.get('title', '')
            link = news.get('link', '')
            key = (title, link)
            if link and key not in seen_keys:
                seen_keys.add(key)
                unique_news.append(news)

        if min_content_length > 0 and unique_news:
            print(f"  正在获取新闻内容并过滤（>={min_content_length}字）...")
            filtered = []
            for n in unique_news:
                content = self.fetch_news_content(n['link'])
                if content and len(content) >= min_content_length:
                    n['content'] = content
                    filtered.append(n)
            unique_news = filtered

        print(f"  共获取 {len(unique_news)} 条新闻")
        return unique_news

    def fetch_news_content(self, url):
        try:
            resp = requests.get(
                url,
                headers={
                    'User-Agent': self.headers['User-Agent'],
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                    'Accept-Language': self.headers['Accept-Language'],
                    'Referer': 'https://www.iwencai.com/'
                },
                timeout=15,
                verify=False
            )
            if resp.status_code != 200:
                return ''
            resp.encoding = resp.apparent_encoding or 'utf-8'
            soup = BeautifulSoup(resp.text, 'html.parser')
            for t in soup(['script', 'style', 'noscript']):
                t.decompose()
            text = soup.get_text('\n', strip=True)
            lines = [ln.strip() for ln in text.splitlines() if ln and len(ln.strip()) > 8]
            content = '\n'.join(lines[:120])
            return content
        except Exception:
            return ''

    def save_to_json(self, news_list, filename='iwencai_news.json'):
        output_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'json')
        os.makedirs(output_dir, exist_ok=True)
        filepath = os.path.join(output_dir, filename)
        data = {
            '行业新闻': {
                '问财网': [
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
    crawler = IWenCaiNewsCrawler(keyword="synopsys")
    news_list = crawler.crawl(max_pages=1, days=7, min_content_length=0)
    crawler.save_to_json(news_list)


if __name__ == '__main__':
    main()
