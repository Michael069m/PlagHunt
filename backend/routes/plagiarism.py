from flask import Blueprint, request, jsonify
from middleware.auth import auth_required, optional_auth
from models.plagiarism_result import PlagiarismResult
import requests
import re
import os
import traceback
from utils.analyze_repo import analyze_suspect_repo
from utils.github_search import search_github_repos
from utils.repo_utils import clone_repo
from utils.compare_utils import (
    compare_file_structure,
    cosine_similarity_text,
    compare_code_files
)

plagiarism_bp = Blueprint('plagiarism', __name__)
result_model = PlagiarismResult()

def parse_github_url(url):
    """Extract owner and repo name from GitHub URL"""
    pattern = r"github\.com[:/](\w[\w\-]*)/([\w\-\.]+)"
    m = re.search(pattern, url)
    if not m:
        raise ValueError("Invalid GitHub URL")
    owner, repo = m.group(1), m.group(2).replace(".git", "")
    return owner, repo

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

def assess_project_uniqueness(suspect_info, candidate_repos):
    """Assess how unique the project is based on topic and functionality"""
    
    suspect_topic = suspect_info.get('topic', '').lower()
    suspect_keywords = [k.lower() for k in suspect_info.get('keywords', [])]
    
    # Common project types (less unique)
    common_topics = [
        'todo app', 'calculator', 'weather app', 'blog', 'portfolio',
        'chat app', 'ecommerce', 'crud app', 'login system', 'basic website',
        'simple game', 'contact form', 'image gallery', 'basic api'
    ]
    
    # Advanced project types (more unique)
    advanced_topics = [
        'machine learning', 'blockchain', 'compiler', 'database engine',
        'operating system', 'game engine', 'ai model', 'distributed system',
        'neural network', 'cryptocurrency', 'computer vision', 'nlp',
        'deep learning', 'microservices', 'kubernetes', 'docker', 'solidity',
        'smart contract', 'defi', 'nft', 'web3', 'ethereum', 'dapp'
    ]
    
    # Calculate topic uniqueness
    is_common = any(common in suspect_topic for common in common_topics)
    is_advanced = any(advanced in suspect_topic for advanced in advanced_topics)
    
    if is_advanced:
        topic_uniqueness = 0.8
    elif is_common:
        topic_uniqueness = 0.3
    else:
        topic_uniqueness = 0.6
    
    # Calculate keyword overlap with candidates
    total_overlap = 0
    for repo in candidate_repos:
        repo_desc = repo.get('description', '').lower()
        repo_name = repo.get('name', '').lower()
        
        keyword_matches = sum(1 for keyword in suspect_keywords 
                            if keyword in repo_desc or keyword in repo_name)
        overlap_ratio = keyword_matches / max(len(suspect_keywords), 1)
        total_overlap += overlap_ratio
    
    avg_keyword_overlap = total_overlap / max(len(candidate_repos), 1)
    
    # Higher overlap = less unique
    keyword_uniqueness = 1.0 - min(avg_keyword_overlap, 0.8)
    
    # Combined uniqueness score
    overall_uniqueness = (topic_uniqueness + keyword_uniqueness) / 2
    
    return {
        'overall_uniqueness': round(overall_uniqueness * 100, 1),  # Convert to percentage
        'topic_uniqueness': round(topic_uniqueness * 100, 1),
        'keyword_uniqueness': round(keyword_uniqueness * 100, 1),
        'is_common_project_type': is_common,
        'is_advanced_project_type': is_advanced,
        'avg_keyword_overlap': round(avg_keyword_overlap * 100, 1)
    }

def simple_github_search(language="Python", per_page=10):
    """Simple GitHub search without advanced analysis"""
    try:
        params = {
            "q": f"language:{language} stars:>10",
            "per_page": per_page,
            "sort": "stars",
            "order": "desc"
        }
        
        response = requests.get("https://api.github.com/search/repositories", params=params)
        if response.status_code == 200:
            results = response.json()
            return results.get("items", [])[:5]  # Return top 5 results
    except Exception as e:
        print(f"GitHub search error: {e}")
    
    return []

@plagiarism_bp.route('/analyze', methods=['POST'])
@auth_required
def analyze_plagiarism():
    """
    Analyze a repository for plagiarism (simplified version)
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400
        
        repo_url = data.get('repo_url')
        if not repo_url:
            return jsonify({"error": "repo_url is required"}), 400
        
        # Optional parameters with defaults - language will be auto-detected
        manual_language = data.get('language')  # User can still override if needed
        
        print(f"Starting plagiarism analysis for: {repo_url}")
        
        # Validate GitHub URL
        try:
            owner, repo_name = parse_github_url(repo_url)
        except ValueError as e:
            return jsonify({"error": str(e)}), 400

        # Step 1: Analyze the suspect repository (now includes language detection)
        print(f"🔍 Step 1: Analyzing suspect repo: {repo_url}")
        suspect_info = analyze_suspect_repo(repo_url)
        
        # Extract primary languages from the repository
        primary_languages = suspect_info.get('primary_languages', ['Python'])
        main_language = manual_language or primary_languages[0] if primary_languages else 'Python'
        
        print(f"✅ Suspect repo analyzed: {suspect_info['repo_name']} by {suspect_info['repo_owner']}")
        print(f"📝 Topic: {suspect_info['topic']}")
        print(f"💻 Detected languages: {', '.join(primary_languages)}")
        print(f"� Primary language for search: {main_language}")
        print(f"�🏷️  Keywords: {', '.join(suspect_info['keywords'][:5])}...")

        # Step 2: Search for candidate repositories using detected languages
        print(f"🔎 Step 2: Searching for candidate repositories...")
        print(f"📝 Search parameters:")
        print(f"   Keywords: {suspect_info['keywords'][:5]}...")
        print(f"   Topic: {suspect_info['topic']}")
        print(f"   Exclude user: {suspect_info['repo_owner']}")
        print(f"   Primary Language: {main_language}")
        print(f"   All Languages: {', '.join(primary_languages)}")
        
        # Search with primary language first, then fallback to other languages if needed
        candidate_repos = []
        
        # Try primary language first
        languages_to_try = [main_language] + [lang for lang in primary_languages if lang != main_language]
        
        for lang in languages_to_try:
            if len(candidate_repos) >= 15:  # Stop if we have enough candidates
                break
                
            try:
                print(f"🔍 Searching with language: {lang}")
                lang_candidates = search_github_repos(
                    keywords=suspect_info["keywords"],
                    topic=suspect_info["topic"],
                    exclude_user=suspect_info["repo_owner"],
                    language=lang,
                    min_stars=0,
                    per_page=20,
                    max_results=30,
                )
                
                # Add candidates, avoiding duplicates
                for candidate in lang_candidates:
                    if not any(existing['html_url'] == candidate['html_url'] for existing in candidate_repos):
                        candidate_repos.append(candidate)
                        
                print(f"📊 Found {len(lang_candidates)} candidates for {lang} (total: {len(candidate_repos)})")
                
            except Exception as e:
                print(f"❌ Search failed for {lang}: {e}")
                continue

        # Increase limit from 5 to 15 candidates for better analysis
        candidate_repos = candidate_repos[:15]
        
        if not candidate_repos:
            return jsonify({
                "error": "No candidate repositories found for comparison",
                "repo_url": repo_url,
                "detected_languages": primary_languages,
                "candidates_found": 0
            }), 404

        # Step 3: Compare with each candidate
        analysis_results = []
        max_structure_similarity = 0.0
        max_readme_similarity = 0.0
        max_code_similarity = 0.0
        high_similarity_count = 0

        for i, repo in enumerate(candidate_repos, 1):
            try:
                print(f"🔍 Step 3.{i}: Analyzing candidate {i}/{len(candidate_repos)}: {repo['html_url']}")
                
                # Clone candidate repository to a safe location
                candidates_base_dir = "/tmp/plaghunt_candidates"
                os.makedirs(candidates_base_dir, exist_ok=True)
                candidate_dir = os.path.join(candidates_base_dir, repo["full_name"].replace("/", "_"))
                print(f"📥 Cloning {repo['full_name']} to {candidate_dir}...")
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
                try:
                    readme_similarity = cosine_similarity_text(
                        suspect_info.get("readme_content", ""),
                        get_readme_content(candidate_dir)
                    )
                except Exception as e:
                    print(f"README comparison failed: {e}")

                # Compare code files
                print("💻 Comparing code files...")
                code_similarity = 0.0
                try:
                    code_similarity = compare_code_files(
                        suspect_info["local_path"],
                        candidate_dir
                    )
                except Exception as e:
                    print(f"Code comparison failed: {e}")

                # Calculate enhanced weighted similarity
                def calculate_weighted_similarity(structure_ratio, readme_similarity, code_similarity):
                    """Calculate weighted similarity that better reflects plagiarism risk"""
                    # Weight code similarity highest as it's most indicative of plagiarism
                    weights = {
                        'code': 0.5,        # 50% - most important
                        'structure': 0.3,   # 30% - structural copying
                        'readme': 0.2       # 20% - documentation copying
                    }
                    
                    # Apply weights
                    weighted_score = (
                        code_similarity * weights['code'] +
                        structure_ratio * weights['structure'] +
                        readme_similarity * weights['readme']
                    )
                    
                    # Boost score if multiple high similarities (indicates systematic copying)
                    high_sim_count = sum([
                        1 for sim in [structure_ratio, readme_similarity, code_similarity] 
                        if sim > 0.7
                    ])
                    
                    if high_sim_count >= 2:
                        weighted_score *= 1.2  # 20% boost for multiple high similarities
                    
                    return min(weighted_score, 1.0)  # Cap at 1.0

                # Calculate enhanced similarity
                overall_similarity = calculate_weighted_similarity(
                    structure_ratio, readme_similarity, code_similarity
                )

                # Update maximums
                max_structure_similarity = max(max_structure_similarity, structure_ratio)
                max_readme_similarity = max(max_readme_similarity, readme_similarity)
                max_code_similarity = max(max_code_similarity, code_similarity)

                # Enhanced plagiarism detection with multiple criteria
                high_code_sim = code_similarity > 0.8
                high_structure_sim = structure_ratio > 0.7
                high_readme_sim = readme_similarity > 0.8
                high_overall_sim = overall_similarity > 0.7
                
                # More sophisticated plagiarism detection
                is_high_similarity = (
                    high_overall_sim or
                    (high_code_sim and high_structure_sim) or
                    (code_similarity > 0.9) or  # Very high code similarity alone
                    (structure_ratio > 0.9)     # Very high structure similarity alone
                )
                
                if is_high_similarity:
                    high_similarity_count += 1

                # Determine risk level for this specific match
                if overall_similarity > 0.9:
                    match_risk = "Critical"
                elif overall_similarity > 0.8:
                    match_risk = "High"
                elif overall_similarity > 0.6:
                    match_risk = "Medium"
                else:
                    match_risk = "Low"

                analysis_results.append({
                    "candidate_repo": {
                        "name": repo["full_name"],
                        "url": repo["html_url"],
                        "stars": repo["stars"],
                        "description": repo.get("description", ""),
                        "language": repo.get("language", "")
                    },
                    "similarity_scores": {
                        "structure_similarity": round(structure_ratio * 100, 1),  # Convert to percentage
                        "readme_similarity": round(readme_similarity * 100, 1),
                        "code_similarity": round(code_similarity * 100, 1),
                        "overall_similarity": round(overall_similarity * 100, 1)
                    },
                    "risk_assessment": {
                        "risk_level": match_risk,
                        "high_code_similarity": high_code_sim,
                        "high_structure_similarity": high_structure_sim,
                        "high_readme_similarity": high_readme_sim
                    },
                    "overlap_files": list(overlap_files),
                    "high_similarity": is_high_similarity
                })

                print(f"✅ Analysis complete for {repo['full_name']}: {overall_similarity:.1f}% overall similarity ({match_risk} risk)")

            except Exception as e:
                print(f"❌ Error analyzing {repo['html_url']}: {e}")
                # Continue with next candidate
                continue

        # Assess project uniqueness
        uniqueness_assessment = assess_project_uniqueness(suspect_info, candidate_repos)
        
        # Calculate enhanced summary statistics
        if analysis_results:
            overall_similarities = [r["similarity_scores"]["overall_similarity"] for r in analysis_results]
            avg_similarity = sum(overall_similarities) / len(overall_similarities)
            highest_similarity = max(overall_similarities)
            
            # Count high-risk matches
            critical_matches = len([r for r in analysis_results if r["risk_assessment"]["risk_level"] == "Critical"])
            high_risk_matches = len([r for r in analysis_results if r["risk_assessment"]["risk_level"] in ["Critical", "High"]])
        else:
            avg_similarity = 0.0
            highest_similarity = 0.0
            critical_matches = 0
            high_risk_matches = 0

        # Enhanced risk assessment
        if critical_matches > 0:
            overall_risk = "Critical"
        elif highest_similarity > 80 or high_risk_matches > 2:  # Using percentage
            overall_risk = "High"
        elif highest_similarity > 60 or high_risk_matches > 0:
            overall_risk = "Medium"
        else:
            overall_risk = "Low"

        # Enhanced plagiarism detection
        plagiarism_detected = (
            highest_similarity > 70 or  # Using percentage
            critical_matches > 0 or
            high_risk_matches > 1
        )

        # Prepare response data
        response_data = {
            "suspect_repo": {
                "name": suspect_info['repo_name'],
                "owner": suspect_info['repo_owner'],
                "url": repo_url,
                "topic": suspect_info['topic'],
                "keywords": suspect_info['keywords'],
                "primary_languages": primary_languages,  # New field
                "language_breakdown": suspect_info.get('language_info', [])  # New field
            },
            "uniqueness_assessment": uniqueness_assessment,
            "analysis_results": analysis_results,
            "plagiarism_detected": plagiarism_detected,
            "summary": {
                "total_candidates_checked": len(analysis_results),
                "high_similarity_count": high_similarity_count,
                "critical_matches": critical_matches,
                "high_risk_matches": high_risk_matches,
                "languages_analyzed": primary_languages,  # New field
                "primary_language": main_language,  # New field
                "max_structure_similarity": round(max_structure_similarity * 100, 1),  # Convert to percentage
                "max_readme_similarity": round(max_readme_similarity * 100, 1),
                "max_code_similarity": round(max_code_similarity * 100, 1),
                "highest_similarity": round(highest_similarity, 1),  # Already in percentage
                "average_similarity": round(avg_similarity, 1),
                "overall_risk_level": overall_risk,
                "project_uniqueness": uniqueness_assessment['overall_uniqueness']
            },
            "status": "completed"
        }
        
        # Save to database if user is authenticated
        current_user = getattr(request, 'current_user', None)
        if current_user:
            result_id = result_model.save_result(
                user_id=current_user['_id'],
                repo_url=repo_url,
                analysis_data=response_data
            )
            response_data['result_id'] = result_id

        print("Analysis completed successfully")
        return jsonify(response_data), 200
        
    except Exception as e:
        print(f"Error in plagiarism analysis: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            "error": "Internal server error during analysis",
            "details": str(e)
        }), 500

@plagiarism_bp.route('/history', methods=['GET'])
@auth_required
def get_history():
    """Get user's plagiarism analysis history"""
    try:
        current_user = getattr(request, 'current_user', None)
        
        # Get pagination parameters
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 20))
        skip = (page - 1) * limit
        
        # Get user history
        history = result_model.get_user_history(
            user_id=current_user['_id'],
            limit=limit,
            skip=skip
        )
        
        # Get stats
        stats = result_model.get_stats(current_user['_id'])
        
        return jsonify({
            "history": history,
            "stats": stats,
            "pagination": {
                "page": page,
                "limit": limit,
                "total": stats['total_analyses']
            }
        }), 200
        
    except Exception as e:
        print(f"Error fetching history: {e}")
        return jsonify({"error": "Failed to fetch history"}), 500

@plagiarism_bp.route('/result/<result_id>', methods=['GET'])
@auth_required
def get_result(result_id):
    """Get specific plagiarism analysis result"""
    try:
        current_user = getattr(request, 'current_user', None)
        
        result = result_model.get_result_by_id(result_id)
        
        if not result:
            return jsonify({"error": "Result not found"}), 404
        
        # Check if user owns this result
        if result['user_id'] != current_user['_id']:
            return jsonify({"error": "Access denied"}), 403
        
        return jsonify(result), 200
        
    except Exception as e:
        print(f"Error fetching result: {e}")
        return jsonify({"error": "Failed to fetch result"}), 500

@plagiarism_bp.route('/result/<result_id>', methods=['DELETE'])
@auth_required
def delete_result(result_id):
    """Delete a plagiarism analysis result"""
    try:
        current_user = getattr(request, 'current_user', None)
        
        success = result_model.delete_result(result_id, current_user['_id'])
        
        if success:
            return jsonify({"message": "Result deleted successfully"}), 200
        else:
            return jsonify({"error": "Result not found or access denied"}), 404
        
    except Exception as e:
        print(f"Error deleting result: {e}")
        return jsonify({"error": "Failed to delete result"}), 500
