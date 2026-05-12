INDEX_NAME = "arxiv_papers"

mapping = {
    "settings": {
        "analysis": {
            "analyzer": {
                "english_analyzer": {
                    "type": "english"
                }
            }
        },
        "number_of_shards": 1,
        "number_of_replicas": 0
    },
    "mappings": {
        "properties": {
            "arxiv_id":   {"type": "keyword"},
            "title":      {"type": "text", "analyzer": "english_analyzer"},
            "abstract":   {"type": "text", "analyzer": "english_analyzer"},
            "authors":    {"type": "text", "analyzer": "english_analyzer"},
            "categories": {"type": "keyword"},
            "keywords":   {"type": "text", "analyzer": "english_analyzer"},
            "url":        {"type": "keyword", "index": False},
            "pdf_url":    {"type": "keyword", "index": False}
        }
    }
}