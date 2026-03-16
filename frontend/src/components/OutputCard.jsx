import React from 'react';

const OutputCard = ({ title, icon, content }) => {
  return (
    <div className="glass-panel output-card">
      <div className="output-header">
        <span className="output-icon">{icon}</span>
        <h3 className="output-title">{title}</h3>
      </div>
      <div className="output-content">
        {content}
      </div>
    </div>
  );
};

export default OutputCard;
