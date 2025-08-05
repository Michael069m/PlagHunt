# GitHub Repository Plagiarism Detection System

A comprehensive, production-ready plagiarism detection system that analyzes GitHub repositories for potential code plagiarism using AI-powered similarity analysis and advanced comparison algorithms.

## Features

### 🔍 Core Detection Capabilities

- **Repository Analysis**: Automated extraction of keywords, topics, and metadata from suspect repositories
- **GitHub Search**: Advanced search with date filtering to find candidate repositories
- **Multi-layered Comparison**:
  - File structure similarity analysis
  - README content comparison using TF-IDF cosine similarity
  - Code file similarity analysis across common files
- **Date-based Filtering**: Automatically excludes repositories created after the suspect repository

### 🛡️ Security & Production Features

- **Secure Token Management**: API tokens stored in environment files (not in source code)
- **Fallback Authentication**: Graceful degradation when API tokens are invalid
- **Error Handling**: Comprehensive error handling and logging
- **Rate Limit Management**: Efficient API usage with chunked search queries

### 🚀 Deployment Options

- **CLI Tool**: Direct command-line interface for quick analysis
- **REST API**: Flask-based API for integration with web applications
- **Node.js Integration**: Ready-to-use client examples for backend integration

## Quick Start

### 1. Installation

```bash
# Clone the repository
git clone <repository-url>
cd Plagiarism_detector

# Install Python dependencies
pip install -r requirements.txt

# Install Node.js dependencies (for client examples)
npm install
```

### 2. Configuration

Copy the configuration template and add your API tokens:

```bash
cp config.env.template config.env
```

Edit `config.env` and add your tokens:

```env
GITHUB_TOKEN=your_github_token_here
GEMINI_API_KEY=your_gemini_api_key_here
```

### 3. Usage

#### CLI Analysis

```bash
python main.py
```

#### API Server

```bash
python api.py
```

#### Node.js Integration

```bash
node nodejs_client_example.js
```

## API Documentation

### Endpoints

#### Health Check

```http
GET /health
```

#### Analyze Repository for Plagiarism

```http
POST /analyze-plagiarism
Content-Type: application/json

{
  "repo_url": "https://github.com/username/repo",
  "language": "Python",
  "min_stars": 5,
  "per_page": 10,
  "max_candidates": 5
}
```

#### Analyze Single Repository

```http
POST /analyze-repo
Content-Type: application/json

{
  "repo_url": "https://github.com/username/repo"
}
```

#### Search GitHub Repositories

```http
POST /search-repos
Content-Type: application/json

{
  "keywords": ["react", "portfolio"],
  "topic": "portfolio website",
  "language": "JavaScript",
  "exclude_user": "username",
  "min_stars": 5,
  "per_page": 10,
  "created_before": "2023-01-01"
}
```

For detailed API documentation, see [API_README.md](API_README.md).

## Architecture

### Core Modules

- **`analyze_repo.py`**: Repository analysis and metadata extraction using Gemini AI
- **`github_search.py`**: GitHub API integration with advanced search capabilities
- **`compare_utils.py`**: Similarity analysis algorithms (TF-IDF, cosine similarity)
- **`repo_utils.py`**: Git repository management utilities
- **`config_loader.py`**: Secure configuration and token management
- **`api.py`**: Flask REST API server

### Security Framework

- **Token Security**: API tokens stored in `config.env` (excluded from version control)
- **Fallback Authentication**: Graceful degradation for invalid tokens
- **Input Validation**: Comprehensive validation for all API endpoints
- **Error Sanitization**: Safe error messages without sensitive information exposure

## Detection Algorithm

The system uses a multi-layered approach to detect potential plagiarism:

1. **Repository Metadata Analysis**: Extract keywords, topics, and creation dates
2. **Candidate Discovery**: Search GitHub for repositories with similar characteristics
3. **Date Filtering**: Exclude repositories created after the suspect repository
4. **Similarity Analysis**:
   - **File Structure**: Compare directory structures and file names
   - **Content Analysis**: TF-IDF cosine similarity for text content
   - **Code Comparison**: Multi-file code similarity analysis

### Detection Thresholds

- **File Structure Similarity**: > 70% overlap triggers flag
- **README Similarity**: > 80% cosine similarity triggers flag
- **Code Similarity**: > 80% average similarity triggers flag

## Configuration

### Environment Variables

| Variable         | Description                  | Required |
| ---------------- | ---------------------------- | -------- |
| `GITHUB_TOKEN`   | GitHub Personal Access Token | Yes      |
| `GEMINI_API_KEY` | Google Gemini AI API Key     | Yes      |

### Search Parameters

| Parameter        | Description                   | Default |
| ---------------- | ----------------------------- | ------- |
| `min_stars`      | Minimum repository stars      | 5       |
| `per_page`       | Results per search page       | 10      |
| `max_candidates` | Maximum candidates to analyze | 5       |

## Security Considerations

- **Never commit API tokens** to version control
- Use environment variables or secure configuration files
- Regularly rotate API tokens
- Monitor API usage and rate limits
- Validate all user inputs

For detailed security information, see [SECURITY.md](SECURITY.md).

## Development

### Running Tests

```bash
python test_api.py
```

### Code Style

The project follows PEP 8 Python style guidelines with comprehensive docstrings and type hints.

### Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## Dependencies

### Python Dependencies

- `flask`: Web framework for REST API
- `flask-cors`: CORS support for web integration
- `requests`: HTTP client for GitHub API
- `scikit-learn`: Machine learning algorithms for similarity analysis
- `gitpython`: Git repository operations
- `python-dotenv`: Environment variable management

### Optional Dependencies

- `google-generativeai`: Gemini AI integration (for enhanced analysis)

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For issues, questions, or contributions, please:

1. Check existing issues in the GitHub repository
2. Create a new issue with detailed information
3. Follow the contribution guidelines

## Roadmap

- [ ] Machine learning model training for improved detection
- [ ] Support for additional version control systems
- [ ] Advanced code structure analysis
- [ ] Real-time monitoring dashboard
- [ ] Integration with CI/CD pipelines
