import React, { useState, useEffect } from 'react';

const Typewriter: React.FC<{ text: string, speed?: number, html?: string }> = ({ text, speed = 30, html }) => {
  const [displayIndex, setDisplayIndex] = useState(0);
  const displayText = text.slice(0, displayIndex);

  useEffect(() => {
    const timer = setInterval(() => {
      setDisplayIndex(displayIndex + 1);
      if (displayIndex >= text.length) {
        clearInterval(timer);
      }
    }, speed);
    return () => clearInterval(timer);
  }, [text, displayIndex, speed]);

  return (
    <div className="typewriter-container">
      {displayText}
      <span className='typewriter'></span>
    </div>
  );
};

export default Typewriter;
