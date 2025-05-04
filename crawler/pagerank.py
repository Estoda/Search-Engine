import django
import os
import sys
import numpy as np

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.settings")
django.setup()

from search_app.models import Page, PageLink

def compute_pagerank(damping=0.85, max_iter=100, tol=1e-6):
    pages = list(Page.objects.all())
    page_index = {page.id: i for i, page in enumerate(pages)}
    n = len(pages)

    if n == 0:
        print("No pages found.")
        return 
    
    # transition matrix
    M = np.zeros((n, n))

    for link in PageLink.objects.all():
        i = page_index(link.from_page.id)
        j = page_index(link.to_page.id)
        if i is not None and j is not None:
            M[j][i] +=1 # link from j to i

    # convert every column to a probability distribution
    for i in range(n):
        col_sum = np.sum(M[:, i])
        if col_sum != 0:
            M[:, i] /= col_sum
        else:
            # if the column is all zeros, set it to uniform distribution
            M[:, i] = 1.0 / n

    # PageRank vector initialization
    rank = np.ones(n) / n

    for iteration in range(max_iter):
        new_rank = damping * M @ rank + (1 - damping) / n
        if np.linalg.norm(new_rank - rank, ord=1) < tol:
            print(f"Converged after {iteration} iterations.")
            break
        rank = new_rank

    
    # Save ranks back to DB
    for i, page in enumerate(pages):
        page.rank = rank[i]
        page.save()

    print("PageRank updated for all pages.")

if __name__ == "__main__":
    compute_pagerank()

