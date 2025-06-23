import React, { useState } from 'react';
import { createRoot } from 'react-dom/client';

function App() {
  const [question, setQuestion] = useState('');
  const [lines, setLines] = useState([]);
  const [researchId, setResearchId] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [previousReports, setPreviousReports] = useState([]);
  const [showPrevious, setShowPrevious] = useState(false);
  const [previewReport, setPreviewReport] = useState(null);
  const [showPreview, setShowPreview] = useState(false);
  
  // Load previous reports on component mount
  React.useEffect(() => {
    fetchPreviousReports();
  }, []);
  
  const fetchPreviousReports = async () => {
    try {
      const response = await fetch('/api/reports?limit=20');
      const data = await response.json();
      setPreviousReports(data.reports || []);
    } catch (error) {
      console.error('Failed to fetch previous reports:', error);
    }
  };

  const previewReportContent = async (reportId) => {
    try {
      const response = await fetch(`/api/reports/${reportId}`);
      const report = await response.json();
      setPreviewReport(report);
      setShowPreview(true);
    } catch (error) {
      console.error('Failed to fetch report:', error);
      alert('Failed to load report preview');
    }
  };

  const deleteReport = async (reportId) => {
    if (!confirm('Are you sure you want to delete this report? This action cannot be undone.')) {
      return;
    }
    
    try {
      const response = await fetch(`/api/reports/${reportId}`, {
        method: 'DELETE'
      });
      
      if (response.ok) {
        // Refresh the reports list
        fetchPreviousReports();
        alert('Report deleted successfully');
      } else {
        alert('Failed to delete report');
      }
    } catch (error) {
      console.error('Failed to delete report:', error);
      alert('Failed to delete report');
    }
  };
  
  const handleSubmit = () => {
    setLines([]);
    setResearchId(null);
    setIsLoading(true);
    
    const evtSrc = new EventSource(`/api/research?q=${encodeURIComponent(question)}`);
    evtSrc.onmessage = (e) => {
      if (e.data === '[DONE]') {
        evtSrc.close();
        setIsLoading(false);
        // Refresh the reports list after completion
        fetchPreviousReports();
      } else if (e.data.startsWith('RESEARCH_ID:')) {
        const id = e.data.split(':')[1];
        setResearchId(id);
      } else {
        setLines((l) => [...l, e.data]);
      }
    };
    
    evtSrc.onerror = () => {
      setIsLoading(false);
      evtSrc.close();
    };
  };

  const downloadReport = (format, id = null) => {
    const reportId = id || researchId;
    if (reportId) {
      const link = document.createElement('a');
      link.href = `/api/download/${reportId}/${format}`;
      link.download = `research_report.${format}`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    }
  };

  return (
    <div style={{ margin: '2em', fontFamily: 'Arial, sans-serif' }}>
      <h1 style={{ color: '#333', borderBottom: '2px solid #007acc', paddingBottom: '0.5em' }}>Deep Crawler</h1>
      <div style={{ marginBottom: '1em' }}>
        <input 
          style={{ 
            width: '60%', 
            padding: '0.5em', 
            fontSize: '16px',
            border: '1px solid #ddd',
            borderRadius: '4px',
            marginRight: '0.5em'
          }} 
          value={question} 
          onChange={e => setQuestion(e.target.value)} 
          placeholder="Research question"
          disabled={isLoading}
        />
        <button 
          style={{
            padding: '0.5em 1em',
            fontSize: '16px',
            backgroundColor: isLoading ? '#ccc' : '#007acc',
            color: 'white',
            border: 'none',
            borderRadius: '4px',
            cursor: isLoading ? 'not-allowed' : 'pointer'
          }}
          onClick={handleSubmit}
          disabled={isLoading}
        >
          {isLoading ? 'Running...' : 'Run'}
        </button>
      </div>
      
      {researchId && !isLoading && (
        <div style={{ marginBottom: '1em', padding: '1em', backgroundColor: '#e8f4f8', borderRadius: '4px' }}>
          <h3 style={{ margin: '0 0 0.5em 0' }}>Download Report:</h3>
          <button 
            style={{ margin: '0.25em', padding: '0.5em 1em', backgroundColor: '#28a745', color: 'white', border: 'none', borderRadius: '4px', cursor: 'pointer' }}
            onClick={() => downloadReport('markdown')}
          >
            Download Markdown
          </button>
          <button 
            style={{ margin: '0.25em', padding: '0.5em 1em', backgroundColor: '#dc3545', color: 'white', border: 'none', borderRadius: '4px', cursor: 'pointer' }}
            onClick={() => downloadReport('pdf')}
          >
            Download PDF
          </button>
          <button 
            style={{ margin: '0.25em', padding: '0.5em 1em', backgroundColor: '#007bff', color: 'white', border: 'none', borderRadius: '4px', cursor: 'pointer' }}
            onClick={() => downloadReport('docx')}
          >
            Download DOCX
          </button>
        </div>
      )}
      
      {/* Previous Reports Section */}
      <div style={{ marginBottom: '1em' }}>
        <button 
          style={{
            padding: '0.5em 1em',
            backgroundColor: '#6c757d',
            color: 'white',
            border: 'none',
            borderRadius: '4px',
            cursor: 'pointer'
          }}
          onClick={() => setShowPrevious(!showPrevious)}
        >
          {showPrevious ? 'Hide' : 'Show'} Previous Reports ({previousReports.length})
        </button>
        
        {showPrevious && (
          <div style={{ 
            marginTop: '1em', 
            border: '1px solid #ddd', 
            borderRadius: '4px', 
            padding: '1em',
            backgroundColor: '#f8f9fa'
          }}>
            <h3 style={{ margin: '0 0 1em 0' }}>Previous Research Reports</h3>
            {previousReports.length === 0 ? (
              <p style={{ margin: 0, color: '#666' }}>No previous reports found.</p>
            ) : (
              <div style={{ maxHeight: '300px', overflowY: 'auto' }}>
                {previousReports.map((report) => (
                  <div key={report.id} style={{ 
                    marginBottom: '0.5em', 
                    padding: '0.5em', 
                    border: '1px solid #e0e0e0', 
                    borderRadius: '4px',
                    backgroundColor: 'white'
                  }}>
                    <div style={{ fontWeight: 'bold', marginBottom: '0.25em' }}>
                      {report.question}
                    </div>
                    <div style={{ fontSize: '0.9em', color: '#666', marginBottom: '0.5em' }}>
                      {new Date(report.created_at).toLocaleString()}
                      {report.has_content ? ' ✓ Complete' : report.has_error ? ' ✗ Error' : ' ... Processing'}
                    </div>
                    {report.has_content && (
                      <div>
                        <button 
                          style={{ margin: '0.25em', padding: '0.25em 0.5em', backgroundColor: '#6f42c1', color: 'white', border: 'none', borderRadius: '4px', cursor: 'pointer', fontSize: '0.8em' }}
                          onClick={() => previewReportContent(report.id)}
                        >
                          Preview
                        </button>
                        <button 
                          style={{ margin: '0.25em', padding: '0.25em 0.5em', backgroundColor: '#28a745', color: 'white', border: 'none', borderRadius: '4px', cursor: 'pointer', fontSize: '0.8em' }}
                          onClick={() => downloadReport('markdown', report.id)}
                        >
                          MD
                        </button>
                        <button 
                          style={{ margin: '0.25em', padding: '0.25em 0.5em', backgroundColor: '#dc3545', color: 'white', border: 'none', borderRadius: '4px', cursor: 'pointer', fontSize: '0.8em' }}
                          onClick={() => downloadReport('pdf', report.id)}
                        >
                          PDF
                        </button>
                        <button 
                          style={{ margin: '0.25em', padding: '0.25em 0.5em', backgroundColor: '#007bff', color: 'white', border: 'none', borderRadius: '4px', cursor: 'pointer', fontSize: '0.8em' }}
                          onClick={() => downloadReport('docx', report.id)}
                        >
                          DOCX
                        </button>
                        <button 
                          style={{ margin: '0.25em', padding: '0.25em 0.5em', backgroundColor: '#6c757d', color: 'white', border: 'none', borderRadius: '4px', cursor: 'pointer', fontSize: '0.8em' }}
                          onClick={() => deleteReport(report.id)}
                        >
                          Delete
                        </button>
                      </div>
                    )}
                    {!report.has_content && (
                      <button 
                        style={{ margin: '0.25em', padding: '0.25em 0.5em', backgroundColor: '#6c757d', color: 'white', border: 'none', borderRadius: '4px', cursor: 'pointer', fontSize: '0.8em' }}
                        onClick={() => deleteReport(report.id)}
                      >
                        Delete
                      </button>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </div>
      
      <div style={{ 
        backgroundColor: '#f5f5f5', 
        border: '1px solid #ddd', 
        borderRadius: '4px', 
        padding: '1em',
        minHeight: '200px'
      }}>
        <pre style={{ whiteSpace: 'pre-wrap', fontFamily: 'inherit', margin: 0 }}>
          {lines.join('\n')}
          {isLoading && <span style={{ color: '#007acc' }}>● Researching...</span>}
        </pre>
      </div>
      
      {/* Preview Modal */}
      {showPreview && previewReport && (
        <div style={{
          position: 'fixed',
          top: 0,
          left: 0,
          width: '100%',
          height: '100%',
          backgroundColor: 'rgba(0,0,0,0.5)',
          display: 'flex',
          justifyContent: 'center',
          alignItems: 'center',
          zIndex: 1000
        }}>
          <div style={{
            backgroundColor: 'white',
            borderRadius: '8px',
            padding: '2em',
            maxWidth: '90%',
            maxHeight: '90%',
            overflow: 'auto',
            position: 'relative'
          }}>
            <button 
              style={{
                position: 'absolute',
                top: '10px',
                right: '15px',
                background: 'none',
                border: 'none',
                fontSize: '24px',
                cursor: 'pointer',
                color: '#999'
              }}
              onClick={() => setShowPreview(false)}
            >
              ×
            </button>
            
            <h2 style={{ marginTop: 0, marginBottom: '1em', color: '#333' }}>
              {previewReport.question}
            </h2>
            
            <div style={{ fontSize: '0.9em', color: '#666', marginBottom: '1em' }}>
              Generated: {new Date(previewReport.generated_at).toLocaleString()}
            </div>
            
            <div style={{
              backgroundColor: '#f8f9fa',
              border: '1px solid #e9ecef',
              borderRadius: '4px',
              padding: '1em',
              whiteSpace: 'pre-wrap',
              fontFamily: 'Georgia, serif',
              lineHeight: '1.6',
              maxHeight: '60vh',
              overflow: 'auto'
            }}>
              {previewReport.content}
            </div>
            
            <div style={{ marginTop: '1em', textAlign: 'center' }}>
              <button 
                style={{ margin: '0.5em', padding: '0.5em 1em', backgroundColor: '#28a745', color: 'white', border: 'none', borderRadius: '4px', cursor: 'pointer' }}
                onClick={() => downloadReport('markdown', previewReport.id)}
              >
                Download Markdown
              </button>
              <button 
                style={{ margin: '0.5em', padding: '0.5em 1em', backgroundColor: '#dc3545', color: 'white', border: 'none', borderRadius: '4px', cursor: 'pointer' }}
                onClick={() => downloadReport('pdf', previewReport.id)}
              >
                Download PDF
              </button>
              <button 
                style={{ margin: '0.5em', padding: '0.5em 1em', backgroundColor: '#007bff', color: 'white', border: 'none', borderRadius: '4px', cursor: 'pointer' }}
                onClick={() => downloadReport('docx', previewReport.id)}
              >
                Download DOCX
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

createRoot(document.getElementById('root')).render(<App />);
