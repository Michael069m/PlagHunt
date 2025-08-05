from analyze_repo import analyze_suspect_repo
from github_search import search_github_repos
from repo_utils import clone_repo
from compare_utils import (
    compare_file_structure,
    cosine_similarity_text,
    compare_code_files
)
import os

# Analyze suspect repo
suspect_info = analyze_suspect_repo("https://github.com/Michael069m/m-flix")
print(f"Suspect repo analyzed: {suspect_info['repo_name']} by {suspect_info['repo_owner']}")
print("Suspect repo keywords:", suspect_info["keywords"])
# Search GitHub
candidate_repos = search_github_repos(
    keywords=suspect_info["keywords"],
    topic=suspect_info["topic"],
    exclude_user=suspect_info["repo_owner"],
    # language="JavaScript",
    min_stars=0,
    per_page=5
)
print(f"Found {len(candidate_repos)} candidate repos based on keywords and topic.")
for repo in candidate_repos:
    print(f"Checking candidate repo: {repo['html_url']}")
    candidate_dir = os.path.join("candidates", repo["full_name"].replace("/", "_"))
    clone_repo(repo["html_url"], candidate_dir)

    # Compare file structure
    structure_ratio, overlap_files = compare_file_structure(
        suspect_info["local_path"],
        candidate_dir
    )
    print("File structure overlap:", structure_ratio)

    # Compare README
    suspect_readme = os.path.join(suspect_info["local_path"], "README.md")
    candidate_readme = os.path.join(candidate_dir, "README.md")

    if os.path.exists(suspect_readme) and os.path.exists(candidate_readme):
        with open(suspect_readme, "r", encoding="utf-8") as f:
            text1 = f.read()
        with open(candidate_readme, "r", encoding="utf-8") as f:
            text2 = f.read()

        readme_sim = cosine_similarity_text(text1, text2)
        print("README similarity:", readme_sim)
    else:
        readme_sim = 0.0

    # Compare code
    code_sim = compare_code_files(
        suspect_info["local_path"],
        candidate_dir
    )
    print("Code similarity:", code_sim)

    # Decide plagiarism threshold
    if (
        structure_ratio > 0.7
        or readme_sim > 0.8
        or code_sim > 0.8
    ):
        print(f"❗ Possible plagiarism detected with {repo['html_url']}")
    else:
        print("No significant similarity.\n")
