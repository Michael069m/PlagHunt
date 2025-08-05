"""
Configuration loader for API tokens and settings
"""
import os
from typing import Optional

def load_config() -> dict:
    """
    Load configuration from config.env file and environment variables.
    Environment variables take precedence over config file.
    
    Returns:
        dict: Configuration dictionary with API keys
    """
    config = {}
    
    # Try to load from config.env file first (in backend directory)
    backend_dir = os.path.dirname(os.path.dirname(__file__))  # Go up two levels to backend/
    config_file = os.path.join(backend_dir, 'config.env')
    if os.path.exists(config_file):
        try:
            with open(config_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        config[key.strip()] = value.strip()
        except Exception as e:
            print(f"Warning: Could not read config.env: {e}")
    
    # Override with environment variables (these take precedence)
    config['GITHUB_TOKEN'] = os.environ.get('GITHUB_TOKEN', config.get('GITHUB_TOKEN'))
    config['GEMINI_API_KEY'] = os.environ.get('GEMINI_API_KEY', config.get('GEMINI_API_KEY'))
    
    return config

def get_github_token() -> Optional[str]:
    """Get GitHub token from config"""
    config = load_config()
    token = config.get('GITHUB_TOKEN')
    if not token:
        raise ValueError("GitHub token not found. Please set GITHUB_TOKEN in config.env or environment variable.")
    return token

def get_gemini_api_key() -> Optional[str]:
    """Get Gemini API key from config"""
    config = load_config()
    api_key = config.get('GEMINI_API_KEY')
    if not api_key:
        raise ValueError("Gemini API key not found. Please set GEMINI_API_KEY in config.env or environment variable.")
    return api_key

if __name__ == "__main__":
    # Test the configuration loading
    try:
        config = load_config()
        print("✅ Configuration loaded successfully")
        print(f"GitHub token: {'✅ Found' if config.get('GITHUB_TOKEN') else '❌ Missing'}")
        print(f"Gemini API key: {'✅ Found' if config.get('GEMINI_API_KEY') else '❌ Missing'}")
    except Exception as e:
        print(f"❌ Configuration error: {e}")
