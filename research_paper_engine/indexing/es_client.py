from elasticsearch import Elasticsearch

es = Elasticsearch("http://localhost:9200")

if es.ping():
    print("✅ Connected to Elasticsearch")
else:
    print("❌ Connection failed")
    exit()