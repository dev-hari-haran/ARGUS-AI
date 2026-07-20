import React from 'react';
import RadialGauge from '../components/RadialGauge';
import { Download, Link, SquareTerminal } from 'lucide-react';

const Home = () => {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>
      {/* HUD Header / Hero - Side by Side */}
      <div className="glass-card" style={{ padding: '3rem 2rem', position: 'relative', overflow: 'hidden' }}>
        <div style={{
          position: 'absolute', top: '-50%', left: '50%', transform: 'translateX(-50%)',
          width: '600px', height: '600px', background: 'var(--accent-1)',
          opacity: 0.1, filter: 'blur(100px)', borderRadius: '50%', zIndex: 0
        }} />
        
        <div style={{ position: 'relative', zIndex: 1, display: 'flex', alignItems: 'center', gap: '2rem' }}>
          <div style={{ flex: 1 }}>
            <h1 style={{ fontSize: '3.5rem', marginBottom: '0.2rem', textTransform: 'uppercase' }}>
              ARGUS - <span style={{ color: 'var(--accent-2)' }}>AI</span>
            </h1>
            <h2 style={{ fontSize: '1.1rem', fontWeight: 500, letterSpacing: '0.05em', color: 'var(--accent-1)', marginBottom: '1.5rem', textTransform: 'uppercase' }}>
              Adaptive Robotic Geometry and Understanding System
            </h2>
            <p style={{ fontSize: '1.2rem', color: 'var(--text-secondary)' }}>
              <strong>Learning Inverse Kinematics instead of solving it.</strong><br/><br/>
              A production-grade Machine Learning framework utilizing five tree-based regressors to predict joint angles (θ₁, θ₂) directly from target coordinates (X, Y) and physical dimensions (L1, L2).
            </p>
          </div>
          <div style={{ flex: 1, display: 'flex', justifyContent: 'center' }}>
            <img src="/banner.svg" alt="ARGUS AI Banner" style={{ maxWidth: '100%', height: 'auto' }} />
          </div>
        </div>
      </div>

      {/* Specifications Row */}
      <div className="grid-dashboard">
        <div className="glass-card" style={{ gridColumn: 'span 3' }}>
          <h4 className="micro-label" style={{ color: 'var(--accent-1)' }}>Model Used</h4>
          <ul style={{ color: 'var(--text-secondary)', paddingLeft: '1.2rem', marginTop: '0.5rem', lineHeight: 1.6, fontSize: '0.9rem' }}>
            <li>XGBoost</li>
            <li>HistGradientBoosting</li>
            <li>Random Forest</li>
            <li>Extra Trees</li>
            <li>Decision Tree</li>
          </ul>
        </div>
        <div className="glass-card" style={{ gridColumn: 'span 3' }}>
          <h4 className="micro-label" style={{ color: 'var(--accent-2)' }}>Optimizer Used</h4>
          <ul style={{ color: 'var(--text-secondary)', paddingLeft: '1.2rem', marginTop: '0.5rem', lineHeight: 1.6, fontSize: '0.9rem' }}>
            <li>Levenberg-Marquardt (LM)</li>
            <li>Damped Least Squares (DLS)</li>
            <li>Optuna (Hyperparameters)</li>
          </ul>
        </div>
        <div className="glass-card" style={{ gridColumn: 'span 3' }}>
          <h4 className="micro-label" style={{ color: 'var(--accent-1)' }}>Evaluation Used</h4>
          <ul style={{ color: 'var(--text-secondary)', paddingLeft: '1.2rem', marginTop: '0.5rem', lineHeight: 1.6, fontSize: '0.9rem' }}>
            <li>Cartesian Mean Error</li>
            <li>Joint Space R² Score</li>
            <li>Bias-Variance Tradeoff</li>
            <li>SHAP Explainer</li>
          </ul>
        </div>
        <div className="glass-card" style={{ gridColumn: 'span 3' }}>
          <h4 className="micro-label" style={{ color: 'var(--accent-2)' }}>Splitting Used</h4>
          <ul style={{ color: 'var(--text-secondary)', paddingLeft: '1.2rem', marginTop: '0.5rem', lineHeight: 1.6, fontSize: '0.9rem' }}>
            <li>Train: 70%</li>
            <li>Validation: 15%</li>
            <li>Test: 15%</li>
            <li>Random State: 42</li>
          </ul>
        </div>
      </div>

      <div className="grid-dashboard">
        {/* Left Column: Info & Code */}
        <div className="glass-card" style={{ gridColumn: 'span 7', display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
          <div>
            <h3 style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.5rem' }}>
              <SquareTerminal size={20} color="var(--accent-1)" /> 
              Architecture Summary
            </h3>
            <p style={{ color: 'var(--text-secondary)', lineHeight: 1.6, marginBottom: '1rem' }}>
              The ARGUS-AI framework is decoupled into independent, highly modular vertical slices. No monolithic scripts; every module is configurable via YAML and interacts strictly through standardized data APIs. We evaluate five distinct tree-based architectures (Decision Tree, Random Forest, Extra Trees, HistGradientBoosting, XGBoost).
            </p>
            <img src="/architecture.svg" alt="Architecture" style={{ width: '100%', borderRadius: '0.5rem' }} />
          </div>
          
          <div>
            <h3 style={{ marginBottom: '0.5rem' }}>Universal Inference</h3>
            <div style={{ 
              background: 'var(--bg-secondary)', padding: '1rem', 
              borderRadius: '0.5rem', border: '1px solid var(--border-color)',
              fontFamily: 'monospace', color: 'var(--text-secondary)', fontSize: '0.9rem'
            }}>
              <span style={{ color: 'var(--text-secondary)' }}># Supply physical geometry and target coordinates to instantly predict joints:</span><br/>
              <span style={{ color: 'var(--accent-1)' }}>python</span> src\inference\predict.py --x 1.2 --y 0.8 --l1 1.0 --l2 1.0 --model xgboost
            </div>
          </div>
        </div>

        {/* Right Column: Gauges (Side by Side) */}
        <div className="glass-card" style={{ gridColumn: 'span 5', display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          <h3 style={{ textAlign: 'center', marginBottom: '1rem' }}>Model Accuracy</h3>
          
          {/* Side by side layout for Gauges */}
          <div style={{ display: 'flex', justifyContent: 'space-around', alignItems: 'center', flex: 1 }}>
            <div style={{ flex: 1 }}>
              <RadialGauge 
                value={99.9} 
                label="OPTIMIZED (IK LM)" 
                color="var(--accent-2)" 
              />
            </div>
            
            <div style={{ width: '1px', backgroundColor: 'var(--border-color)', height: '70%' }}></div>
            
            <div style={{ flex: 1 }}>
              <RadialGauge 
                value={81.2} 
                label="NON-OPTIMIZED (XGBOOST)" 
                color="var(--accent-1)" 
              />
            </div>
          </div>
          
          <div style={{ marginTop: 'auto' }}>
            <img src="/pipeline.svg" alt="Pipeline" style={{ width: '100%', borderRadius: '0.5rem', opacity: 0.8 }} />
          </div>
        </div>
      </div>

      {/* CTA Row */}
      <div className="glass-card" style={{ display: 'flex', gap: '1rem', flexWrap: 'wrap', justifyContent: 'center' }}>
        <a href="/raw_dataset.csv" download className="btn btn-primary" style={{ textDecoration: 'none' }}>
          <Download size={18} /> Download Dataset
        </a>
        <a href="/ik_lm_model.pkl" download className="btn btn-primary" style={{ textDecoration: 'none' }}>
          <Download size={18} /> Optimized Model (.pkl)
        </a>
        <a href="/xgboost_model.pkl" download className="btn btn-secondary" style={{ textDecoration: 'none' }}>
          <Download size={18} /> Non-Optimized (.pkl)
        </a>
        <div style={{ flex: 1 }}></div>
        <a href="https://github.com/dev-hari-haran/ARGUS-AI" target="_blank" rel="noreferrer" className="btn btn-secondary" style={{ textDecoration: 'none' }}>
          <Link size={18} /> GitHub
        </a>
        <a href="https://www.linkedin.com/in/hariharan-r-905a8a2a4/" target="_blank" rel="noreferrer" className="btn btn-secondary" style={{ textDecoration: 'none' }}>
          <Link size={18} /> LinkedIn
        </a>
      </div>
    </div>
  );
};

export default Home;
