import React from 'react';

export default function AshokStambh({ className = "h-14 w-auto" }) {
  return (
    <img 
      src="/emblem.png" 
      alt="State Emblem of India (Ashok Stambh)" 
      className={`${className} object-contain hover:scale-105 transition-all drop-shadow-sm`}
    />
  );
}
