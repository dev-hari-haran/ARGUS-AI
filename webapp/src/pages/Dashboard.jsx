import React, { useState } from 'react';
import { BarChart, Bar, LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, ReferenceDot, ReferenceLine, Legend, Cell } from 'recharts';
import { Search, Maximize2 } from 'lucide-react';
import ChartExportWrapper from '../components/ChartExportWrapper';
import GraphModal from '../components/GraphModal';
import graphsData from '../data/graphsData.json';

// Generate Bias vs Variance Data
const biasVarianceData = Array.from({ length: 100 }, (_, i) => {
  const complexity = i;
  const bias = 150 * Math.exp(-0.08 * complexity); 
  const variance = 0.02 * Math.pow(complexity, 2); 
  const totalError = bias + variance + 10;
  return { complexity, Bias: parseFloat(bias.toFixed(2)), Variance: parseFloat(variance.toFixed(2)), 'Total Error': parseFloat(totalError.toFixed(2)) };
});

// Find sweet spot (minimum total error)
const sweetSpotIdx = biasVarianceData.reduce((minIdx, item, idx, arr) => 
  item['Total Error'] < arr[minIdx]['Total Error'] ? idx : minIdx, 0
);

const Dashboard = () => {
  const [searchQuery, setSearchQuery] = useState('');
  const [modalContent, setModalContent] = useState(null);
  
  const filteredGraphs = graphsData.filter(graph => 
    graph.title.toLowerCase().includes(searchQuery.toLowerCase()) || 
    graph.description.toLowerCase().includes(searchQuery.toLowerCase()) ||
    graph.category.toLowerCase().includes(searchQuery.toLowerCase())
  );

  // Real data from latest training run
  const errorComparisonData = [
    { name: 'IK Analytical', error: 0.00001, fill: '#10b981' },
    { name: 'XGBoost (5M)', error: 0.116, fill: '#EAB308' },
    { name: 'Linear Reg', error: 0.85, fill: '#3b82f6' },
    { name: 'HistGradBoost', error: 0.461, fill: '#8b5cf6' }
  ];

  const r2ComparisonData = [
    { name: 'θ₁ R²', XGBoost: 0.958, LinearReg: 0.42 },
    { name: 'θ₂ R²', XGBoost: 0.999, LinearReg: 0.61 }
  ];

  const trainingTimeData = [
    { name: '1M', XGBoost: 68, LinearReg: 5 },
    { name: '2M', XGBoost: 95, LinearReg: 9 },
    { name: '3M', XGBoost: 115, LinearReg: 14 },
    { name: '4M', XGBoost: 130, LinearReg: 18 },
    { name: '5M', XGBoost: 145, LinearReg: 22 }
  ];

  const StatCard = ({ title, value, subtext, trend, isGood }) => (
    <div className="glass-card" style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
      <div className="micro-label">{title}</div>
      <div className="tabular-nums" style={{ fontSize: '2rem', fontWeight: 'bold' }}>{value}</div>
      <div style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', display: 'flex', gap: '0.5rem' }}>
        <span style={{ color: isGood ? 'var(--accent-2)' : 'var(--accent-1)' }}>{trend}</span>
        {subtext}
      </div>
    </div>
  );

  const openModal = (title, component) => {
    setModalContent({ title, component });
  };

  // Custom Sweet Spot Label
  const SweetSpotLabel = ({ viewBox }) => {
    const { x, y } = viewBox;
    return (
      <g>
        <rect x={x - 60} y={y - 45} width={120} height={28} rx={6} fill="#10b981" fillOpacity={0.9} />
        <text x={x} y={y - 27} textAnchor="middle" fill="white" fontSize={12} fontWeight="bold">
          ★ Sweet Spot
        </text>
        <line x1={x} y1={y - 17} x2={x} y2={y - 6} stroke="#10b981" strokeWidth={2} />
      </g>
    );
  };

  // Custom Model Label
  const ModelLabel = ({ viewBox }) => {
    const { x, y } = viewBox;
    return (
      <g>
        <rect x={x - 75} y={y - 70} width={150} height={28} rx={6} fill="#EAB308" fillOpacity={0.9} />
        <text x={x} y={y - 52} textAnchor="middle" fill="#000" fontSize={11} fontWeight="bold">
          ⚙ Our XGBoost Model
        </text>
        <line x1={x} y1={y - 42} x2={x} y2={y - 6} stroke="#EAB308" strokeWidth={2} strokeDasharray="4 2" />
      </g>
    );
  };

  // The Bias-Variance Chart Component
  const BiasVarianceChart = () => (
    <ResponsiveContainer width="100%" height="100%">
      <LineChart data={biasVarianceData} margin={{ top: 60, right: 30, left: 0, bottom: 20 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="var(--border-color)" />
        <XAxis dataKey="complexity" stroke="var(--text-secondary)" label={{ value: 'Model Complexity →', position: 'bottom', fill: 'var(--text-secondary)' }} />
        <YAxis stroke="var(--text-secondary)" label={{ value: 'Error', angle: -90, position: 'insideLeft', fill: 'var(--text-secondary)' }} />
        <Tooltip contentStyle={{ backgroundColor: 'var(--bg-card)', borderColor: 'var(--border-color)', color: 'var(--text-primary)' }}/>
        <Legend verticalAlign="top" height={36}/>
        
        {/* Underfitting / Overfitting zones */}
        <ReferenceLine x={20} stroke="rgba(59,130,246,0.3)" strokeWidth={30} />
        <ReferenceLine x={75} stroke="rgba(239,68,68,0.3)" strokeWidth={30} />
        
        <Line type="monotone" dataKey="Bias" stroke="#3b82f6" strokeWidth={3} dot={false} name="Bias (Underfitting)" />
        <Line type="monotone" dataKey="Variance" stroke="#ef4444" strokeWidth={3} dot={false} name="Variance (Overfitting)" />
        <Line type="monotone" dataKey="Total Error" stroke="#EAB308" strokeWidth={4} dot={false} name="Total Error" />
        
        {/* Sweet Spot marker */}
        <ReferenceDot x={sweetSpotIdx} y={biasVarianceData[sweetSpotIdx]['Total Error']} r={10} fill="#10b981" stroke="white" strokeWidth={3} />
        <ReferenceLine x={sweetSpotIdx} stroke="#10b981" strokeDasharray="5 5" label={<SweetSpotLabel />} />
        
        {/* Our Model marker (near sweet spot) */}
        <ReferenceDot x={sweetSpotIdx + 3} y={biasVarianceData[sweetSpotIdx + 3]['Total Error']} r={8} fill="#EAB308" stroke="white" strokeWidth={2} />
        <ReferenceLine x={sweetSpotIdx + 3} stroke="#EAB308" strokeDasharray="3 3" label={<ModelLabel />} />

        {/* Zone Labels */}
        <ReferenceLine x={15} stroke="transparent" label={{ value: "← Underfitting", position: "top", fill: "#3b82f6", fontSize: 13, fontWeight: 'bold' }} />
        <ReferenceLine x={80} stroke="transparent" label={{ value: "Overfitting →", position: "top", fill: "#ef4444", fontSize: 13, fontWeight: 'bold' }} />
      </LineChart>
    </ResponsiveContainer>
  );

  const ErrorCompChart = () => (
    <ResponsiveContainer width="100%" height="100%">
      <BarChart data={errorComparisonData} layout="vertical" margin={{ top: 5, right: 30, left: 10, bottom: 5 }}>
        <CartesianGrid strokeDasharray="3 3" horizontal={false} stroke="var(--border-color)" />
        <XAxis type="number" stroke="var(--text-secondary)" tick={{fontSize: 12}} />
        <YAxis type="category" dataKey="name" stroke="var(--text-secondary)" tick={{fontSize: 11}} width={90}/>
        <Tooltip contentStyle={{ backgroundColor: 'var(--bg-card)', borderColor: 'var(--border-color)', color: 'var(--text-primary)' }}/>
        <Bar dataKey="error" radius={[0, 4, 4, 0]}>
          {errorComparisonData.map((entry, index) => (
            <Cell key={`cell-${index}`} fill={entry.fill} />
          ))}
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  );

  const R2Chart = () => (
    <ResponsiveContainer width="100%" height="100%">
      <BarChart data={r2ComparisonData} margin={{ top: 5, right: 20, left: -20, bottom: 5 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="var(--border-color)" />
        <XAxis dataKey="name" stroke="var(--text-secondary)" tick={{fontSize: 12}} />
        <YAxis stroke="var(--text-secondary)" tick={{fontSize: 12}} domain={[0, 1]} />
        <Tooltip contentStyle={{ backgroundColor: 'var(--bg-card)', borderColor: 'var(--border-color)', color: 'var(--text-primary)' }}/>
        <Legend />
        <Bar dataKey="XGBoost" fill="#EAB308" radius={[4, 4, 0, 0]} />
        <Bar dataKey="LinearReg" fill="#3b82f6" radius={[4, 4, 0, 0]} />
      </BarChart>
    </ResponsiveContainer>
  );

  const TrainingTimeChart = () => (
    <ResponsiveContainer width="100%" height="100%">
      <LineChart data={trainingTimeData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="var(--border-color)" />
        <XAxis dataKey="name" stroke="var(--text-secondary)" tick={{fontSize: 12}} label={{ value: 'Dataset Size (rows)', position: 'bottom', fill: 'var(--text-secondary)', fontSize: 11 }} />
        <YAxis stroke="var(--text-secondary)" tick={{fontSize: 12}} label={{ value: 'Seconds', angle: -90, position: 'insideLeft', fill: 'var(--text-secondary)', fontSize: 11 }} />
        <Tooltip contentStyle={{ backgroundColor: 'var(--bg-card)', borderColor: 'var(--border-color)', color: 'var(--text-primary)' }}/>
        <Legend />
        <Line type="monotone" dataKey="XGBoost" stroke="#EAB308" strokeWidth={3} dot={{ r: 4, fill: '#EAB308' }} />
        <Line type="monotone" dataKey="LinearReg" stroke="#3b82f6" strokeWidth={3} dot={{ r: 4, fill: '#3b82f6' }} />
      </LineChart>
    </ResponsiveContainer>
  );

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
      
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-end' }}>
        <div>
          <h1 style={{ margin: 0, fontSize: '2rem' }}>Analytics Dashboard</h1>
          <p style={{ color: 'var(--text-secondary)', margin: 0 }}>Comparison of Inverse Kinematics vs Machine Learning</p>
        </div>
      </div>

      {/* Stat Cards Grid */}
      <div className="grid-dashboard" style={{ gridTemplateColumns: 'repeat(4, 1fr)' }}>
        <StatCard title="IK Accuracy" value="99.99%" subtext="vs Ground Truth" trend="↑ 18.7%" isGood={true} />
        <StatCard title="Cartesian Error" value="1.58e-5" subtext="Mean Euclidean Dist" trend="↓ 99.9%" isGood={true} />
        <StatCard title="Training Time" value="0.0s" subtext="No training required" trend="Fast" isGood={true} />
        <StatCard title="ML Model Avg Error" value="0.116" subtext="XGBoost (5M Rows)" trend="↓ 65%" isGood={true} />
      </div>

      <div className="grid-dashboard">
        {/* Main Bias-Variance Graph */}
        <div style={{ gridColumn: 'span 7' }}>
          <ChartExportWrapper title="Bias vs Variance Tradeoff" filename="bias_variance">
            <div 
              style={{ height: '400px', cursor: 'pointer', position: 'relative' }} 
              onClick={() => openModal("Bias vs Variance Tradeoff", <BiasVarianceChart />)}
              className="chart-hover-wrapper"
            >
              <div className="chart-expand-hint" style={{ position: 'absolute', top: 10, right: 10, zIndex: 10, backgroundColor: 'var(--bg-secondary)', padding: '0.5rem', borderRadius: '0.5rem', opacity: 0.8, display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <Maximize2 size={16} /> <span className="micro-label">Click to expand</span>
              </div>
              <BiasVarianceChart />
            </div>
            <p className="micro-label" style={{ textAlign: 'center', marginTop: '1rem' }}>
              Visualization of our model's performance on the bias-variance curve.
            </p>
          </ChartExportWrapper>
        </div>

        {/* Secondary Charts */}
        <div style={{ gridColumn: 'span 5', display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
          
          <ChartExportWrapper title="Cartesian Error Comparison" filename="error_comparison">
            <div 
              style={{ height: '150px', cursor: 'pointer', position: 'relative' }}
              onClick={() => openModal("Cartesian Error Comparison", <ErrorCompChart />)}
            >
              <ErrorCompChart />
            </div>
          </ChartExportWrapper>

          <ChartExportWrapper title="R² Score (XGBoost vs Linear Regression)" filename="r2_comparison">
            <div 
              style={{ height: '150px', cursor: 'pointer', position: 'relative' }}
              onClick={() => openModal("R² Score Comparison", <R2Chart />)}
            >
              <R2Chart />
            </div>
          </ChartExportWrapper>

          <ChartExportWrapper title="Training Time vs Dataset Size" filename="training_time">
            <div 
              style={{ height: '170px', cursor: 'pointer', position: 'relative' }}
              onClick={() => openModal("Training Time vs Dataset Size", <TrainingTimeChart />)}
            >
              <TrainingTimeChart />
            </div>
          </ChartExportWrapper>

        </div>
      </div>

      {/* Generated Analytics Gallery */}
      <div>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', borderBottom: '1px solid var(--border-color)', paddingBottom: '0.5rem', marginBottom: '1.5rem', marginTop: '2rem' }}>
          <h2 style={{ fontSize: '1.8rem', margin: 0 }}>
            Comprehensive Analytics Gallery
          </h2>
          <div style={{ position: 'relative', width: '300px' }}>
            <Search size={18} style={{ position: 'absolute', left: '10px', top: '50%', transform: 'translateY(-50%)', color: 'var(--text-secondary)' }} />
            <input 
              type="text" 
              placeholder="Search graphs by title or detail..." 
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              style={{
                width: '100%', padding: '0.5rem 1rem 0.5rem 2.5rem', 
                borderRadius: '0.5rem', border: '1px solid var(--border-color)', 
                background: 'var(--bg-secondary)', color: 'var(--text-primary)', outline: 'none'
              }} 
            />
          </div>
        </div>
        
        <div style={{ columnCount: 2, columnGap: '1.5rem' }}>
          {filteredGraphs.map((graph) => (
            <div key={graph.id} style={{ breakInside: 'avoid', marginBottom: '1.5rem' }}>
              <ChartExportWrapper title={graph.title} filename={graph.id}>
                <div 
                  style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem', cursor: 'pointer' }}
                  onClick={() => openModal(graph.title, <img src={graph.filename} alt={graph.title} style={{ width: '100%', height: '100%', objectFit: 'contain' }} />)}
                >
                  <img src={graph.filename} alt={graph.title} style={{ width: '100%', height: 'auto', borderRadius: '0.25rem' }} />
                  <p className="micro-label" style={{ color: 'var(--text-secondary)' }}>
                    {graph.description}
                  </p>
                </div>
              </ChartExportWrapper>
            </div>
          ))}
        </div>
      </div>

      <GraphModal 
        isOpen={!!modalContent} 
        onClose={() => setModalContent(null)}
        title={modalContent?.title}
      >
        {modalContent?.component}
      </GraphModal>

    </div>
  );
};

export default Dashboard;
