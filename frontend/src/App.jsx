import { useState } from 'react';
import InputPanel from './components/InputPanel';
import OutputCard from './components/OutputCard';
import Loader from './components/Loader';
import TalkPanel from './components/TalkPanel';
import './index.css';

// Using Vite env variables or fallback to local
const API_BASE = import.meta.env.VITE_API_URL || "http://localhost:8080";
const GENERATE_URL = `${API_BASE}/generate`;

function App() {
  const [isLoading, setIsLoading] = useState(false);
  const [results, setResults] = useState(null);
  const [error, setError] = useState(null);
  const [activeTab, setActiveTab] = useState('studio'); // 'studio' or 'talk'

  const handleGenerate = async (topic) => {
    setIsLoading(true);
    setResults(null);
    setError(null);
    setActiveTab('studio'); // Switch to studio view to show results
    
    try {
      const response = await fetch(GENERATE_URL, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ topic }),
      });
      
      if (response.status === 429) {
        setError("🚨 API Quota Reached! You've hit the daily free limit. Please try again tomorrow or link a billing account.");
        return;
      }

      if (!response.ok) {
        throw new Error(`Error: ${response.statusText}`);
      }
      
      const data = await response.json();
      
      // Secondary check for quota message inside data
      if (data.script && data.script.includes("Quota Reached")) {
        setError("🚨 API Quota Reached! Please wait for the daily reset.");
        return;
      }

      setResults(data);
    } catch (err) {
      console.error("Failed to generate content:", err);
      setError("Failed to connect to the AI Agent. Please try again.");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="app-container">
      <header>
        <h1>AI Content Studio</h1>
        <p className="subtitle">From idea to full social package in seconds</p>
      </header>
      
      <div className="mode-toggle">
        <button 
          className={`toggle-btn ${activeTab === 'studio' ? 'active' : ''}`}
          onClick={() => setActiveTab('studio')}
        >
          Studio Mode 🎬
        </button>
        <button 
          className={`toggle-btn ${activeTab === 'talk' ? 'active' : ''}`}
          onClick={() => setActiveTab('talk')}
        >
          Talk Mode 🗣️
        </button>
      </div>

      <main>
        {activeTab === 'studio' ? (
          <>
            <InputPanel onSubmit={handleGenerate} isLoading={isLoading} />
            
            {isLoading && <Loader message="Agents are crafting your content..." />}
            
            {error && <div className="error-message">{error}</div>}
            
            {results && (
              <div className="results-grid">
                <OutputCard 
                  title="Video Script" 
                  icon="🎬" 
                  content={results.script} 
                />
                <OutputCard 
                  title="Caption" 
                  icon="📝" 
                  content={results.caption} 
                />
                <OutputCard 
                  title="Hashtags" 
                  icon="🏷️" 
                  content={results.hashtags} 
                />
                <OutputCard 
                  title="Thumbnail Idea" 
                  icon="🖼️" 
                  content={results.thumbnail} 
                />
              </div>
            )}
          </>
        ) : (
          <TalkPanel onGenerate={handleGenerate} />
        )}
      </main>
    </div>
  );
}

export default App;
