from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import os
import traceback
from analyze_repo import analyze_suspect_repo
from github_search import search_github_repos
from repo_utils import clone_repo
from compare_utils import (
    compare_file_structure,
    cosine_similarity_text,
    compare_code_files
)

app = Flask(__name__)
CORS(app)  # Enable CORS for Node.js backend communication

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "message": "Plagiarism Detection API is running"})

@app.route('/analyze-plagiarism', methods=['POST'])
def analyze_plagiarism():
    """
    Main endpoint to analyze a repository for plagiarism
    
    Expected JSON payload:
    {
        "repo_url": "https://github.com/username/repo",
        "language": "Python",  // optional, defaults to "Python"
        "min_stars": 5,        // optional, defaults to 5
        "per_page": 10,        // optional, defaults to 10
        "max_candidates": 5    // optional, defaults to 5
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400
        
        repo_url = data.get('repo_url')
        if not repo_url:
            return jsonify({"error": "repo_url is required"}), 400
        
        # Optional parameters with defaults
        language = data.get('language', 'Python')
        min_stars = data.get('min_stars', 5)
        per_page = data.get('per_page', 10)
        max_candidates = data.get('max_candidates', 5)
        
        # Step 1: Analyze the suspect repository
        print(f"🔍 Step 1: Analyzing suspect repo: {repo_url}")
        suspect_info = analyze_suspect_repo(repo_url)
        print(f"✅ Suspect repo analyzed: {suspect_info['repo_name']} by {suspect_info['repo_owner']}")
        print(f"📝 Topic: {suspect_info['topic']}")
        print(f"🏷️  Keywords: {', '.join(suspect_info['keywords'][:5])}...")  # Show first 5 keywords
        
        response_data = {
            "suspect_repo": {
                "name": suspect_info['repo_name'],
                "owner": suspect_info['repo_owner'],
                "url": repo_url,
                "topic": suspect_info['topic'],
                "keywords": suspect_info['keywords']
            },
            "analysis_results": [],
            "plagiarism_detected": False,
            "summary": {
                "total_candidates_checked": 0,
                "high_similarity_count": 0,
                "max_structure_similarity": 0.0,
                "max_readme_similarity": 0.0,
                "max_code_similarity": 0.0
            }
        }
        
        # Step 2: Search for candidate repositories
        print(f"🔎 Step 2: Searching for candidate repositories (language: {language}, min_stars: {min_stars})...")
        candidate_repos = search_github_repos(
            keywords=suspect_info["keywords"],
            topic=suspect_info["topic"],
            exclude_user=suspect_info["repo_owner"],
            language=language,
            min_stars=min_stars,
            per_page=per_page
        )
        print(f"📊 Found {len(candidate_repos)} candidate repositories")
        
        # Limit candidates to max_candidates
        candidate_repos = candidate_repos[:max_candidates]
        response_data["summary"]["total_candidates_checked"] = len(candidate_repos)
        
        if not candidate_repos:
            return jsonify({
                **response_data,
                "message": "No candidate repositories found for comparison"
            })
        
        # Step 3: Compare with each candidate
        for i, repo in enumerate(candidate_repos, 1):
            try:
                print(f"🔍 Step 3.{i}: Analyzing candidate {i}/{len(candidate_repos)}: {repo['html_url']}")
                
                # Clone candidate repository
                candidate_dir = os.path.join("candidates", repo["full_name"].replace("/", "_"))
                print(f"📥 Cloning {repo['full_name']}...")
                clone_repo(repo["html_url"], candidate_dir)
                
                # Compare file structure
                print("📁 Comparing file structures...")
                structure_ratio, overlap_files = compare_file_structure(
                    suspect_info["local_path"],
                    candidate_dir
                )
                
                # Compare README files
                print("📄 Comparing README files...")
                readme_similarity = 0.0
                suspect_readme = os.path.join(suspect_info["local_path"], "README.md")
                candidate_readme = os.path.join(candidate_dir, "README.md")
                
                if os.path.exists(suspect_readme) and os.path.exists(candidate_readme):
                    with open(suspect_readme, "r", encoding="utf-8") as f:
                        text1 = f.read()
                    with open(candidate_readme, "r", encoding="utf-8") as f:
                        text2 = f.read()
                    readme_similarity = cosine_similarity_text(text1, text2)
                
                # Compare code files
                print("💻 Comparing code files...")
                code_similarity = compare_code_files(
                    suspect_info["local_path"],
                    candidate_dir
                )
                
                print(f"📊 Similarities - Structure: {structure_ratio:.2f}, README: {readme_similarity:.2f}, Code: {code_similarity:.2f}")
                
                # Determine if plagiarism is detected
                is_plagiarism = (
                    structure_ratio > 0.7 or
                    readme_similarity > 0.8 or
                    code_similarity > 0.8
                )
                
                if is_plagiarism:
                    response_data["plagiarism_detected"] = True
                    response_data["summary"]["high_similarity_count"] += 1
                
                # Update maximum similarities
                response_data["summary"]["max_structure_similarity"] = max(
                    response_data["summary"]["max_structure_similarity"], 
                    structure_ratio
                )
                response_data["summary"]["max_readme_similarity"] = max(
                    response_data["summary"]["max_readme_similarity"], 
                    readme_similarity
                )
                response_data["summary"]["max_code_similarity"] = max(
                    response_data["summary"]["max_code_similarity"], 
                    code_similarity
                )
                
                # Add result to response
                result = {
                    "candidate_repo": {
                        "name": repo["full_name"],
                        "url": repo["html_url"],
                        "stars": repo["stars"],
                        "description": repo["description"],
                        "language": repo["language"]
                    },
                    "similarities": {
                        "file_structure": round(structure_ratio, 3),
                        "readme": round(readme_similarity, 3),
                        "code": round(code_similarity, 3)
                    },
                    "plagiarism_detected": is_plagiarism,
                    "overlapping_files": list(overlap_files) if isinstance(overlap_files, set) else overlap_files
                }
                
                response_data["analysis_results"].append(result)
                
            except Exception as e:
                print(f"Error analyzing candidate {repo['html_url']}: {str(e)}")
                # Continue with next candidate instead of failing completely
                continue
        
        return jsonify(response_data)
        
    except Exception as e:
        error_message = str(e)
        print(f"Error in analyze_plagiarism: {error_message}")
        print(traceback.format_exc())
        return jsonify({
            "error": "Internal server error",
            "message": error_message
        }), 500

@app.route('/analyze-repo-only', methods=['POST'])
def analyze_repo_only():
    """
    Endpoint to analyze a single repository without plagiarism detection
    
    Expected JSON payload:
    {
        "repo_url": "https://github.com/username/repo"
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400
        
        repo_url = data.get('repo_url')
        if not repo_url:
            return jsonify({"error": "repo_url is required"}), 400
        
        # Analyze the repository
        suspect_info = analyze_suspect_repo(repo_url)
        
        return jsonify({
            "repo_name": suspect_info['repo_name'],
            "repo_owner": suspect_info['repo_owner'],
            "repo_url": repo_url,
            "topic": suspect_info['topic'],
            "keywords": suspect_info['keywords'],
            "local_path": suspect_info['local_path']
        })
        
    except Exception as e:
        error_message = str(e)
        print(f"Error in analyze_repo_only: {error_message}")
        print(traceback.format_exc())
        return jsonify({
            "error": "Internal server error",
            "message": error_message
        }), 500

@app.route('/search-repos', methods=['POST'])
def search_repos():
    """
    Endpoint to search GitHub repositories
    
    Expected JSON payload:
    {
        "keywords": ["react", "portfolio"],
        "topic": "portfolio website",      // optional
        "language": "JavaScript",         // optional
        "exclude_user": "username",       // optional
        "min_stars": 5,                   // optional
        "per_page": 10                    // optional
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400
        
        keywords = data.get('keywords', [])
        if not keywords:
            return jsonify({"error": "keywords array is required"}), 400
        
        # Optional parameters
        topic = data.get('topic')
        language = data.get('language')
        exclude_user = data.get('exclude_user')
        min_stars = data.get('min_stars', 0)
        per_page = data.get('per_page', 10)
        
        # Search repositories
        repos = search_github_repos(
            keywords=keywords,
            topic=topic,
            language=language,
            exclude_user=exclude_user,
            min_stars=min_stars,
            per_page=per_page
        )
        
        return jsonify({
            "total_found": len(repos),
            "repositories": repos
        })
        
    except Exception as e:
        error_message = str(e)
        print(f"Error in search_repos: {error_message}")
        print(traceback.format_exc())
        return jsonify({
            "error": "Internal server error",
            "message": error_message
        }), 500

if __name__ == '__main__':
    # Create necessary directories
    os.makedirs("candidates", exist_ok=True)
    
    print("🚀 Starting Plagiarism Detection API on http://localhost:3009")
    print("📋 Available endpoints:")
    print("  GET  /health")
    print("  POST /analyze-plagiarism")
    print("  POST /analyze-repo-only") 
    print("  POST /search-repos")
    print("🛑 Press Ctrl+C to stop\n")
    
    # Run the Flask app - disable debug mode to prevent auto-restart on file changes
    app.run(host='0.0.0.0', port=3009, debug=False, threaded=True)
