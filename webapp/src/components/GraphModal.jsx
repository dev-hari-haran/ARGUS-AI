import React, { useState } from 'react';
import { X, ZoomIn, ZoomOut, Maximize, Minimize } from 'lucide-react';

const GraphModal = ({ isOpen, onClose, children, title }) => {
  const [scale, setScale] = useState(1);

  if (!isOpen) return null;

  const handleZoomIn = () => setScale(prev => Math.min(prev + 0.2, 3));
  const handleZoomOut = () => setScale(prev => Math.max(prev - 0.2, 0.5));
  const handleFitWidth = () => setScale(1); // Standard scale
  const handleFitHeight = () => setScale(0.8); // Slightly smaller to fit height

  return (
    <div style={{
      position: 'fixed',
      top: 0, left: 0, right: 0, bottom: 0,
      backgroundColor: 'rgba(15, 23, 42, 0.95)',
      zIndex: 9999,
      display: 'flex',
      flexDirection: 'column',
      backdropFilter: 'blur(10px)'
    }}>
      {/* Toolbar */}
      <div style={{
        display: 'flex', justifyContent: 'space-between', alignItems: 'center',
        padding: '1rem 2rem', borderBottom: '1px solid var(--border-color)',
        backgroundColor: 'var(--bg-primary)'
      }}>
        <h3 style={{ margin: 0, color: 'var(--text-primary)' }}>{title || "Graph View"}</h3>
        <div style={{ display: 'flex', gap: '1rem' }}>
          <button onClick={handleZoomIn} className="btn-icon" title="Zoom In"><ZoomIn size={20} /></button>
          <button onClick={handleZoomOut} className="btn-icon" title="Zoom Out"><ZoomOut size={20} /></button>
          <button onClick={handleFitWidth} className="btn-icon" title="Fit Width"><Maximize size={20} /></button>
          <button onClick={handleFitHeight} className="btn-icon" title="Fit Height"><Minimize size={20} /></button>
          <div style={{ width: '1px', backgroundColor: 'var(--border-color)', margin: '0 0.5rem' }}></div>
          <button onClick={onClose} className="btn-icon" title="Close"><X size={20} color="#ef4444" /></button>
        </div>
      </div>

      {/* Content Area */}
      <div style={{
        flex: 1,
        overflow: 'auto',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        padding: '2rem'
      }}>
        <div style={{
          transform: `scale(${scale})`,
          transition: 'transform 0.2s ease-out',
          width: '100%',
          maxWidth: '1200px',
          height: '80vh',
          backgroundColor: 'var(--bg-card)',
          padding: '2rem',
          borderRadius: '1rem',
          boxShadow: '0 25px 50px -12px rgba(0, 0, 0, 0.5)',
          display: 'flex',
          flexDirection: 'column'
        }}>
          {children}
        </div>
      </div>
    </div>
  );
};

export default GraphModal;
