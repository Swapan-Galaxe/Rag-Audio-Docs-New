import React, { useState } from 'react';
import './App.css';

function App() {
  const [files, setFiles] = useState([]);
  const [summaryType, setSummaryType] = useState('concise');
  const [query, setQuery] = useState('');
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState(null);

  const API_URL = process.env.REACT_APP_API_URL || '';

  // Test connection on mount
  React.useEffect(() => {
    fetch(`${API_URL}/health`)
      .then(res => res.json())
      .then(data => console.log('API Connected:', data))
      .catch(err => console.error('API Connection Failed:', err));
  }, []);

  const handleFileChange = (e) => {
    setFiles(Array.from(e.target.files));
    setError(null);
  };

  const handleProcess = async () => {
    if (files.length === 0) {
      setError('Please select at least one file');
      return;
    }

    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const results = [];
      
      for (const file of files) {
        const formData = new FormData();
        formData.append('file', file);
        formData.append('summary_type', summaryType);
        if (query) formData.append('query', query);

        const response = await fetch(`${API_URL}/process`, {
          method: 'POST',
          body: formData,
        });

        const data = await response.json();
        
        if (data.error) {
          results.push({ filename: file.name, error: data.error });
        } else {
          results.push(data);
        }
      }
      
      setResult({ files: results });
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = async () => {
    if (!searchQuery) {
      setError('Please enter a search query');
      return;
    }

    setLoading(true);
    setError(null);
    setSearchResults(null);

    try {
      const response = await fetch(`${API_URL}/query`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: searchQuery, k: 5 }),
      });

      if (!response.ok) throw new Error('Search failed');

      const data = await response.json();
      setSearchResults(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="App">
      <header className="header">
        <h1>🤖 RAG Pipeline</h1>
        <p>AI-Powered Document Summarization</p>
      </header>

      <div className="container">
        <div className="card">
          <h2>📄 Upload & Process Document</h2>
          
          <div className="form-group">
            <label>Select Files:</label>
            <input type="file" onChange={handleFileChange} accept=".pdf,.docx,.txt,.mp3,.wav" multiple />
            {files.length > 0 && <span className="file-name">Selected: {files.length} file(s)</span>}
          </div>

          <div className="form-group">
            <label>Summary Type:</label>
            <select value={summaryType} onChange={(e) => setSummaryType(e.target.value)}>
              <option value="concise">Concise</option>
              <option value="detailed">Detailed</option>
              <option value="bullet_points">Bullet Points</option>
            </select>
          </div>

          <div className="form-group">
            <label>Query (Optional):</label>
            <input
              type="text"
              placeholder="e.g., What are the key findings?"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
            />
          </div>

          <button onClick={handleProcess} disabled={loading} className="btn-primary">
            {loading ? 'Processing...' : 'Process Document'}
          </button>
        </div>

        <div className="card">
          <h2>🔍 Search Documents</h2>
          
          <div className="form-group">
            <input
              type="text"
              placeholder="Search for specific information..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
            />
          </div>

          <button onClick={handleSearch} disabled={loading} className="btn-secondary">
            {loading ? 'Searching...' : 'Search'}
          </button>
        </div>

        {error && (
          <div className="alert alert-error">
            ❌ {error}
          </div>
        )}

        {result && (
          <div className="card result-card">
            <h2>✅ Summary Results</h2>
            {result.files.map((item, index) => (
              <div key={index} className="file-result">
                <h3>📄 {item.filename}</h3>
                {item.error ? (
                  <div className="alert alert-error">Error: {item.error}</div>
                ) : (
                  <>
                    <div className="result-meta">
                      <span><strong>Type:</strong> {item.summary_type}</span>
                    </div>
                    <div className="result-content">
                      <p>{item.summary}</p>
                    </div>
                  </>
                )}
              </div>
            ))}
          </div>
        )}

        {searchResults && (
          <div className="card result-card">
            <h2>🔍 Search Results</h2>
            <p className="result-count">{searchResults.results.length} results found</p>
            {searchResults.results.map((item, index) => (
              <div key={index} className="search-result-item">
                <div className="result-header">
                  <strong>Result {index + 1}</strong>
                  {item.metadata?.source && (
                    <span className="source">Source: {item.metadata.source}</span>
                  )}
                </div>
                <p>{item.content}</p>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

export default App;
