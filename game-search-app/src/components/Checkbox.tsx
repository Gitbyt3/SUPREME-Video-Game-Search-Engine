import React, { useState, useEffect, useCallback } from 'react';

const Checkbox: React.FC<{checked: boolean, onChange: (checked: boolean, ev: React.MouseEvent<HTMLDivElement>) => void, size?: number}> = ({checked, onChange, size = 14}) => {
  const handleToggle = useCallback((ev: React.MouseEvent<HTMLDivElement>) => {
    onChange(!checked, ev);
  }, [onChange, checked]);
  
  return <div className={['checkbox', checked ? 'checked' : ''].filter(x => x).join(' ')} style={{'--size': `${size}px`} as React.CSSProperties} onClick={handleToggle}>
    <div></div>
  </div>;
};

export default Checkbox;