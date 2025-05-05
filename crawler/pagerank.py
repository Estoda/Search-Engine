import os
import django
import sys
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.settings")
django.setup()

from search_app.models import Page, Index, PageLink
from collections import defaultdict

DAMPING_FACTOR = 0.8
ITERATIONS = 500

def compute_pagerank():
    pages = Page.objects.all()
    page_ids = [page.id for page in pages]
    page_index = {page.id: i for i, page in enumerate(pages)}
    N = len(page_ids)

    # Initialize rank for each page
    ranks = [1.0 / N] * N

    # Build graph: page_id -> list of to_page_id
    outgoing_links = defaultdict(list)
    incoming_links = defaultdict(list)

    for link in PageLink.objects.all():
        if link.from_page_id != link.to_page_id:  # Avoid self-loops
            outgoing_links[link.from_page_id].append(link.to_page_id)
            incoming_links[link.to_page_id].append(link.from_page_id)

    for _ in range(ITERATIONS):
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

    # Normalize the ranks to be between 0.01 and 1
    min_rank = min(ranks)
    max_rank = max(ranks)
    
    # Map the ranks to the desired range [0.01, 1]
    for i, page in enumerate(pages):
        normalized_rank = (ranks[i] - min_rank) / (max_rank - min_rank)  # Normalize to [0, 1]
        normalized_rank = 0.01 + (normalized_rank * (1 - 0.01))  # Scale to [0.01, 1]
        page.rank = normalized_rank
        page.save()

    print("PageRank computation completed.")

if __name__ == "__main__":
    compute_pagerank()