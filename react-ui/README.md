# React UI Setup & Run

## Quick Start

### 1. Install Backend Dependencies
```bash
cd c:\rag_pipeline
py -m pip install flask-cors
```

### 2. Start Backend API Server
```bash
py api_server.py
```
Server runs on: http://localhost:8000

### 3. Install Frontend Dependencies
Open a NEW terminal:
```bash
cd c:\rag_pipeline\react-ui
npm install
```

### 4. Start React App
```bash
npm start
```
App opens at: http://localhost:3000

## Features

✅ **Upload Documents** - PDF, DOCX, TXT, MP3, WAV
✅ **Choose Summary Type** - Concise, Detailed, Bullet Points
✅ **Optional Query** - Ask specific questions
✅ **Search Documents** - Query processed documents
✅ **Real-time Results** - See summaries instantly

## Usage

1. **Process Document:**
   - Click "Select File" and choose a document
   - Select summary type (concise/detailed/bullet_points)
   - Optionally add a query
   - Click "Process Document"

2. **Search Documents:**
   - Enter search query
   - Click "Search"
   - View relevant document chunks

## Troubleshooting

**CORS Error:**
```bash
py -m pip install flask-cors
```

**Port 3000 in use:**
```bash
# React will ask to use another port, press Y
```

**Backend not responding:**
- Ensure API server is running on port 8000
- Check .env file has Azure credentials

## File Structure

```
react-ui/
├── public/
│   └── index.html
├── src/
│   ├── App.js          # Main component
│   ├── App.css         # Styles
│   ├── index.js        # Entry point
│   └── index.css       # Global styles
└── package.json        # Dependencies
```

## Build for Production

```bash
cd react-ui
npm run build
```

Deploy the `build/` folder to any static hosting service.
