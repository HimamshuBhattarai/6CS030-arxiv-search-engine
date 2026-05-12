from query.search_engine import search

results = search("object detection", category_filter="cs.CV")

for r in results:
    print(f"[{r['score']}] {r['title']}")
    print(f"  Authors   : {r['authors']}")
    print(f"  Keywords  : {r['keywords']}")
    print(f"  URL       : {r['url']}")
    print()