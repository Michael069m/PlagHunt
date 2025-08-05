#!/usr/bin/env python3
import requests
import json

# Simple test without the complex search function
def test_github_search():
    url = "https://api.github.com/search/repositories"
    params = {
        "q": "stock prediction python",
        "per_page": 5,
        "sort": "stars",
        "order": "desc"
    }
    
    try:
        response = requests.get(url, params=params)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Total count: {data.get('total_count', 0)}")
            print(f"Items returned: {len(data.get('items', []))}")
            
            for i, item in enumerate(data.get('items', [])[:3]):
                print(f"{i+1}. {item['full_name']} - {item['stargazers_count']} stars")
        else:
            print(f"Error: {response.text}")
            
    except Exception as e:
        print(f"Exception: {e}")

if __name__ == "__main__":
    test_github_search()
