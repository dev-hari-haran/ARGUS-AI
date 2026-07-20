import React, { useRef } from 'react';
import { Download, Image as ImageIcon, FileText } from 'lucide-react';
import html2canvas from 'html2canvas';
import { jsPDF } from 'jspdf';

const ChartExportWrapper = ({ children, title, filename = "chart" }) => {
  const chartRef = useRef(null);

  const exportAsPNG = async () => {
    if (!chartRef.current) return;
    const canvas = await html2canvas(chartRef.current, { backgroundColor: null });
    const image = canvas.toDataURL("image/png");
    const link = document.createElement("a");
    link.href = image;
    link.download = `${filename}.png`;
    link.click();
  };

  const exportAsPDF = async () => {
    if (!chartRef.current) return;
    const canvas = await html2canvas(chartRef.current, { backgroundColor: null });
    const imgData = canvas.toDataURL("image/png");
    
    // Create PDF (A4 landscape)
    const pdf = new jsPDF({
      orientation: 'landscape',
      unit: 'px',
      format: [canvas.width, canvas.height]
    });
    
    pdf.addImage(imgData, 'PNG', 0, 0, canvas.width, canvas.height);
    pdf.save(`${filename}.pdf`);
  };

  return (
    <div className="glass-card" style={{ position: 'relative', display: 'flex', flexDirection: 'column' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
        <h3 style={{ margin: 0, fontSize: '1.1rem' }}>{title}</h3>
        <div style={{ display: 'flex', gap: '0.5rem' }}>
          <button onClick={exportAsPNG} className="btn-icon" title="Export as PNG">
            <ImageIcon size={16} />
          </button>
          <button onClick={exportAsPDF} className="btn-icon" title="Export as PDF">
            <FileText size={16} />
          </button>
        </div>
      </div>
      
      <div ref={chartRef} style={{ flex: 1, position: 'relative' }}>
        {children}
      </div>
    </div>
  );
};

export default ChartExportWrapper;
