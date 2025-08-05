# PlagHunt - Advanced Plagiarism Detection System

A modern plagiarism detection system built with **React 19** frontend and **Flask + MongoDB** backend.

## 🚀 Quick Start

### Prerequisites

1. **Python 3.8+** installed
2. **Node.js 18+** and npm installed
3. **MongoDB** installed and running
4. **Git** installed

### 1. Install MongoDB (if not installed)

```bash
# macOS with Homebrew
brew tap mongodb/brew
brew install mongodb-community
brew services start mongodb-community
```

### 2. Clone and Setup

```bash
git clone <your-repo-url>
cd PlagHunt
```

### 3. One-Command Startup

```bash
# Start everything with one command
./start_plaghunt.sh
```

This will automatically:

- Start MongoDB (if not running)
- Install backend dependencies in virtual environment
- Install frontend dependencies
- Start backend on http://localhost:5001
- Start frontend on http://localhost:5174

### 4. Manual Setup (Alternative)

#### Backend Setup

```bash
cd backend
# Use the virtual environment python directly
venv/bin/python app.py
```

#### Frontend Setup (in new terminal)

```bash
cd frontend
npm run dev
```

## 🔧 Configuration

### Required API Keys

1. **GitHub Token**: Get from https://github.com/settings/tokens
2. **Gemini AI Key**: Get from https://aistudio.google.com/app/apikey

### Setup Configuration

Edit `backend/config.env` and add your API keys:

```env
# GitHub Personal Access Token
GITHUB_TOKEN=your_github_token_here

# Gemini AI API Key
GEMINI_API_KEY=your_gemini_api_key_here
```

## 🌟 Features

- **User Authentication**: Secure JWT-based authentication
- **Repository Analysis**: Analyze GitHub repositories for potential plagiarism
- **Smart Search**: AI-powered candidate repository discovery
- **History Tracking**: Keep track of all your analyses
- **Modern UI**: Beautiful React 19 interface with Tailwind CSS
- **Real-time Results**: Live analysis results and progress tracking

## 🛠️ Technology Stack

### Backend

- **Flask**: Python web framework
- **MongoDB**: NoSQL database
- **JWT**: Authentication
- **Gemini AI**: Code analysis
- **GitHub API**: Repository data
- **scikit-learn**: Text similarity analysis

### Frontend

- **React 19**: Latest React with new features
- **Tailwind CSS**: Utility-first CSS framework
- **Axios**: HTTP client
- **React Router**: Navigation
- **Lucide Icons**: Modern icon library

## 📊 API Endpoints

### Authentication

- `POST /api/auth/register` - User registration
- `POST /api/auth/login` - User login
- `GET /api/auth/verify` - Token verification

### Plagiarism Detection

- `POST /api/plagiarism/analyze` - Analyze repository
- `GET /api/plagiarism/history` - Get analysis history
- `GET /api/plagiarism/result/<id>` - Get specific result
- `DELETE /api/plagiarism/result/<id>` - Delete result

### Health Check

- `GET /api/health` - Service health status

## 🚧 Recent Fixes & Improvements

- ✅ Fixed Google Generative AI import issues
- ✅ Corrected config file path resolution
- ✅ Updated frontend to use proper App component
- ✅ Added comprehensive error handling
- ✅ Created automated startup scripts
- ✅ Fixed authentication middleware
- ✅ Simplified plagiarism analysis for reliability
- ✅ Updated dependencies to latest versions
- ✅ Added proper virtual environment support

## 🔍 How It Works

1. **User Registration/Login**: Create account or sign in
2. **Repository Submission**: Enter GitHub repository URL
3. **Candidate Discovery**: System searches for similar repositories
4. **Analysis**: AI analyzes code similarity and structure
5. **Results**: Get detailed plagiarism report with similarity scores
6. **History**: View and manage all previous analyses

## 🛡️ Security Features

- JWT token-based authentication
- Password hashing with bcrypt
- API rate limiting
- Input validation and sanitization
- CORS protection

## 📝 Development Notes

- Backend runs on port 5001 (changed from 5000 due to macOS AirPlay conflict)
- Frontend runs on port 5174 (Vite auto-increments if 5173 is busy)
- MongoDB runs on default port 27017
- All dependencies are managed with virtual environments

## 🚀 Deployment

For production deployment, see the included Docker files and deployment scripts:

- `backend/Dockerfile`
- `frontend/Dockerfile`
- `backend/deploy_production.sh`

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

### 3. Start Backend

```bash
cd backend
chmod +x start_backend.sh
./start_backend.sh
```

The backend will:

- Create a virtual environment
- Install Python dependencies
- Start the Flask server on `http://localhost:5000`

### 4. Start Frontend (in a new terminal)

```bash
cd frontend
chmod +x start_frontend.sh
./start_frontend.sh
```

The frontend will:

- Install Node.js dependencies
- Start the React dev server on `http://localhost:5173`

## 🎨 Features

### Frontend (React 19)

- ✅ **Modern UI** - Black background with yellow/red accents
- ✅ **Authentication** - Login/Register with JWT
- ✅ **React 19 Features**:
  - `useActionState` for form handling
  - `useOptimistic` for optimistic UI updates
  - `use()` hook for data fetching
- ✅ **Dashboard** - GitHub URL input and analysis history
- ✅ **Responsive Design** - Works on all devices

### Backend (Flask + MongoDB)

- ✅ **RESTful API** - Clean API endpoints
- ✅ **Authentication** - JWT-based auth with bcrypt
- ✅ **MongoDB Integration** - User data and analysis history
- ✅ **Plagiarism Analysis** - GitHub repository analysis
- ✅ **History Management** - Save and retrieve analysis results

## 🔧 Configuration

### Backend Environment Variables

Create or edit `backend/config.env`:

```env
# MongoDB Configuration
MONGODB_URI=mongodb://localhost:27017/
DB_NAME=plagiarism_detector

# JWT Configuration
JWT_SECRET_KEY=your-super-secret-jwt-key-change-in-production

# GitHub API Configuration
GITHUB_TOKEN=your_github_token_here

# Google AI Configuration (Optional)
GOOGLE_API_KEY=your_google_api_key_here

# Flask Configuration
FLASK_ENV=development
FLASK_DEBUG=True
```

### Frontend Configuration

The frontend automatically connects to `http://localhost:5000` for the backend API.

## 📱 Usage

1. **Open your browser** to `http://localhost:5173`
2. **Register** a new account or **login**
3. **Enter a GitHub repository URL** in the dashboard
4. **Select the programming language**
5. **Click "Start Analysis"** to begin plagiarism detection
6. **View results** and check your **analysis history**

## 🛠️ Manual Setup (if scripts don't work)

### Backend Setup

```bash
cd backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Start the server
python app.py
```

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Upgrade to React 19 (if needed)
npm install react@19 react-dom@19

# Start development server
npm run dev
```

## 🔍 API Endpoints

### Authentication

- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login user
- `POST /api/auth/refresh` - Refresh token

### Plagiarism Analysis

- `POST /api/plagiarism/analyze` - Analyze repository
- `GET /api/plagiarism/history` - Get analysis history
- `GET /api/plagiarism/result/<id>` - Get specific result
- `DELETE /api/plagiarism/result/<id>` - Delete result

### Health Check

- `GET /api/health` - Check API status

## 🐛 Troubleshooting

### MongoDB Connection Issues

```bash
# Check if MongoDB is running
brew services list | grep mongodb

# Start MongoDB
brew services start mongodb-community

# Check MongoDB status
mongosh --eval "db.runCommand('ping')"
```

### Python Dependencies Issues

```bash
# Update pip
pip install --upgrade pip

# Clear pip cache
pip cache purge

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

### Node.js Issues

```bash
# Clear npm cache
npm cache clean --force

# Delete node_modules and reinstall
rm -rf node_modules package-lock.json
npm install
```

### Port Already in Use

```bash
# Kill process on port 5000 (backend)
lsof -ti:5000 | xargs kill -9

# Kill process on port 5173 (frontend)
lsof -ti:5173 | xargs kill -9
```

## 🚀 Production Deployment

### Backend

1. Set `FLASK_ENV=production` in config.env
2. Change `JWT_SECRET_KEY` to a secure random string
3. Update MongoDB URI for production database
4. Use a WSGI server like Gunicorn

### Frontend

1. Build the production version: `npm run build`
2. Serve the `dist` folder with a web server
3. Update API URL in production

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🆘 Support

If you encounter any issues:

1. Check the troubleshooting section above
2. Ensure all prerequisites are installed
3. Check that MongoDB is running
4. Verify environment variables are set correctly

---

**Happy Coding! 🎉**
