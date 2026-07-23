import React from 'react';

export default function Logo({ size = 30 }) {
  return (
    <svg xmlns="http://www.w3.org/2000/svg" width={size} height={size} viewBox="0 0 30 30" fill="none">
      <path d="M15 2L4 7V15C4 21.3 8.9 27.2 15 28.5C21.1 27.2 26 21.3 26 15V7L15 2Z"
        stroke="#00b4d8" strokeWidth="1.8" strokeLinejoin="round" fill="rgba(0,180,216,0.07)"/>
      <rect x="11" y="11" width="8" height="8" rx="1.5" stroke="#00b4d8" strokeWidth="1.4"/>
      <line x1="15" y1="2" x2="15" y2="11" stroke="#00b4d8" strokeWidth="1.1" strokeDasharray="2 2"/>
      <line x1="15" y1="19" x2="15" y2="28" stroke="#00b4d8" strokeWidth="1.1" strokeDasharray="2 2"/>
    </svg>
  );
}
