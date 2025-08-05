import os
import json
import re
import shutil
from git import Repo
from collections import Counter
import google.generativeai as genai
from .config_loader import get_gemini_api_key, get_github_token

# Setup Gemini client
genai.configure(api_key=get_gemini_api_key())

def get_repo_languages(repo_path):
    """Extract the primary languages used in the repository"""
    languages = Counter()
    
    # File extension to language mapping (including Solidity)
    language_map = {
        '.py': 'Python',
        '.js': 'JavaScript',
        '.ts': 'TypeScript',
        '.java': 'Java',
        '.cpp': 'C++',
        '.c': 'C',
        '.cs': 'C#',
        '.go': 'Go',
        '.rs': 'Rust',
        '.php': 'PHP',
        '.rb': 'Ruby',
        '.swift': 'Swift',
        '.kt': 'Kotlin',
        '.scala': 'Scala',
        '.r': 'R',
        '.m': 'Objective-C',
        '.dart': 'Dart',
        '.lua': 'Lua',
        '.pl': 'Perl',
        '.sh': 'Shell',
        '.sql': 'SQL',
        '.html': 'HTML',
        '.css': 'CSS',
        '.jsx': 'JavaScript',
        '.tsx': 'TypeScript',
        '.vue': 'Vue',
        '.svelte': 'Svelte',
        '.sol': 'Solidity',  # Added Solidity support
        '.cairo': 'Cairo',   # StarkNet
        '.move': 'Move',     # Aptos/Sui
        '.vy': 'Vyper',      # Ethereum Vyper
        '.fe': 'Fe',         # Ethereum Fe
        '.yul': 'Yul'        # Ethereum assembly
    }
    
    # Count files by extension and weight by file size
    total_size = 0
    for root, dirs, files in os.walk(repo_path):
        # Skip hidden directories and common build/dependency directories
        dirs[:] = [d for d in dirs if not d.startswith('.') and d not in 
                  ['node_modules', '__pycache__', 'venv', 'env', 'build', 'dist', 'target', 
                   'artifacts', 'cache', 'typechain-types', 'contracts/build']]
        
        for file in files:
            if file.startswith('.'):
                continue
                
            file_path = os.path.join(root, file)
            try:
                # Get file size to weight languages by code volume
                file_size = os.path.getsize(file_path)
                if file_size > 1024 * 1024:  # Skip files larger than 1MB
                    continue
                    
                _, ext = os.path.splitext(file.lower())
                if ext in language_map:
                    languages[language_map[ext]] += file_size
                    total_size += file_size
            except (OSError, IOError):
                continue
    
    if not languages:
        return ['Python']  # Default fallback
    
    # Convert to percentages and get top languages
    language_percentages = []
    
    for lang, size in languages.most_common():
        percentage = (size / total_size) * 100 if total_size > 0 else 0
        if percentage >= 3:  # Only include languages that make up at least 3%
            language_percentages.append(lang)
    
    # Return list of primary languages (top 3)
    primary_languages = language_percentages[:3]
    return primary_languages if primary_languages else ['Python']

def get_detailed_language_info(repo_path):
    """Get detailed language breakdown for display"""
    languages = Counter()
    language_map = {
        '.py': 'Python', '.js': 'JavaScript', '.ts': 'TypeScript', '.java': 'Java',
        '.cpp': 'C++', '.c': 'C', '.cs': 'C#', '.go': 'Go', '.rs': 'Rust',
        '.php': 'PHP', '.rb': 'Ruby', '.swift': 'Swift', '.kt': 'Kotlin',
        '.sol': 'Solidity', '.cairo': 'Cairo', '.move': 'Move', '.vy': 'Vyper'
    }
    
    for root, dirs, files in os.walk(repo_path):
        dirs[:] = [d for d in dirs if not d.startswith('.') and d not in 
                  ['node_modules', '__pycache__', 'venv', 'env', 'build', 'dist', 
                   'artifacts', 'cache', 'typechain-types']]
        
        for file in files:
            if file.startswith('.'):
                continue
            _, ext = os.path.splitext(file.lower())
            if ext in language_map:
                languages[language_map[ext]] += 1
    
    total_files = sum(languages.values())
    if total_files == 0:
        return [{'language': 'Unknown', 'percentage': 100, 'file_count': 0}]
    
    return [
        {
            'language': lang,
            'percentage': round((count / total_files) * 100, 1),
            'file_count': count
        }
        for lang, count in languages.most_common()
        if (count / total_files) * 100 >= 1  # Only show languages with at least 1% of files
    ]

def get_readme_content(repo_path):
    """Extract README content from a repository"""
    readme_files = ['README.md', 'README.txt', 'README.rst', 'README']
    for readme_file in readme_files:
        readme_path = os.path.join(repo_path, readme_file)
        if os.path.exists(readme_path):
            try:
                with open(readme_path, 'r', encoding='utf-8') as f:
                    return f.read()
            except Exception:
                continue
    return ""

def parse_github_url(url):
    """
    Extract owner + repo name from a GitHub URL
    e.g. https://github.com/Username/RepoName.git
         → Username, RepoName.git
    """
    pattern = r"github\.com[:/](\w[\w\-]*)/([\w\-\.]+)"
    m = re.search(pattern, url)
    if not m:
        raise ValueError("Invalid GitHub URL")
    owner, repo = m.group(1), m.group(2).replace(".git", "")
    return owner, repo

def clone_repo(url, clone_dir="/tmp/plaghunt_cloned_repo"):
    # Remove existing clone
    if os.path.exists(clone_dir):
        shutil.rmtree(clone_dir)
    Repo.clone_from(url, clone_dir)
    return clone_dir

def collect_project_text(project_path):
    """
    Reads README + package.json + small files for analysis.
    """
    combined_text = ""
    
    # README
    readme_path = os.path.join(project_path, "README.md")
    if os.path.exists(readme_path):
        with open(readme_path, "r", encoding="utf-8") as f:
            combined_text += f.read() + "\n"

    # package.json
    package_path = os.path.join(project_path, "package.json")
    if os.path.exists(package_path):
        with open(package_path, "r", encoding="utf-8") as f:
            combined_text += f.read() + "\n"

    # Small code files
    for root, dirs, files in os.walk(project_path):
        # Skip node_modules and other common directories that might contain binaries
        dirs[:] = [d for d in dirs if d not in ['node_modules', '.git', '__pycache__', '.venv', 'venv', 'artifacts', 'cache']]
        
        for name in files:
            file_path = os.path.join(root, name)
            try:
                # Check if file exists and is a regular file (not a symlink or binary)
                if (os.path.isfile(file_path) and 
                    not os.path.islink(file_path) and 
                    os.path.getsize(file_path) < 5000 and 
                    name.endswith((".js", ".ts", ".py", ".html", ".jsx", ".sol", ".vy", ".cairo"))):
                    with open(file_path, "r", encoding="utf-8") as f:
                        combined_text += f.read() + "\n"
            except (OSError, IOError, UnicodeDecodeError) as e:
                # Skip files that can't be read (binaries, permission issues, etc.)
                print(f"Skipping file {file_path}: {e}")
                continue

    return combined_text

def analyze_with_gemini(text):
    import re

    prompt = f"""
You are an AI that analyzes software projects.

Given the following text, identify:
- The main project topic (e.g. ecommerce app, portfolio, blog, chat app, etc.)
- A list of important keywords related to the project domain, functionality, or tech stack.

Return ONLY this JSON format:

{{
  "topic": "...",
  "keywords": ["...", "...", "..."]
}}

Project Text:
{text}
    """

    response = genai.GenerativeModel('gemini-2.5-flash').generate_content(prompt)
    text_response = response.text.strip()

    # Remove ```json fences if present
    text_response = re.sub(r"^```json", "", text_response, flags=re.IGNORECASE)
    text_response = re.sub(r"^```", "", text_response)
    text_response = re.sub(r"```$", "", text_response)
    text_response = text_response.strip()

    try:
        result = json.loads(text_response)
    except json.JSONDecodeError:
        result = {
            "topic": "unknown",
            "keywords": []
        }
    return result

def analyze_suspect_repo(repo_url):
    import requests
    from datetime import datetime
    
    owner, repo_name = parse_github_url(repo_url)
    local_path = clone_repo(repo_url)
    project_text = collect_project_text(local_path)
    analysis = analyze_with_gemini(project_text)
    
    # Extract languages from the repository
    primary_languages = get_repo_languages(local_path)
    language_info = get_detailed_language_info(local_path)
    
    # Get README content
    readme_content = get_readme_content(local_path)

    # Get repository creation date from GitHub API
    created_at = None
    try:
        github_api_url = f"https://api.github.com/repos/{owner}/{repo_name}"
        headers = {
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {get_github_token()}"
        }
        response = requests.get(github_api_url, headers=headers)
        
        # If authentication fails, try without token
        if response.status_code == 401:
            print(f"Warning: GitHub token invalid, trying without authentication...")
            response = requests.get(github_api_url)
            
        if response.status_code == 200:
            repo_data = response.json()
            created_at = repo_data.get("created_at")
            # Convert to YYYY-MM-DD format for GitHub search
            if created_at:
                created_date = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                created_at = created_date.strftime('%Y-%m-%d')
                print(f"Repository created on: {created_at}")
        else:
            print(f"Warning: Could not fetch repo info. Status: {response.status_code}")
    except Exception as e:
        print(f"Warning: Could not fetch creation date: {e}")

    result = {
        "repo_owner": owner,
        "repo_name": repo_name,
        "repo_url": repo_url,
        "topic": analysis.get("topic", "unknown"),
        "keywords": analysis.get("keywords", []),
        "local_path": local_path,
        "readme_content": readme_content,
        "primary_languages": primary_languages,  # New field
        "language_info": language_info,  # New field for detailed breakdown
        "created_at": created_at
    }
    return result

if __name__ == "__main__":
    repo_url = input("Enter suspect GitHub repo URL: ").strip()
    info = analyze_suspect_repo(repo_url)
    print(json.dumps(info, indent=2))
