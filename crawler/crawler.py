import asyncio
import aiohttp
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin
import os
import sys
import django
import time
import pickle
from tqdm import tqdm
from django.utils import timezone
from asgiref.sync import sync_to_async

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.settings")
django.setup()

from search_app.models import Page, Index, PageLink
import re
from django.db import transaction

start_urls = [
    "https://gate.ahram.org.eg/",
    "https://english.ahram.org.eg/",
    "https://www.bbc.com/",
    "https://www.cnn.com/",
    "https://en.wikipedia.org/wiki/Main_Page",
    "https://www.imdb.com/",
    "https://www.britannica.com/",
    "https://edition.cnn.com/",
    "https://www.theguardian.com/international",
    "https://www.nytimes.com/",
    "https://www.aljazeera.com/",
    "https://www.nationalgeographic.com/",
    "https://www.techcrunch.com/",
]

max_urls = 400
max_depth = 4
output_folder = "scraped_pages"

ignored_extensions = [
    ".jpg",
    ".jpeg",
    ".png",
    ".gif",
    ".bmp",
    ".svg",
    ".webp",
    ".pdf",
    ".zip",
    ".rar",
]

os.makedirs(output_folder, exist_ok=True)


class WebCrawler:
    def __init__(self, start_urls, max_urls, max_depth, output_folder):
        self.start_urls = start_urls
        self.max_urls = max_urls
        self.max_depth = max_depth
        self.output_folder = output_folder
        self.visited_urls = set()
        self.urls_to_visit = [(url, 0) for url in start_urls]
        self.collected_urls = []

        self.semaphore = asyncio.Semaphore(20) # Limit concurrent requests

    async def fetch(self, session, url):
        # Fetch HTML content of a page safely
        try:
            # Skip unwanted URLs
            if any(
                substr in url
                for substr in ["Special:", "action=", "login", "createaccount"]
            ):
                return None

            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            }
            async with self.semaphore:
                async with session.get(url, headers=headers, timeout=30) as response:
                    if response.status == 200:
                        content_type = response.headers.get("Content-Type", "")
                        if "text/html" in content_type:
                            return await response.text()
                    else:
                        print(f"Non_200 response for {url}: {response.status}")
        except Exception as e:
            print(f"Error fetching {url}: {e}")
        return None

    def should_ignore(self, url):
        # Check if the URL should be ignored based on its extension
        parsed_url = urlparse(url)
        for ext in ignored_extensions:
            if parsed_url.path.lower().endswith(ext):
                return True
        return False

    def extract_links(self, url, html):
        # Extract links from the HTML content
        links = set()
        if not html:
            return links

        soup = BeautifulSoup(html, "html.parser")
        base_domain = urlparse(url).netloc

        for a_tag in soup.find_all("a", href=True):
            href = a_tag["href"]
            if href.startswith("#") or href.startswith("javascript:"):
                continue
            if href.startswith("/"):
                href = urljoin(url, href)
            if href.startswith("http"):
                links.add(href)

        print(f"[DEBUG] Extracted {len(links)} links from {url}")
        return links

    async def save_content(self, url, content, file_number):
        try:
            await sync_to_async(self._sync_save_content)(url, content)
        except Exception as e:
            print(f"Error saving {url} : {e}")

    def _sync_save_content(self, url, content):
        print(f"[DEBUG] Saving content form {url}")
        def get_visible_text(soup):
            # Remove unwanted elements
            for tag in soup(["script", "style", "meta", "noscript", "header", "footer", "nav"]):
                tag.extract()
            return soup.get_text(separator=" ", strip=True)
        # Save the content to DB
        soup = BeautifulSoup(content, "html.parser")
        text_content = get_visible_text(soup)
        title = soup.title.string if soup.title else "No Title"
        
        page, _ = Page.objects.update_or_create(
            url=url,
            defaults={
                "title": title,
                "content": text_content,
                "crawled_at": timezone.now(),
            },
        )

        # Extract links from the content    
        raw_links = set(a.get("href") for a in soup.find_all("a", href=True))
        print(f"[DEBUG] Found {len(raw_links)} raw links in {url}")
        normalized_links = [self.normalize_url(url, link) for link in raw_links]
        links = [link for link in normalized_links if self.is_valid_url(link)]
        print(f"[DEBUG] Normalized to {len(links)} valid links in {url}")

        linked_pages = []
        for link in links:
            page_obj, _ = Page.objects.get_or_create(url=link)
            linked_pages.append(page_obj)

    
        # Index the page content
        self.index_page(page, text_content)
        self.save_links(page, links)

    
    def save_links(self, from_page, outgoing_links):
        print(f"[DEBUG] Saving links from: {from_page.url} - Found {len(outgoing_links)} links")
        if not outgoing_links:
            print(f"[DEBUG] No outgoing links found for {from_page.url}")
            return
        # Save the links to the database
        for url in outgoing_links:
            if not url or not url.startswith("http"):
                continue
            try:
                to_page, _ = Page.objects.get_or_create(url=url)
                link_obj, created = PageLink.objects.get_or_create(from_page=from_page, to_page=to_page)
                if created:
                    print(f"[DEBUG] Created link from {from_page.url} to {to_page.url}")
            except Exception as e:
                print(f"[DEBUG] Error creating link from {from_page.url} to {url}: {e}")



    def is_valid_url(self, url):
        return (
            url.startswith("http")
            and not self.should_ignore(url)
            and not url.startswith("mailto:")
            and not url.startswith("#")
            and not url.startswith("javascript:")
        )
    
    def normalize_url(self, base_url, link):
        # Normalize the URL to ensure it is absolute
        return urljoin(base_url, link)
    
    def save_state(self):
        # Save the state of the crawler
        with open("visited_urls.pkl", "wb") as f:
            pickle.dump(self.visited_urls, f)
        with open("urls_to_visit.pkl", "wb") as f:
            pickle.dump(self.urls_to_visit, f)
        with open("collected_urls.pkl", "wb") as f:
            pickle.dump(self.collected_urls, f)
        print("State saved.")

    def load_state(self):
        # Load the state of the crawler
        if (
            os.path.exists("visited_urls.pkl")
            and os.path.exists("urls_to_visit.pkl")
            and os.path.exists("collected_urls.pkl")
        ):
            with open("visited_urls.pkl", "rb") as f:
                self.visited_urls = pickle.load(f)
            with open("urls_to_visit.pkl", "rb") as f:
                self.urls_to_visit = pickle.load(f)
            with open("collected_urls.pkl", "rb") as f:
                self.collected_urls = pickle.load(f)
            print("State loaded.")

            current_urls = {url for url, depth in self.urls_to_visit}
            for url in self.start_urls:
                if url not in self.visited_urls and url not in current_urls:
                    self.urls_to_visit.append((url, 0))
                    print(f"Added {url} to urls_to_visit.")
        else:
            print("State not found. Starting from scratch.")

    async def crawl(self):
        # Load the state of the crawler
        self.load_state()
        start_time = time.time()
        async with aiohttp.ClientSession() as session:
            with tqdm(
                total=self.max_urls, initial=len(self.collected_urls), desc="Crawling"
            ) as pbar:
                while self.urls_to_visit and len(self.collected_urls) < self.max_urls:
                    current_batch = self.urls_to_visit[:50]
                    self.urls_to_visit = self.urls_to_visit[50:]

                    tasks = [
                        self.process_url(session, url, depth, pbar)
                        for url, depth in current_batch
                    ]
                    await asyncio.gather(*tasks)

                    self.save_state()  # Save the state of the crawler after each batch
        print(
            f"{len(self.collected_urls)} URLs collected in {time.time() - start_time:.2f} seconds."
        )

    async def process_url(self, session, url, depth, pbar):
        # Processing the URL, Extracting the content and saving it, Bringing the content.
        if url in self.visited_urls or len(self.collected_urls) >= self.max_urls:
            return
        
        print(f"Processing {url} at depth {depth}")

        retries = 3
        html = None

        for attempt in range(retries):
            html = await self.fetch(session, url)
            if html:
                break
            else:
                print(f"Retrying {url}... attempt {attempt + 1}")
                await asyncio.sleep(1)  # Wait before retrying

        if not html:
            print(f"Failed to fetch {url} after {retries} attempts.")
            return

        self.visited_urls.add(url)
        self.collected_urls.append(url)
        await self.save_content(
            url,
            html,
            len(self.collected_urls),
        )
        pbar.update(1)

        if depth < self.max_depth:
                new_links = self.extract_links(url, html)
                for link in new_links:
                    if (
                        link not in self.visited_urls
                        and len(self.collected_urls) + len(self.urls_to_visit)
                        < self.max_urls
                    ):
                        self.urls_to_visit.append((link, depth + 1))

    def index_page(self, page: Page, content: str):
        # Indexing the page
        words = re.findall(r"\w+", content.lower())
        index_objects = []

        # Adding words to Index
        with transaction.atomic():  # Ensure concurrency
            for position, word in enumerate(words):
                index_objects.append(Index(page=page, keyword=word, position=position))
            Index.objects.bulk_create(index_objects)


async def main():
    crawler = WebCrawler(
        start_urls=start_urls,
        max_urls=max_urls,
        max_depth=max_depth,
        output_folder=output_folder,
    )
    await crawler.crawl()


if __name__ == "__main__":
    import sys

    if sys.platform.startswith("win"):
        asyncio.set_event_loop_ploicy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())
