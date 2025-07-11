# Security Setup Guide

## API Token Configuration

Your API tokens are now securely managed through a configuration system that keeps sensitive information out of your source code.

### Files Created:

1. **`config.env`** - Contains your actual API keys (already created with your tokens)
2. **`config.env.template`** - Template file for other users
3. **`config_loader.py`** - Utility to load configuration securely
4. **`.gitignore`** - Updated to exclude sensitive files

### Security Features:

✅ **API tokens moved out of source code**
✅ **config.env excluded from git commits**
✅ **Environment variable support** (for production deployments)
✅ **Fallback authentication** (if tokens fail)
✅ **Template file for easy setup**

### How It Works:

1. **Configuration Loading Priority:**

   - Environment variables (highest priority)
   - config.env file (fallback)
   - Error if neither found

2. **Usage in Code:**

   ```python
   from config_loader import get_github_token, get_gemini_api_key

   # Instead of hardcoded tokens:
   github_token = get_github_token()
   gemini_key = get_gemini_api_key()
   ```

### For Production Deployment:

Set environment variables instead of using config.env:

```bash
export GITHUB_TOKEN="your_token_here"
export GEMINI_API_KEY="your_api_key_here"
```

### For New Users:

1. Copy `config.env.template` to `config.env`
2. Add your actual API keys to `config.env`
3. Never commit `config.env` to version control

### What's Protected:

- ✅ GitHub Personal Access Token
- ✅ Gemini AI API Key
- ✅ Cloned repositories (temporary files)
- ✅ Analysis results cache
- ✅ Python cache files
- ✅ IDE configuration files

### Verification:

Run this to test your configuration:

```bash
python config_loader.py
```

You should see:

```
✅ Configuration loaded successfully
GitHub token: ✅ Found
Gemini API key: ✅ Found
```

Your plagiarism detection system is now secure and ready for production use!
