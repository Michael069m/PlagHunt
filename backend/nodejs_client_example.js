// Example Node.js client for the Plagiarism Detection API
const axios = require('axios');

const API_BASE_URL = 'http://localhost:5000';

class PlagiarismDetectionClient {
    constructor(baseUrl = API_BASE_URL) {
        this.baseUrl = baseUrl;
    }

    // Check if the API is healthy
    async healthCheck() {
        try {
            const response = await axios.get(`${this.baseUrl}/health`);
            return response.data;
        } catch (error) {
            throw new Error(`Health check failed: ${error.message}`);
        }
    }

    // Analyze a repository for plagiarism
    async analyzePlagiarism(repoUrl, options = {}) {
        try {
            const payload = {
                repo_url: repoUrl,
                language: options.language || 'Python',
                min_stars: options.minStars || 5,
                per_page: options.perPage || 10,
                max_candidates: options.maxCandidates || 5
            };

            const response = await axios.post(`${this.baseUrl}/analyze-plagiarism`, payload);
            return response.data;
        } catch (error) {
            if (error.response) {
                throw new Error(`API Error: ${error.response.data.error || error.response.data.message}`);
            }
            throw new Error(`Request failed: ${error.message}`);
        }
    }

    // Analyze a single repository without plagiarism detection
    async analyzeRepoOnly(repoUrl) {
        try {
            const payload = { repo_url: repoUrl };
            const response = await axios.post(`${this.baseUrl}/analyze-repo-only`, payload);
            return response.data;
        } catch (error) {
            if (error.response) {
                throw new Error(`API Error: ${error.response.data.error || error.response.data.message}`);
            }
            throw new Error(`Request failed: ${error.message}`);
        }
    }

    // Search GitHub repositories
    async searchRepos(keywords, options = {}) {
        try {
            const payload = {
                keywords: keywords,
                topic: options.topic,
                language: options.language,
                exclude_user: options.excludeUser,
                min_stars: options.minStars || 0,
                per_page: options.perPage || 10
            };

            const response = await axios.post(`${this.baseUrl}/search-repos`, payload);
            return response.data;
        } catch (error) {
            if (error.response) {
                throw new Error(`API Error: ${error.response.data.error || error.response.data.message}`);
            }
            throw new Error(`Request failed: ${error.message}`);
        }
    }
}

// Example usage
async function example() {
    const client = new PlagiarismDetectionClient();

    try {
        // Health check
        console.log('Checking API health...');
        const health = await client.healthCheck();
        console.log('✅ API is healthy:', health);

        // Analyze a repository for plagiarism
        console.log('\n🔍 Analyzing repository for plagiarism...');
        const plagiarismResult = await client.analyzePlagiarism(
            'https://github.com/Michael069m/Stock-Price-Predictor-project',
            {
                language: 'Python',
                minStars: 5,
                maxCandidates: 3
            }
        );

        console.log('📊 Plagiarism Analysis Results:');
        console.log(`Suspect Repo: ${plagiarismResult.suspect_repo.name} by ${plagiarismResult.suspect_repo.owner}`);
        console.log(`Topic: ${plagiarismResult.suspect_repo.topic}`);
        console.log(`Keywords: ${plagiarismResult.suspect_repo.keywords.join(', ')}`);
        console.log(`Plagiarism Detected: ${plagiarismResult.plagiarism_detected ? '❗ YES' : '✅ NO'}`);
        console.log(`Candidates Checked: ${plagiarismResult.summary.total_candidates_checked}`);
        console.log(`High Similarity Count: ${plagiarismResult.summary.high_similarity_count}`);

        if (plagiarismResult.analysis_results.length > 0) {
            console.log('\n📋 Detailed Results:');
            plagiarismResult.analysis_results.forEach((result, index) => {
                console.log(`\n${index + 1}. ${result.candidate_repo.name}`);
                console.log(`   URL: ${result.candidate_repo.url}`);
                console.log(`   Stars: ${result.candidate_repo.stars}`);
                console.log(`   Similarities:`);
                console.log(`     - File Structure: ${(result.similarities.file_structure * 100).toFixed(1)}%`);
                console.log(`     - README: ${(result.similarities.readme * 100).toFixed(1)}%`);
                console.log(`     - Code: ${(result.similarities.code * 100).toFixed(1)}%`);
                console.log(`   Plagiarism: ${result.plagiarism_detected ? '❗ YES' : '✅ NO'}`);
            });
        }

    } catch (error) {
        console.error('❌ Error:', error.message);
    }
}

// Express.js route handler example
function createExpressRoutes(app) {
    const client = new PlagiarismDetectionClient();

    // Route to analyze plagiarism
    app.post('/api/check-plagiarism', async (req, res) => {
        try {
            const { repoUrl, language, minStars, maxCandidates } = req.body;

            if (!repoUrl) {
                return res.status(400).json({ error: 'Repository URL is required' });
            }

            const result = await client.analyzePlagiarism(repoUrl, {
                language,
                minStars,
                maxCandidates
            });

            res.json(result);
        } catch (error) {
            console.error('Plagiarism check error:', error.message);
            res.status(500).json({ error: error.message });
        }
    });

    // Route to analyze single repo
    app.post('/api/analyze-repo', async (req, res) => {
        try {
            const { repoUrl } = req.body;

            if (!repoUrl) {
                return res.status(400).json({ error: 'Repository URL is required' });
            }

            const result = await client.analyzeRepoOnly(repoUrl);
            res.json(result);
        } catch (error) {
            console.error('Repo analysis error:', error.message);
            res.status(500).json({ error: error.message });
        }
    });

    // Route to search repositories
    app.post('/api/search-repos', async (req, res) => {
        try {
            const { keywords, ...options } = req.body;

            if (!keywords || !Array.isArray(keywords)) {
                return res.status(400).json({ error: 'Keywords array is required' });
            }

            const result = await client.searchRepos(keywords, options);
            res.json(result);
        } catch (error) {
            console.error('Repo search error:', error.message);
            res.status(500).json({ error: error.message });
        }
    });
}

module.exports = {
    PlagiarismDetectionClient,
    createExpressRoutes
};

// Run example if this file is executed directly
if (require.main === module) {
    example();
}
