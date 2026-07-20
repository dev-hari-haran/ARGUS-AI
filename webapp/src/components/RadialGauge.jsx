import React from 'react';
import { RadialBarChart, RadialBar, PolarAngleAxis, ResponsiveContainer } from 'recharts';

const RadialGauge = ({ value, label, color }) => {
  const data = [
    { name: 'Accuracy', value: value, fill: color }
  ];

  return (
    <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', width: '100%', height: '220px' }}>
      <ResponsiveContainer width="100%" height="80%">
        <RadialBarChart 
          cx="50%" 
          cy="50%" 
          innerRadius="70%" 
          outerRadius="90%" 
          barSize={15} 
          data={data} 
          startAngle={90} 
          endAngle={-270}
        >
          <PolarAngleAxis 
            type="number" 
            domain={[0, 100]} 
            angleAxisId={0} 
            tick={false} 
          />
          <RadialBar 
            minAngle={15} 
            background={{ fill: 'var(--bg-secondary)' }}
            clockWise 
            dataKey="value" 
            cornerRadius={10}
          />
          {/* We use SVG text to render the value directly in the center */}
          <text 
            x="50%" 
            y="50%" 
            textAnchor="middle" 
            dominantBaseline="middle" 
            className="tabular-nums" 
            style={{ fontSize: '2rem', fill: 'var(--text-primary)', fontWeight: 'bold' }}
          >
            {value}%
          </text>
        </RadialBarChart>
      </ResponsiveContainer>
      
      <div className="micro-label" style={{ marginTop: '0.5rem', textAlign: 'center' }}>
        {label}
      </div>
    </div>
  );
};

export default RadialGauge;
