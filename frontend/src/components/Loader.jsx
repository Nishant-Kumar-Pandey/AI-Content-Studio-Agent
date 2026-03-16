import React from 'react';

const Loader = ({ message = "Generating content..." }) => {
  return (
    <div className="loader-container">
      <div className="spinner"></div>
      <div className="loading-text">{message}</div>
    </div>
  );
};

export default Loader;
