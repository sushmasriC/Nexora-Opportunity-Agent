import React, { useEffect, useRef, useState } from 'react';

interface NetworkBackgroundProps {
  dotCount?: number;
  lineCount?: number;
}

const NetworkBackground: React.FC<NetworkBackgroundProps> = ({ 
  dotCount = 60, 
  lineCount = 40 
}) => {
  const containerRef = useRef<HTMLDivElement>(null);
  const [isVisible, setIsVisible] = useState(false);

  useEffect(() => {
    const container = containerRef.current;
    if (!container) return;

    // Clear existing elements
    container.innerHTML = '';

    // Generate dots with more varied sizes and colors
    const dots: Array<{ x: number; y: number; element: HTMLDivElement }> = [];
    for (let i = 0; i < dotCount; i++) {
      const dot = document.createElement('div');
      dot.className = 'network-dot';
      
      const x = Math.random() * 100;
      const y = Math.random() * 100;
      const size = 2 + Math.random() * 4; // Vary dot sizes
      const opacity = 0.3 + Math.random() * 0.7; // Vary opacity
      
      dot.style.left = `${x}%`;
      dot.style.top = `${y}%`;
      dot.style.width = `${size}px`;
      dot.style.height = `${size}px`;
      dot.style.opacity = opacity.toString();
      dot.style.animationDelay = `${Math.random() * 3}s`;
      dot.style.animationDuration = `${3 + Math.random() * 2}s`;
      
      // Add some color variation
      const colors = ['#60a5fa', '#3b82f6', '#93c5fd', '#dbeafe'];
      const color = colors[Math.floor(Math.random() * colors.length)];
      dot.style.background = color;
      dot.style.boxShadow = `0 0 10px ${color}, 0 0 20px ${color}, 0 0 30px ${color}`;
      
      container.appendChild(dot);
      dots.push({ x, y, element: dot });
    }

    // Generate lines connecting nearby dots
    const lines: HTMLDivElement[] = [];
    for (let i = 0; i < lineCount; i++) {
      const dot1 = dots[Math.floor(Math.random() * dots.length)];
      const dot2 = dots[Math.floor(Math.random() * dots.length)];
      
      if (dot1 === dot2) continue;

      const distance = Math.sqrt(
        Math.pow(dot2.x - dot1.x, 2) + Math.pow(dot2.y - dot1.y, 2)
      );

      // Only connect dots that are reasonably close
      if (distance < 35) {
        const line = document.createElement('div');
        line.className = 'network-line';
        
        const angle = Math.atan2(dot2.y - dot1.y, dot2.x - dot1.x) * 180 / Math.PI;
        const length = distance * window.innerWidth / 100;
        const opacity = 0.2 + Math.random() * 0.6;
        
        line.style.left = `${dot1.x}%`;
        line.style.top = `${dot1.y}%`;
        line.style.width = `${length}px`;
        line.style.transform = `rotate(${angle}deg)`;
        line.style.opacity = opacity.toString();
        line.style.animationDelay = `${Math.random() * 4}s`;
        line.style.animationDuration = `${4 + Math.random() * 2}s`;
        
        // Add some color variation to lines
        const colors = ['#60a5fa', '#3b82f6', '#93c5fd'];
        const color = colors[Math.floor(Math.random() * colors.length)];
        line.style.background = `linear-gradient(90deg, transparent, ${color}, transparent)`;
        line.style.boxShadow = `0 0 5px ${color}`;
        
        container.appendChild(line);
        lines.push(line);
      }
    }

    // Add floating animation to dots
    dots.forEach((dot, index) => {
      dot.element.style.animation += `, float ${6 + Math.random() * 4}s ease-in-out infinite`;
      dot.element.style.animationDelay += `, ${Math.random() * 6}s`;
    });

    // Animate lines appearing
    lines.forEach((line, index) => {
      line.style.animation += `, connect ${2 + Math.random() * 3}s ease-in-out infinite`;
      line.style.animationDelay += `, ${Math.random() * 5}s`;
    });

    // Show the network after a short delay
    setTimeout(() => setIsVisible(true), 100);

    // Cleanup function
    return () => {
      if (container) {
        container.innerHTML = '';
      }
    };
  }, [dotCount, lineCount]);

  return (
    <div 
      ref={containerRef} 
      className="network-bg" 
      style={{ 
        opacity: isVisible ? 1 : 0,
        transition: 'opacity 2s ease-in-out'
      }} 
    />
  );
};

export default NetworkBackground;
