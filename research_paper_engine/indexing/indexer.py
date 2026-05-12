import json
from elasticsearch import helpers
from .es_client import es
from .index_mapping import INDEX_NAME, mapping

def create_index():
    if es.indices.exists(index=INDEX_NAME):
        es.indices.delete(index=INDEX_NAME)
        print(f"🗑️  Deleted existing index")
    es.indices.create(index=INDEX_NAME, body=mapping)
    print(f"✅ Created index: {INDEX_NAME}")

def generate_actions(papers):
    for paper in papers:
        yield {
            "_index": INDEX_NAME,
            "_id":    paper["arxiv_id"],
            "_source": paper
        }

def bulk_index(filepath="../data/processed_papers.json"):
    with open(filepath) as f:
        papers = json.load(f)
    print(f"📄 Loaded {len(papers)} papers")

    success, failed = helpers.bulk(es, generate_actions(papers), stats_only=True)
    print(f"✅ Indexed: {success} | ❌ Failed: {failed}")
    
    es.indices.refresh(index=INDEX_NAME)

    count = es.count(index=INDEX_NAME)["count"]
    print(f"📊 Total in ES: {count}")
    

if __name__ == "__main__":
    create_index()
    bulk_index()