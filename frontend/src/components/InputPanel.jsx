import React, { useState } from 'react';

const InputPanel = ({ onSubmit, isLoading }) => {
  const [topic, setTopic] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    if (topic.trim() && !isLoading) {
      onSubmit(topic);
    }
  };

  return (
    <div className="input-section">
      <div className="glass-panel" style={{ width: '100%' }}>
        <h2 style={{ textAlign: 'center', marginBottom: '1.5rem', fontWeight: 500 }}>
          What do you want to create today?
        </h2>
        
        <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          <div className="input-wrapper">
            <input
              type="text"
              className="topic-input"
              placeholder="e.g., AI in Healthcare, Next.js Tips..."
              value={topic}
              onChange={(e) => setTopic(e.target.value)}
              disabled={isLoading}
            />
          </div>
          
          <button 
            type="submit" 
            className="generate-btn" 
            disabled={!topic.trim() || isLoading}
            style={{ alignSelf: 'center' }}
          >
            {isLoading ? 'Generating ✨' : 'Generate Concept 🚀'}
          </button>
        </form>
      </div>
    </div>
  );
};

export default InputPanel;
