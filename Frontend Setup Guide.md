# Frontend Setup Guide

This guide will help you set up and run the LifeFlight dashboard frontend application.

## Prerequisites

- **Node.js**: 14.0 or higher (tested with 18.x and higher)
- Check version: `node --version` and `npm --version`
- Install from [nodejs.org](https://nodejs.org/) or use [nvm](https://github.com/nvm-sh/nvm)

## Installation

### 1. Navigate to Frontend Directory
```bash
cd lifeflight-dashboard-frontend
```

### 2. Install Dependencies
```bash
npm install
```

**Note**: This may take a few minutes depending on your internet connection.

## Running the Application

```bash
npm start
```

This will:
- Start the React development server
- Open browser automatically to `http://localhost:3000`
- Enable hot-reloading (changes will refresh automatically)

Press `Ctrl + C` to stop the server.

## Configuration

### Backend API URL
The frontend connects to the backend API at `http://localhost:5001` by default.

### Port Configuration
Default port is 3000. To use a different port:
```bash
PORT=3001 npm start
```

Or create a `.env` file:
```env
REACT_APP_API_URL=http://localhost:5001
PORT=3000
```

## Available Scripts

- `npm start` - Run development server
- `npm run build` - Build for production
- `npm test` - Run tests

## Troubleshooting

- **Port in use**: `lsof -ti:3000` to find process, or use `PORT=3001 npm start`
- **Install fails**: `npm cache clean --force` then `rm -rf node_modules && npm install`
- **Backend connection**: Verify backend is running: `curl http://localhost:5001/api/test`
- **Module errors**: Delete `node_modules` and reinstall: `rm -rf node_modules && npm install`

## Next Steps

1. Start the backend server (see backend README)
2. Start the frontend server (`npm start`)
3. Open browser to `http://localhost:3000`
