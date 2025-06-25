import React from 'react';

function ResearchOutput({ lines, isLoading, currentStep, progress, researchId, downloadReport }) {
  if (lines.length === 0 && !isLoading) return null;

  return (
    <div style={{
      background: '#ffffff',
      borderRadius: '16px',
      padding: '2rem',
      marginBottom: '2rem',
      boxShadow: '0 10px 30px -5px rgba(0, 0, 0, 0.07)',
    }}>
      <h3 style={{ 
        margin: '0 0 1.5rem 0', 
        fontSize: '1.5rem', 
        fontWeight: '700',
        color: '#1f2937'
      }}>
        🔬 Live Research Progress
      </h3>
      <div style={{ 
        background: '#1e293b',
        color: '#e2e8f0',
        borderRadius: '12px',
        padding: '1.5rem',
        fontFamily: '"Fira Code", monospace',
        fontSize: '0.9rem',
        lineHeight: '1.6',
        maxHeight: '600px',
        overflowY: 'auto',
      }}>
        {lines.map((line, index) => {
          let color = '#e2e8f0';
          
          if (line.includes('🔍') || line.includes('🤖')) {
            color = '#60a5fa';
          } else if (line.includes('✅') || line.includes('🎉')) {
            color = '#34d399';
          } else if (line.includes('⚠️') || line.includes('❌')) {
            color = '#f87171';
          } else if (line.includes('📋') || line.includes('📊')) {
            color = '#a78bfa';
          } else if (line.includes('🌐') || line.includes('📄')) {
            color = '#fbbf24';
          } else if (line.includes('📝') || line.includes('✍️')) {
            color = '#fb7185';
          }
          
          return (
            <div 
              key={index} 
              style={{ 
                marginBottom: '0.5rem',
                color: color,
              }}
            >
              {line}
            </div>
          );
        })}
        {isLoading && (
          <div style={{ 
            color: '#60a5fa',
            animation: 'pulse 2s infinite',
            marginTop: '1rem',
          }}>
            🔄 {currentStep}
          </div>
        )}
      </div>
      
      {researchId && !isLoading && (
        <div style={{marginTop: '1.5rem'}}>
          <h3 style={{ 
            margin: '0 0 1.5rem 0', 
            fontSize: '1.5rem', 
            fontWeight: '700',
            color: '#1f2937'
          }}>
            📊 Research Complete - Download Results
          </h3>
          <div style={{ display: 'flex', gap: '1rem', flexWrap: 'wrap' }}>
            {['markdown', 'pdf', 'docx'].map(format => (
              <button 
                key={format}
                style={{ 
                  padding: '0.75rem 1.5rem', 
                  background: format === 'markdown' ? '#10b981' : format === 'pdf' ? '#ef4444' : '#3b82f6',
                  color: 'white', 
                  border: 'none', 
                  borderRadius: '12px', 
                  cursor: 'pointer',
                  fontSize: '1rem',
                  fontWeight: '600',
                  transition: 'all 0.3s ease',
                  boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)'
                }}
                onClick={() => downloadReport(format)}
              >
                📄 {format.toUpperCase()}
              </button>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

export default ResearchOutput;
