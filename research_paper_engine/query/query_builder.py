def build_query(user_query, category_filter=None):
    query = {
        "query": {
            "bool": {
                "must": [
                    {
                        "multi_match": {
                            "query": user_query,
                            "fields": ["title^3", "keywords^2", "abstract^1", "authors^1"],
                            "type": "best_fields",
                            "fuzziness": "AUTO"   # handles typos e.g. "tranformer" → "transformer"
                        }
                    }
                ]
            }
        },
        "highlight": {
            "fields": {
                "title":    {},
                "abstract": {"fragment_size": 200, "number_of_fragments": 1}
            }
        },
        "_source": ["arxiv_id", "title", "abstract", "authors", "categories", "keywords", "url", "pdf_url"]
    }

    # Optional category filter e.g. "cs.LG"
    if category_filter:
        query["query"]["bool"]["filter"] = [
            {"term": {"categories": category_filter}}
        ]

    return query