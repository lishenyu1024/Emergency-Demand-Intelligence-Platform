# Backend Setup Guide

This guide will help you set up and run the LifeFlight backend server.

## Prerequisites

- **Python**: 3.8 or higher (tested with 3.12.3)
- Check version: `python3 --version`

## Installation

### 1. Navigate to Backend Directory
```bash
cd backend
```

### 2. Create and Activate Virtual Environment
```bash
# Create virtual environment
python3 -m venv venv

# Activate (macOS/Linux)
source venv/bin/activate

# Activate (Windows)
venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
pip install joblib prophet  # Additional dependencies
```

## Running the Server

```bash
# Ensure virtual environment is activated
source venv/bin/activate  # macOS/Linux

# Run the server
python app.py
```

The server will start on **port 5001** by default.

Verify it's running:
```bash
curl http://localhost:5001/api/test
```

## Configuration

Create a `.env` file (optional):
```env
FLASK_ENV=development
FLASK_DEBUG=True
PORT=5001
```

## Troubleshooting

- **Port in use**: `lsof -ti:5001` to find process, or use `export PORT=5002`
- **Missing dependencies**: Ensure `joblib` and `prophet` are installed
- **Import errors**: Reinstall dependencies: `pip install -r requirements.txt`

## Next Steps

1. Start the frontend server
2. Frontend connects to `http://localhost:5001` by default
3. Open browser to `http://localhost:3000`
