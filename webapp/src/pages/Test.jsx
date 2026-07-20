import React, { useState, useRef, useEffect, useCallback } from 'react';
import { ChevronLeft, ChevronRight, Activity, ZoomIn, ZoomOut, Maximize } from 'lucide-react';

const Test = () => {
  const [x, setX] = useState(2.0);
  const [y, setY] = useState(2.0);
  const [l1, setL1] = useState(2.0);
  const [l2, setL2] = useState(2.0);
  
  const [solution, setSolution] = useState(null);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);

  const canvasRef = useRef(null);
  
  // Camera state: offset is in world units, zoom is px per world unit
  const cameraRef = useRef({ offsetX: 0, offsetY: 0, zoom: 60 });
  const isPanning = useRef(false);
  const panStart = useRef({ x: 0, y: 0 });

  const handleSolve = async () => {
    setLoading(true);
    setError(null);
    setSolution(null);
    
    try {
      const res = await fetch("http://127.0.0.1:5000/predict", {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({ x: Number(x), y: Number(y), l1: Number(l1), l2: Number(l2) })
      });
      
      const data = await res.json();
      
      if (data.error) {
        setError(data.error);
      } else if (data.solution) {
        setSolution(data.solution);
      }
    } catch (err) {
      setError("Failed to connect to backend server. Make sure Python server is running.");
    } finally {
      setLoading(false);
    }
  };

  const drawScene = useCallback(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    const W = canvas.width;
    const H = canvas.height;
    const cam = cameraRef.current;
    
    ctx.clearRect(0, 0, W, H);
    
    // Fill background
    ctx.fillStyle = '#0f0f0f';
    ctx.fillRect(0, 0, W, H);

    // World-to-screen helper
    const toScreenX = (wx) => W / 2 + (wx - cam.offsetX) * cam.zoom;
    const toScreenY = (wy) => H / 2 - (wy - cam.offsetY) * cam.zoom;
    
    // --- Infinite Grid ---
    // Determine a nice grid step based on zoom level
    const rawStep = 80 / cam.zoom; // target ~80px spacing
    const magnitude = Math.pow(10, Math.floor(Math.log10(rawStep)));
    const residual = rawStep / magnitude;
    let gridStep;
    if (residual <= 1.5) gridStep = magnitude;
    else if (residual <= 3.5) gridStep = 2 * magnitude;
    else if (residual <= 7.5) gridStep = 5 * magnitude;
    else gridStep = 10 * magnitude;
    
    // Compute visible world bounds
    const worldLeft = cam.offsetX - W / (2 * cam.zoom);
    const worldRight = cam.offsetX + W / (2 * cam.zoom);
    const worldBottom = cam.offsetY - H / (2 * cam.zoom);
    const worldTop = cam.offsetY + H / (2 * cam.zoom);
    
    const startX = Math.floor(worldLeft / gridStep) * gridStep;
    const endX = Math.ceil(worldRight / gridStep) * gridStep;
    const startY = Math.floor(worldBottom / gridStep) * gridStep;
    const endY = Math.ceil(worldTop / gridStep) * gridStep;

    // Sub-grid (finer lines)
    const subStep = gridStep / 5;
    ctx.beginPath();
    ctx.strokeStyle = 'rgba(255, 255, 255, 0.04)';
    ctx.lineWidth = 1;
    for (let wx = Math.floor(worldLeft / subStep) * subStep; wx <= worldRight; wx += subStep) {
      const sx = toScreenX(wx);
      ctx.moveTo(sx, 0);
      ctx.lineTo(sx, H);
    }
    for (let wy = Math.floor(worldBottom / subStep) * subStep; wy <= worldTop; wy += subStep) {
      const sy = toScreenY(wy);
      ctx.moveTo(0, sy);
      ctx.lineTo(W, sy);
    }
    ctx.stroke();

    // Major grid lines
    ctx.beginPath();
    ctx.strokeStyle = 'rgba(255, 255, 255, 0.12)';
    ctx.lineWidth = 1;
    for (let wx = startX; wx <= endX; wx += gridStep) {
      const sx = toScreenX(wx);
      ctx.moveTo(sx, 0);
      ctx.lineTo(sx, H);
    }
    for (let wy = startY; wy <= endY; wy += gridStep) {
      const sy = toScreenY(wy);
      ctx.moveTo(0, sy);
      ctx.lineTo(W, sy);
    }
    ctx.stroke();
    
    // --- Axes ---
    // X axis
    const axisYScreen = toScreenY(0);
    if (axisYScreen >= 0 && axisYScreen <= H) {
      ctx.beginPath();
      ctx.strokeStyle = 'rgba(255, 255, 255, 0.4)';
      ctx.lineWidth = 1.5;
      ctx.moveTo(0, axisYScreen);
      ctx.lineTo(W, axisYScreen);
      ctx.stroke();
    }
    // Y axis
    const axisXScreen = toScreenX(0);
    if (axisXScreen >= 0 && axisXScreen <= W) {
      ctx.beginPath();
      ctx.strokeStyle = 'rgba(255, 255, 255, 0.4)';
      ctx.lineWidth = 1.5;
      ctx.moveTo(axisXScreen, 0);
      ctx.lineTo(axisXScreen, H);
      ctx.stroke();
    }

    // --- Grid Labels ---
    ctx.fillStyle = 'rgba(255, 255, 255, 0.6)';
    ctx.font = '11px "Inter", sans-serif';
    
    // Format label smartly
    const formatLabel = (val) => {
      if (gridStep >= 1) return Math.round(val).toString();
      const decimals = Math.max(0, -Math.floor(Math.log10(gridStep)));
      return val.toFixed(decimals);
    };
    
    // X labels (along X axis)
    const labelY = Math.min(Math.max(axisYScreen + 14, 14), H - 4);
    ctx.textAlign = 'center';
    ctx.textBaseline = 'top';
    for (let wx = startX; wx <= endX; wx += gridStep) {
      if (Math.abs(wx) < gridStep * 0.01) continue; // skip 0
      const sx = toScreenX(wx);
      if (sx > 20 && sx < W - 20) {
        ctx.fillText(formatLabel(wx), sx, labelY);
      }
    }
    
    // Y labels (along Y axis)
    const labelX = Math.min(Math.max(axisXScreen - 6, 30), W - 6);
    ctx.textAlign = 'right';
    ctx.textBaseline = 'middle';
    for (let wy = startY; wy <= endY; wy += gridStep) {
      if (Math.abs(wy) < gridStep * 0.01) continue; // skip 0
      const sy = toScreenY(wy);
      if (sy > 10 && sy < H - 10) {
        ctx.fillText(formatLabel(wy), labelX, sy);
      }
    }
    
    // Origin label
    if (axisXScreen >= 0 && axisXScreen <= W && axisYScreen >= 0 && axisYScreen <= H) {
      ctx.textAlign = 'right';
      ctx.textBaseline = 'top';
      ctx.fillText('0', axisXScreen - 6, axisYScreen + 6);
    }
    
    // --- Target Point ---
    const tx = toScreenX(Number(x));
    const ty = toScreenY(Number(y));
    ctx.beginPath();
    ctx.arc(tx, ty, 5, 0, Math.PI * 2);
    ctx.fillStyle = '#ef4444';
    ctx.fill();
    ctx.beginPath();
    ctx.arc(tx, ty, 10, 0, Math.PI * 2);
    ctx.strokeStyle = 'rgba(239, 68, 68, 0.4)';
    ctx.lineWidth = 2;
    ctx.stroke();
    ctx.fillStyle = 'rgba(239, 68, 68, 0.8)';
    ctx.font = '11px "Inter", sans-serif';
    ctx.textAlign = 'left';
    ctx.textBaseline = 'bottom';
    ctx.fillText(`Target (${Number(x).toFixed(1)}, ${Number(y).toFixed(1)})`, tx + 14, ty - 6);

    // --- Draw Manipulator ---
    const sol = solution;
    if (sol) {
      const th1 = sol.theta1;
      const th2 = sol.theta2;
      
      const j1sx = toScreenX(0);
      const j1sy = toScreenY(0);
      
      const j2wx = Number(l1) * Math.cos(th1);
      const j2wy = Number(l1) * Math.sin(th1);
      const j2sx = toScreenX(j2wx);
      const j2sy = toScreenY(j2wy);
      
      const th12 = th1 + th2;
      const ewx = j2wx + Number(l2) * Math.cos(th12);
      const ewy = j2wy + Number(l2) * Math.sin(th12);
      const esx = toScreenX(ewx);
      const esy = toScreenY(ewy);
      
      const robotYellow = '#EAB308';
      
      // Links
      ctx.beginPath();
      ctx.strokeStyle = robotYellow;
      ctx.lineWidth = 12;
      ctx.lineCap = 'round';
      ctx.moveTo(j1sx, j1sy);
      ctx.lineTo(j2sx, j2sy);
      ctx.lineTo(esx, esy);
      ctx.stroke();
      
      // Joints
      ctx.fillStyle = '#334155';
      ctx.strokeStyle = robotYellow;
      ctx.lineWidth = 3;
      
      ctx.beginPath(); ctx.arc(j1sx, j1sy, 12, 0, Math.PI * 2); ctx.fill(); ctx.stroke();
      ctx.beginPath(); ctx.arc(j2sx, j2sy, 10, 0, Math.PI * 2); ctx.fill(); ctx.stroke();
      
      // End Effector Gripper
      ctx.save();
      ctx.translate(esx, esy);
      ctx.rotate(-th12); // flip for canvas coords
      
      ctx.fillStyle = '#334155';
      ctx.beginPath();
      ctx.rect(0, -15, 12, 30);
      ctx.fill();
      
      ctx.fillStyle = robotYellow;
      ctx.beginPath();
      ctx.moveTo(12, -15); ctx.lineTo(24, -22); ctx.lineTo(34, -22);
      ctx.lineTo(34, -14); ctx.lineTo(24, -14); ctx.lineTo(12, -7);
      ctx.fill();
      
      ctx.beginPath();
      ctx.moveTo(12, 15); ctx.lineTo(24, 22); ctx.lineTo(34, 22);
      ctx.lineTo(34, 14); ctx.lineTo(24, 14); ctx.lineTo(12, 7);
      ctx.fill();
      
      ctx.fillStyle = '#1e293b';
      ctx.beginPath(); ctx.rect(26, -14, 8, 4); ctx.fill();
      ctx.beginPath(); ctx.rect(26, 10, 8, 4); ctx.fill();
      
      ctx.restore();
    }
  }, [solution, x, y, l1, l2]);

  // Redraw on any state change
  useEffect(() => { drawScene(); }, [drawScene]);
  useEffect(() => { drawScene(); }, [l1, l2, x, y]);

  // --- Mouse handlers for panning ---
  const handleMouseDown = (e) => {
    isPanning.current = true;
    panStart.current = { x: e.clientX, y: e.clientY };
    e.currentTarget.style.cursor = 'grabbing';
  };
  
  const handleMouseMove = (e) => {
    if (!isPanning.current) return;
    const dx = e.clientX - panStart.current.x;
    const dy = e.clientY - panStart.current.y;
    const cam = cameraRef.current;
    cam.offsetX -= dx / cam.zoom;
    cam.offsetY += dy / cam.zoom;
    panStart.current = { x: e.clientX, y: e.clientY };
    drawScene();
  };
  
  const handleMouseUp = (e) => {
    isPanning.current = false;
    e.currentTarget.style.cursor = 'grab';
  };
  
  // --- Wheel zoom ---
  const handleWheel = (e) => {
    e.preventDefault();
    const cam = cameraRef.current;
    const factor = e.deltaY < 0 ? 1.15 : 1 / 1.15;
    cam.zoom = Math.max(5, Math.min(500, cam.zoom * factor));
    drawScene();
  };

  // --- Controls ---
  const zoomIn = () => {
    cameraRef.current.zoom = Math.min(500, cameraRef.current.zoom * 1.4);
    drawScene();
  };
  const zoomOut = () => {
    cameraRef.current.zoom = Math.max(5, cameraRef.current.zoom / 1.4);
    drawScene();
  };
  const fitView = () => {
    const maxReach = Number(l1) + Number(l2);
    const canvas = canvasRef.current;
    if (!canvas) return;
    const padding = 1.5; // world units of padding around the reach
    const fitZoom = Math.min(canvas.width, canvas.height) / (2 * (maxReach + padding));
    cameraRef.current = { offsetX: 0, offsetY: 0, zoom: fitZoom };
    drawScene();
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem', paddingBottom: '4rem' }}>
      
      <div>
        <h1 style={{ margin: 0, fontSize: '2rem' }}>Interactive IK Tester</h1>
        <p style={{ color: 'var(--text-secondary)', margin: 0 }}>Input coordinates and let the ML Model predict Joint Angles (Theta 1 & Theta 2).</p>
      </div>

      <div style={{ display: 'flex', gap: '2rem', flexWrap: 'wrap' }}>
        
        {/* Input Form Panel */}
        <div className="glass-card" style={{ flex: '1', minWidth: '300px', display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
          <h3 style={{ margin: 0, fontSize: '1.2rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <Activity size={20} color="var(--accent-1)" />
            Configuration
          </h3>
          
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
              <label className="micro-label">End Effector X</label>
              <input type="number" step="0.1" value={x} onChange={e => setX(e.target.value)} className="input-field" style={inputStyle} />
            </div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
              <label className="micro-label">End Effector Y</label>
              <input type="number" step="0.1" value={y} onChange={e => setY(e.target.value)} className="input-field" style={inputStyle} />
            </div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
              <label className="micro-label">Link Length (L1)</label>
              <input type="number" step="0.1" value={l1} onChange={e => setL1(e.target.value)} className="input-field" style={inputStyle} />
            </div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
              <label className="micro-label">Link Length (L2)</label>
              <input type="number" step="0.1" value={l2} onChange={e => setL2(e.target.value)} className="input-field" style={inputStyle} />
            </div>
          </div>
          
          <button className="btn btn-primary" onClick={handleSolve} disabled={loading} style={{ width: '100%', marginTop: '1rem', justifyContent: 'center' }}>
            {loading ? 'Solving...' : 'Solve Inverse Kinematics'}
          </button>
          
          {error && <div style={{ color: '#ef4444', fontSize: '0.9rem', marginTop: '1rem', padding: '1rem', backgroundColor: 'rgba(239, 68, 68, 0.1)', borderRadius: '0.5rem' }}>{error}</div>}
          
          {solution && (
            <div style={{ marginTop: '1rem', borderTop: '1px solid var(--border-color)', paddingTop: '1.5rem' }}>
              
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
                <span className="micro-label" style={{ color: 'var(--accent-2)' }}>ML Model (XGBoost) Prediction</span>
              </div>
              
              <div style={{ display: 'flex', gap: '1rem', marginBottom: '1.5rem' }}>
                <div style={{ flex: 1, backgroundColor: 'var(--bg-secondary)', padding: '1rem', borderRadius: '0.5rem' }}>
                  <div className="micro-label">Theta 1 (rad)</div>
                  <div className="tabular-nums" style={{ fontSize: '1.5rem', fontWeight: 'bold', marginBottom: '0.5rem' }}>{solution.theta1.toFixed(4)}</div>
                  {solution.analytical_theta1 !== null && (
                     <div style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', borderTop: '1px dashed var(--border-color)', paddingTop: '0.5rem' }}>
                        <div>True (Analytical): <span className="tabular-nums">{solution.analytical_theta1.toFixed(4)}</span></div>
                        <div style={{ color: '#ef4444', marginTop: '0.25rem' }}>Error: {solution.error_theta1.toFixed(2)}%</div>
                     </div>
                  )}
                </div>
                <div style={{ flex: 1, backgroundColor: 'var(--bg-secondary)', padding: '1rem', borderRadius: '0.5rem' }}>
                  <div className="micro-label">Theta 2 (rad)</div>
                  <div className="tabular-nums" style={{ fontSize: '1.5rem', fontWeight: 'bold', marginBottom: '0.5rem' }}>{solution.theta2.toFixed(4)}</div>
                  {solution.analytical_theta2 !== null && (
                     <div style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', borderTop: '1px dashed var(--border-color)', paddingTop: '0.5rem' }}>
                        <div>True (Analytical): <span className="tabular-nums">{solution.analytical_theta2.toFixed(4)}</span></div>
                        <div style={{ color: '#ef4444', marginTop: '0.25rem' }}>Error: {solution.error_theta2.toFixed(2)}%</div>
                     </div>
                  )}
                </div>
              </div>
            </div>
          )}
        </div>
        
        {/* Visualizer Panel */}
        <div className="glass-card" style={{ flex: '2', minWidth: '400px', display: 'flex', flexDirection: 'column' }}>
          
          {/* Toolbar */}
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.75rem' }}>
            <span className="micro-label" style={{ color: 'var(--text-secondary)' }}>Manipulator Workspace</span>
            <div style={{ display: 'flex', gap: '0.5rem' }}>
              <button onClick={zoomIn} style={toolbarBtnStyle} title="Zoom In">
                <ZoomIn size={16} />
              </button>
              <button onClick={zoomOut} style={toolbarBtnStyle} title="Zoom Out">
                <ZoomOut size={16} />
              </button>
              <button onClick={fitView} style={toolbarBtnStyle} title="Fit View">
                <Maximize size={16} />
              </button>
            </div>
          </div>
          
          <canvas 
            ref={canvasRef} 
            width={700} 
            height={550} 
            onMouseDown={handleMouseDown}
            onMouseMove={handleMouseMove}
            onMouseUp={handleMouseUp}
            onMouseLeave={handleMouseUp}
            onWheel={handleWheel}
            style={{ 
              width: '100%',
              backgroundColor: '#0f0f0f', 
              borderRadius: '0.5rem',
              border: '1px solid var(--border-color)',
              cursor: 'grab'
            }}
          />
          <p className="micro-label" style={{ color: 'var(--text-secondary)', textAlign: 'center', marginTop: '0.5rem' }}>
            Scroll to zoom · Drag to pan · Use toolbar buttons for quick controls
          </p>
        </div>
        
      </div>
    </div>
  );
};

const inputStyle = {
  width: '100%',
  padding: '0.5rem',
  borderRadius: '0.25rem',
  border: '1px solid var(--border-color)',
  backgroundColor: 'var(--bg-primary)',
  color: 'var(--text-primary)',
  outline: 'none',
  fontSize: '1rem'
};

const toolbarBtnStyle = {
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'center',
  width: '32px',
  height: '32px',
  borderRadius: '0.375rem',
  border: '1px solid var(--border-color)',
  backgroundColor: 'var(--bg-secondary)',
  color: 'var(--text-primary)',
  cursor: 'pointer',
  transition: 'all 0.15s ease'
};

export default Test;
