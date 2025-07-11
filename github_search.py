import requests
import os
from itertools import islice
from config_loader import get_github_token

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
    per_page=10,
    created_before=None
):
    """
    Search GitHub repositories with date filtering support.
    
    Args:
        created_before: ISO date string (YYYY-MM-DD) to exclude repos created after this date
    """
    all_results = []
    seen_repos = set()

    keyword_chunks = list(chunk_keywords(keywords, chunk_size=5))
    
    if not keyword_chunks:
        keyword_chunks = [[]]  # fallback if no keywords

    for kw_chunk in keyword_chunks:
        # Compose a safe query
        query_terms = []

        if topic and topic.lower() != "unknown":
            query_terms.append(topic)

        if kw_chunk:
            query_terms.extend(kw_chunk)

        query = " ".join(query_terms)

        if exclude_user:
            query += f" -user:{exclude_user}"

        if language:
            query += f" language:{language}"

        if min_stars > 0:
            query += f" stars:>={min_stars}"

        if created_before:
            query += f" created:<{created_before}"

        # truncate if still too long
        query = query[:250]

        params = {
            "q": query,
            "per_page": per_page,
            "sort": "stars",
            "order": "desc"
        }

        headers = {
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {get_github_token()}"
        }

        response = requests.get(GITHUB_API_URL, params=params, headers=headers)
        
        # If authentication fails, try without token (with rate limits)
        if response.status_code == 401:
            print(f"Warning: GitHub token invalid, trying without authentication (limited rate)...")
            headers = {"Accept": "application/vnd.github+json"}
            response = requests.get(GITHUB_API_URL, params=params, headers=headers)
            
        response.raise_for_status()
        results = response.json()

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
