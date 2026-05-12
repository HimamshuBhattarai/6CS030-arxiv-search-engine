import arxiv
import json
import os
from datetime import datetime

CATEGORIES = [
    "cs.LG",   # Machine Learning
    "cs.AI",   # Artificial Intelligence  
    "cs.IR",   # Information Retrieval
    "cs.CL",   # Computation and Language (NLP)
    "cs.CV",   # Computer Vision
    "cs.NE",   # Neural and Evolutionary Computing
]

PAPERS_PER_CATEGORY = 500

def fetch_papers(category: str, max_results: int) -> list[dict]:
    client = arxiv.Client(
        page_size=100,
        delay_seconds=3,
        num_retries=3
    )

    search = arxiv.Search(
        query=f"cat:{category}",       # fetch by category, not keyword
        max_results=max_results,
        sort_by=arxiv.SortCriterion.SubmittedDate,
        sort_order=arxiv.SortOrder.Descending   # most recent first
    )

    papers = []
    for result in client.results(search):
        papers.append({
            "arxiv_id":   result.entry_id.split("/")[-1],
            "title":      result.title,
            "abstract":   result.summary,
            "authors":    [a.name for a in result.authors],
            "categories": result.categories,
            "published":  result.published.strftime("%Y-%m-%d"),
            "updated":    result.updated.strftime("%Y-%m-%d"),
            "url":        result.entry_id,
            "pdf_url":    result.pdf_url,
        })
    return papers


def fetch_all_and_save():
    os.makedirs("data/raw", exist_ok=True)
    all_papers = []

    for category in CATEGORIES:
        print(f"Fetching {PAPERS_PER_CATEGORY} papers from {category}...")
        papers = fetch_papers(category, PAPERS_PER_CATEGORY)
        all_papers.extend(papers)
        print(f"  Got {len(papers)} papers")

    # Remove duplicates by arxiv_id
    seen = set()
    unique_papers = []
    for p in all_papers:
        if p["arxiv_id"] not in seen:
            seen.add(p["arxiv_id"])
            unique_papers.append(p)

    print(f"\nTotal unique papers: {len(unique_papers)}")

    # Save to file
    output_path = "data/raw/papers.json"
    with open(output_path, "w") as f:
        json.dump(unique_papers, f, indent=2)

    print(f"Saved to {output_path}")
    return unique_papers


if __name__ == "__main__":
    fetch_all_and_save()