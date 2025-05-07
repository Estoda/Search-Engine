import os
import django
import sys
import time

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.settings")
django.setup()

from search_app.models import Page, PageLink
from collections import defaultdict

DAMPING_FACTOR = 0.85
ITERATIONS = 100

def compute_pagerank():
    start_time = time.time()

    print("[INFO] Fetching pages from database...")
    pages= Page.objects.exclude(title__isnull=True).exclude(title__exact="").exclude(content__isnull=True).exclude(content__exact="") 
    page_ids = [page.id for page in pages]
    page_index = {page.id: i for i, page in enumerate(pages)}
    N = len(page_ids)
    print(f"[INFO] Total pages: {N}")

    # Initialize rank for each page
    ranks = [1.0 / N] * N

    # Build graph: page_id -> list of to_page_id
    outgoing_links = defaultdict(list)
    incoming_links = defaultdict(list)

    print("[INFO] Building link graph...")
    for link in PageLink.objects.all():
        if link.from_page_id != link.to_page_id:  # Avoid self-loops
            outgoing_links[link.from_page_id].append(link.to_page_id)
            incoming_links[link.to_page_id].append(link.from_page_id)

    print("[INFO] Starting PageRank iterations...")
    for it in range(ITERATIONS):
        new_ranks = [0.0] * N
        for page in pages:
            i = page_index[page.id]
            rank_sum = 0.0
            for in_id in incoming_links[page.id]:
                j = page_index[in_id]
                out_degree = len(outgoing_links[in_id])
                if out_degree > 0:
                    rank_sum += ranks[j] / out_degree

            new_ranks[i] = (1 - DAMPING_FACTOR) / N + DAMPING_FACTOR * rank_sum

        ranks = new_ranks
        if (it + 1) % 10 == 0 or it == ITERATIONS - 1:
            print(f"[INFO] Iteration {it + 1}/{ITERATIONS} complete")

    print("[INFO] Normalizing and saving ranks to database...")
    min_rank = min(ranks)
    max_rank = max(ranks)

    for i, page in enumerate(pages):
        normalized_rank = (ranks[i] - min_rank) / (max_rank - min_rank) if max_rank > min_rank else 0.0
        normalized_rank = 0.01 + (normalized_rank * (1 - 0.01))  # Scale to [0.01, 1]
        page.rank = normalized_rank
        page.save()

    elapsed = time.time() - start_time
    print(f"[DONE] PageRank computation completed in {elapsed:.2f} seconds.")

if __name__ == "__main__":
    compute_pagerank()
