import sys
from service.search_service import search

def test_search():
    print("Testing Brave Search API...")
    query = "artificial intelligence"
    
    try:
        # Perform the search
        results = search(query, count=3)
        
        # Check if the results contain web results
        if results and results.get("web", {}).get("results"):
            web_results = results["web"]["results"]
            print(f"\nSuccessfully retrieved {len(web_results)} results for '{query}':\n")
            
            for i, result in enumerate(web_results, 1):
                print(f"[{i}] {result.get('title')}")
                print(f"URL: {result.get('url')}")
                print(f"Description: {result.get('description')}\n")
        else:
            print("Search succeeded but no web results were returned.")
            print("Raw response:", results)
            
    except Exception as e:
        print(f"Test failed with error: {e}")

if __name__ == "__main__":
    test_search()
