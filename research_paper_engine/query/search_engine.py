from indexing.es_client import es
from indexing.index_mapping import INDEX_NAME
from query.query_builder import build_query

def search(user_query: str, category_filter: str | None = None, top_n: int = 10) -> list[dict]:
    """
    Search papers in Elasticsearch index.
    
    Args:
        user_query: Search query string
        category_filter: Optional arXiv category filter (e.g., 'cs.AI')
        top_n: Number of results to return (1-100)
        
    Returns:
        List of paper results ranked by BM25 relevance score
        
    Raises:
        ValueError: If query is empty or invalid parameters
    """
    # Input validation
    if not user_query or not user_query.strip():
        raise ValueError("Query cannot be empty")
    if top_n < 1 or top_n > 100:
        raise ValueError("top_n must be between 1 and 100")
    
    query = build_query(user_query, category_filter)

    response = es.search(
        index=INDEX_NAME,
        body=query,
        size=top_n
    )

    results = []
    for hit in response["hits"]["hits"]:
        source = hit["_source"]
        results.append({
            "score":      round(hit["_score"], 4),
            "title":      source.get("title", ""),
            "authors":    source.get("authors", [])[:3],   # show first 3 authors
            "categories": source.get("categories", []),
            "keywords":   source.get("keywords", [])[:5],  # show top 5 keywords
            "abstract":   " ".join(source.get("abstract", "").split()[:50]),  # ~50 words
            "url":        source.get("url", ""),
            "pdf_url":    source.get("pdf_url", ""),
            "highlight":  hit.get("highlight", {})
        })

    total = response["hits"]["total"]["value"]
    print(f"🔍 Found {total} results for '{user_query}' (showing top {top_n})")
    return results