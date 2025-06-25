import React from 'react';

function PreviewModal({ showPreview, setShowPreview, previewReport, renderMarkdown }) {
  if (!showPreview || !previewReport) return null;

  return (
    <div style={{
      position: 'fixed',
      top: 0,
      left: 0,
      right: 0,
      bottom: 0,
      background: 'rgba(0, 0, 0, 0.5)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      zIndex: 1000,
      padding: '2rem'
    }} onClick={() => setShowPreview(false)}>
      <div style={{
        background: 'white',
        borderRadius: '16px',
        maxWidth: '900px',
        maxHeight: '80vh',
        overflow: 'auto',
        padding: '2rem',
        boxShadow: '0 25px 50px -12px rgba(0, 0, 0, 0.25)'
      }} onClick={e => e.stopPropagation()}>
        <div style={{ 
          display: 'flex', 
          justifyContent: 'space-between', 
          alignItems: 'center', 
          marginBottom: '2rem',
          borderBottom: '1px solid #e2e8f0',
          paddingBottom: '1rem'
        }}>
          <h2 style={{ 
            margin: 0, 
            fontSize: '1.8rem', 
            fontWeight: '700',
            color: '#1f2937'
          }}>
            📖 Report Preview
          </h2>
          <button 
            style={{
              background: '#ef4444',
              color: 'white',
              border: 'none',
              borderRadius: '50%',
              width: '40px',
              height: '40px',
              cursor: 'pointer',
              fontSize: '1.2rem',
              fontWeight: 'bold',
              transition: 'all 0.3s ease'
            }}
            onClick={() => setShowPreview(false)}
          >
            ×
          </button>
        </div>
        <div style={{ 
          lineHeight: '1.7',
          color: '#374151'
        }}>
          {renderMarkdown(previewReport.content)}
        </div>
      </div>
    </div>
  );
}

export default PreviewModal;
