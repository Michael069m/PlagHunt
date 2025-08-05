import requests
import os
from itertools import islice
from .config_loader import get_github_token

GITHUB_API_URL = "https://api.github.com/search/repositories"

def chunk_keywords(keywords, chunk_size=5):
    """
    Yield successive chunks of keywords
    """
    it = iter(keywords)
    while True:
        chunk = list(islice(it, chunk_size))
        if not chunk:
            break
        yield chunk

def search_github_repos(
    keywords,
    topic=None,
    language=None,
    exclude_user=None,
    min_stars=0,
    per_page=30,  # Increased from 10 to 30
    created_before=None,
    max_results=100  # Maximum total results to fetch
):
    """
    Search GitHub repositories with date filtering support.
    
    Args:
        created_before: ISO date string (YYYY-MM-DD) to exclude repos created after this date
        max_results: Maximum number of total results to return
    """
    all_results = []
    seen_repos = set()

    # Try multiple search strategies to maximize results
    search_strategies = []
    
    # Helper function to clean topic for search
    def clean_topic_for_search(topic_str):
        if not topic_str or topic_str.lower() == "unknown":
            return []
        # Split on common separators and clean up
        parts = topic_str.replace("/", " ").replace("-", " ").replace("_", " ").split()
        # Remove common words that don't help with search
        stop_words = {"a", "an", "the", "and", "or", "but", "for", "of", "to", "in", "on", "at", "by"}
        cleaned = [part.strip() for part in parts if part.strip() and part.lower() not in stop_words]
        return cleaned
    
    # Clean topic into searchable terms
    topic_terms = clean_topic_for_search(topic) if topic else []
    
    # Strategy 1: Most specific keywords from topic + keywords
    specific_terms = []
    if topic_terms:
        specific_terms.extend(topic_terms[:2])  # Take first 2 topic terms
    if keywords:
        specific_terms.extend(keywords[:3])  # Add top 3 keywords
    
    if specific_terms:
        search_strategies.append({
            "query_terms": specific_terms,
            "name": "specific_terms"
        })
    
    # Strategy 2: Topic terms only (if available)
    if topic_terms:
        search_strategies.append({
            "query_terms": topic_terms,
            "name": "topic_terms"
        })
    
    # Strategy 3: Keywords only (broader search)
    if keywords:
        search_strategies.append({
            "query_terms": keywords[:4],  # top 4 keywords
            "name": "keywords_only"
        })
    
    # Strategy 4: Individual keyword searches (most comprehensive)
    if keywords:
        for i, keyword in enumerate(keywords[:3]):  # Try top 3 keywords individually
            search_strategies.append({
                "query_terms": [keyword],
                "name": f"single_keyword_{i+1}"
            })
    
    # If no strategies, fallback to basic search
    if not search_strategies:
        search_strategies.append({
            "query_terms": ["portfolio", "dashboard", "project"] if not keywords else keywords[:1],
            "name": "fallback"
        })

    for strategy in search_strategies:
        if len(all_results) >= max_results:
            break
            
        print(f"🔍 Trying search strategy: {strategy['name']}")
        
        # Try different star thresholds
        star_thresholds = [0, 1, 5] if strategy['name'] != 'fallback' else [0]
        
        for min_star_threshold in star_thresholds:
            if len(all_results) >= max_results:
                break
            # Compose a safe query
            query_terms = strategy["query_terms"].copy()
            
            # Create proper search query - use quotes for multi-word terms
            formatted_terms = []
            for term in query_terms:
                if " " in term:
                    formatted_terms.append(f'"{term}"')  # Quote multi-word terms
                else:
                    formatted_terms.append(term)
            
            query = " ".join(formatted_terms)

            if exclude_user:
                query += f" -user:{exclude_user}"

            if language:
                query += f" language:{language}"

            if min_star_threshold > 0:
                query += f" stars:>={min_star_threshold}"

            if created_before:
                query += f" created:<{created_before}"

            # truncate if still too long
            query = query[:250]

            params = {
                "q": query,
                "per_page": min(per_page, 30),  # GitHub max is 100, but 30 is reasonable
                "sort": "stars",
                "order": "desc"
            }

            headers = {
                "Accept": "application/vnd.github+json",
                "Authorization": f"Bearer {get_github_token()}"
            }

            try:
                response = requests.get(GITHUB_API_URL, params=params, headers=headers)
                
                # If authentication fails, try without token (with rate limits)
                if response.status_code == 401:
                    print(f"Warning: GitHub token invalid, trying without authentication (limited rate)...")
                    headers = {"Accept": "application/vnd.github+json"}
                    response = requests.get(GITHUB_API_URL, params=params, headers=headers)
                
                if response.status_code == 403:
                    print(f"Warning: Rate limit reached. Continuing with existing results...")
                    break
                    
                response.raise_for_status()
                results = response.json()
                
                found_in_this_search = 0
                for item in results.get("items", []):
                    repo_full_name = item["full_name"]
                    if repo_full_name in seen_repos:
                        continue

                    seen_repos.add(repo_full_name)
                    all_results.append({
                        "full_name": repo_full_name,
                        "html_url": item["html_url"],
                        "stars": item["stargazers_count"],
                        "description": item["description"],
                        "owner": item["owner"]["login"],
                        "language": item["language"]
                    })
                    found_in_this_search += 1
                    
                    if len(all_results) >= max_results:
                        break
                
                print(f"  ✅ Found {found_in_this_search} new repos with {min_star_threshold}+ stars")
                
                # If we found good results with higher stars, no need to try lower thresholds
                if found_in_this_search >= 10:
                    break
                    
            except Exception as e:
                print(f"  ❌ Search failed: {e}")
                continue

    print(f"🎯 Total unique repositories found: {len(all_results)}")
    return all_results

if __name__ == "__main__":
    # Example usage
    repos = search_github_repos(
        keywords=["portfolio", "react"],
        topic="portfolio website",
        language="JavaScript",
        exclude_user="Aaraav",
        min_stars=5,
        per_page=5
    )

    for repo in repos:
        print(repo)
