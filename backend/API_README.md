# Plagiarism Detection API

A Flask-based REST API for detecting code plagiarism by analyzing GitHub repositories.

## Features

- Analyze repositories for topic detection and keyword extraction
- Search GitHub for similar repositories
- Compare file structures, README content, and source code
- Detect potential plagiarism with configurable thresholds
- RESTful API endpoints for integration with Node.js backends

## Setup

### 1. Install Python Dependencies

```bash
pip install flask flask-cors requests GitPython google-genai
```

### 2. Set Environment Variables

Make sure you have your Gemini API key set:

```bash
export GEMINI_API_KEY="your_gemini_api_key_here"
```

### 3. Start the API Server

```bash
python api.py
```

The API will run on `http://localhost:5000`

## API Endpoints

### Health Check
- **GET** `/health`
- Returns the API status

### Analyze Plagiarism
- **POST** `/analyze-plagiarism`
- Analyzes a repository and checks for plagiarism against similar repositories

**Request Body:**
```json
{
    "repo_url": "https://github.com/username/repo",
    "language": "Python",          // optional, defaults to "Python"
    "min_stars": 5,               // optional, defaults to 5
    "per_page": 10,               // optional, defaults to 10
    "max_candidates": 5           // optional, defaults to 5
}
```

**Response:**
```json
{
    "suspect_repo": {
        "name": "repo-name",
        "owner": "username",
        "url": "https://github.com/username/repo",
        "topic": "Machine Learning",
        "keywords": ["python", "ml", "data"]
    },
    "analysis_results": [
        {
            "candidate_repo": {
                "name": "similar-repo",
                "url": "https://github.com/other/similar-repo",
                "stars": 150,
                "description": "A similar project",
                "language": "Python"
            },
            "similarities": {
                "file_structure": 0.85,
                "readme": 0.75,
                "code": 0.60
            },
            "plagiarism_detected": true,
            "overlapping_files": ["main.py", "README.md"]
        }
    ],
    "plagiarism_detected": true,
    "summary": {
        "total_candidates_checked": 5,
        "high_similarity_count": 1,
        "max_structure_similarity": 0.85,
        "max_readme_similarity": 0.75,
        "max_code_similarity": 0.60
    }
}
```

### Analyze Repository Only
- **POST** `/analyze-repo-only`
- Analyzes a single repository without plagiarism checking

**Request Body:**
```json
{
    "repo_url": "https://github.com/username/repo"
}
```

### Search Repositories
- **POST** `/search-repos`
- Searches GitHub for repositories matching criteria

**Request Body:**
```json
{
    "keywords": ["react", "portfolio"],
    "topic": "portfolio website",      // optional
    "language": "JavaScript",         // optional
    "exclude_user": "username",       // optional
    "min_stars": 5,                   // optional
    "per_page": 10                    // optional
}
```

## Node.js Integration

### Install Axios (for HTTP requests)

```bash
npm install axios
```

### Example Usage

```javascript
const axios = require('axios');

async function checkPlagiarism(repoUrl) {
    try {
        const response = await axios.post('http://localhost:5000/analyze-plagiarism', {
            repo_url: repoUrl,
            language: 'Python',
            max_candidates: 5
        });
        
        console.log('Plagiarism detected:', response.data.plagiarism_detected);
        return response.data;
    } catch (error) {
        console.error('Error:', error.response?.data || error.message);
    }
}

// Usage
checkPlagiarism('https://github.com/username/suspicious-repo');
```

See `nodejs_client_example.js` for a complete Node.js client implementation.

## Plagiarism Detection Thresholds

The API considers plagiarism detected if any of these conditions are met:

- **File Structure Similarity** > 70%
- **README Similarity** > 80%
- **Code Similarity** > 80%

You can modify these thresholds in the `api.py` file.

## Error Handling

All endpoints return appropriate HTTP status codes:

- `200` - Success
- `400` - Bad Request (missing/invalid parameters)
- `500` - Internal Server Error

Error responses include an `error` field with details:

```json
{
    "error": "Internal server error",
    "message": "Detailed error description"
}
```

## Rate Limiting

Be aware of GitHub API rate limits:
- Unauthenticated: 60 requests per hour
- Authenticated: 5,000 requests per hour

The API uses an authenticated GitHub token for better rate limits.
