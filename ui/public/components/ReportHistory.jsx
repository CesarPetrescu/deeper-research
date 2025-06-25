import React from 'react';

function ReportHistory({ 
  showPrevious, 
  previousReports, 
  previewReportContent, 
  downloadReport, 
  deleteReport 
}) {
  if (!showPrevious) return null;

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
        📚 Research History
      </h3>
      {previousReports.length === 0 ? (
        <p style={{ margin: 0, color: '#6b7280', fontSize: '1.1rem' }}>No previous reports found.</p>
      ) : (
        <div style={{ display: 'grid', gap: '1rem' }}>
          {previousReports.map((report) => (
            <div key={report.id} style={{ 
              background: '#f8fafc',
              border: '1px solid #e2e8f0',
              borderRadius: '12px',
              padding: '1.5rem',
              transition: 'all 0.3s ease'
            }}>
              <div style={{ marginBottom: '1rem' }}>
                <div style={{ fontWeight: '600', fontSize: '1.1rem', color: '#1f2937', marginBottom: '0.5rem' }}>
                  {report.question}
                </div>
                <div style={{ fontSize: '0.9rem', color: '#6b7280' }}>
                  {new Date(report.created_at).toLocaleString()}
                  <span style={{ 
                    marginLeft: '1rem',
                    padding: '0.25rem 0.75rem',
                    borderRadius: '20px',
                    fontSize: '0.8rem',
                    fontWeight: '500',
                    background: report.has_content ? '#dcfce7' : report.has_error ? '#fee2e2' : '#fef3c7',
                    color: report.has_content ? '#166534' : report.has_error ? '#991b1b' : '#92400e'
                  }}>
                    {report.has_content ? '✅ Complete' : report.has_error ? '❌ Error' : '⏳ Processing'}
                  </span>
                </div>
              </div>
              
              <div style={{ display: 'flex', gap: '0.75rem', flexWrap: 'wrap' }}>
                {report.has_content && (
                  <>
                    <button 
                      style={{ 
                        padding: '0.5rem 1rem', 
                        backgroundColor: '#6366f1', 
                        color: 'white', 
                        border: 'none', 
                        borderRadius: '8px', 
                        cursor: 'pointer',
                        fontSize: '0.9rem',
                        fontWeight: '500',
                        transition: 'all 0.3s ease'
                      }}
                      onClick={() => previewReportContent(report.id)}
                    >
                      👁️ Preview
                    </button>
                    {['markdown', 'pdf', 'docx'].map(format => (
                      <button 
                        key={format}
                        style={{ 
                          padding: '0.5rem 1rem', 
                          backgroundColor: format === 'markdown' ? '#10b981' : format === 'pdf' ? '#ef4444' : '#3b82f6',
                          color: 'white', 
                          border: 'none', 
                          borderRadius: '8px', 
                          cursor: 'pointer',
                          fontSize: '0.9rem',
                          fontWeight: '500',
                          transition: 'all 0.3s ease'
                        }}
                        onClick={() => downloadReport(format, report.id)}
                      >
                        {format.toUpperCase()}
                      </button>
                    ))}
                  </>
                )}
                <button 
                  style={{ 
                    padding: '0.5rem 1rem', 
                    backgroundColor: '#ef4444', 
                    color: 'white', 
                    border: 'none', 
                    borderRadius: '8px', 
                    cursor: 'pointer',
                    fontSize: '0.9rem',
                    fontWeight: '500',
                    transition: 'all 0.3s ease'
                  }}
                  onClick={() => deleteReport(report.id)}
                >
                  🗑️ Delete
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default ReportHistory;
