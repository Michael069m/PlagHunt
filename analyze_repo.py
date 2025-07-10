import os
import json
import re
import shutil
from git import Repo
from google import genai

# Setup Gemini client
client = genai.Client(api_key="AIzaSyASaYDYt5VNobHpcpsm3ngIUn1rD49UJgM")

def parse_github_url(url):
    """
    Extract owner + repo name from a GitHub URL
    e.g. https://github.com/Aaraav/Portfolio
         → Aaraav, Portfolio
    """
    pattern = r"github\.com[:/](\w[\w\-]*)/([\w\-\.]+)"
    m = re.search(pattern, url)
    if not m:
        raise ValueError("Invalid GitHub URL")
    owner, repo = m.group(1), m.group(2).replace(".git", "")
    return owner, repo

def clone_repo(url, clone_dir="./cloned_repo"):
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
        for name in files:
            file_path = os.path.join(root, name)
            if os.path.getsize(file_path) < 5000 and name.endswith((".js", ".ts", ".py", ".html", ".jsx")):
                with open(file_path, "r", encoding="utf-8") as f:
                    combined_text += f.read() + "\n"

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

    response = client.models.generate_content(
        model="gemini-2.5-flash", contents=prompt
    )
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
    owner, repo_name = parse_github_url(repo_url)
    local_path = clone_repo(repo_url)
    project_text = collect_project_text(local_path)
    analysis = analyze_with_gemini(project_text)

    result = {
        "repo_owner": owner,
        "repo_name": repo_name,
        "repo_url": repo_url,
        "topic": analysis.get("topic", "unknown"),
        "keywords": analysis.get("keywords", []),
        "local_path": local_path
    }
    return result

if __name__ == "__main__":
    repo_url = input("Enter suspect GitHub repo URL: ").strip()
    info = analyze_suspect_repo(repo_url)
    print(json.dumps(info, indent=2))
