import React from 'react';
import Typewriter from './Typewriter';
const LoadingAnimation: React.FC = () => {
  return (
    <div className="loading-container">
      <div className="loading-text"><Typewriter text="Connecting to Pantheon..." /></div>
      <div className="loading-bar">
        <div className="loading-bar-inner"></div>
      </div>
    </div>
  );
};

export default LoadingAnimation;
