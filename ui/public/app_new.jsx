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
  const [currentStep, setCurrentStep] = useState('');
  const [progress, setProgress] = useState(0);
  
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
        fetchPreviousReports();
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
    setCurrentStep('Starting research...');
    setProgress(0);
    
    const evtSrc = new EventSource(`/api/research?q=${encodeURIComponent(question)}`);
    evtSrc.onmessage = (e) => {
      if (e.data === '[DONE]') {
        evtSrc.close();
        setIsLoading(false);
        setCurrentStep('Research completed!');
        setProgress(100);
        fetchPreviousReports();
      } else if (e.data.startsWith('RESEARCH_ID:')) {
        const id = e.data.split(':')[1];
        setResearchId(id);
        setCurrentStep('Research plan created...');
        setProgress(10);
      } else {
        setLines((l) => [...l, e.data]);
        
        // Update progress and step based on content
        if (e.data.includes('🔍 Researching:')) {
          setCurrentStep('Planning research strategy...');
          setProgress(5);
        } else if (e.data.includes('📋 Research Plan:')) {
          setCurrentStep('Gathering sources...');
          setProgress(15);
        } else if (e.data.includes('🌐 Found') && e.data.includes('URLs')) {
          setCurrentStep('Crawling websites...');
          setProgress(25);
        } else if (e.data.includes('📄 Successfully crawled')) {
          setCurrentStep('Building knowledge index...');
          setProgress(40);
        } else if (e.data.includes('🔗 Built search index')) {
          setCurrentStep('Writing report sections...');
          setProgress(50);
        } else if (e.data.includes('✍️ Writing') && e.data.includes('sections')) {
          setCurrentStep('Analyzing and writing...');
          setProgress(60);
        } else if (e.data.includes('📝 Section')) {
          const match = e.data.match(/Section (\d+)\/(\d+)/);
          if (match) {
            const current = parseInt(match[1]);
            const total = parseInt(match[2]);
            const sectionProgress = 60 + (current / total * 30);
            setProgress(sectionProgress);
            setCurrentStep(`Writing section ${current} of ${total}...`);
          }
        } else if (e.data.includes('📚 Adding references')) {
          setCurrentStep('Finalizing references...');
          setProgress(95);
        }
      }
    };
    
    evtSrc.onerror = () => {
      setIsLoading(false);
      setCurrentStep('Error occurred');
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

  const renderMarkdown = (content) => {
    if (!content) return null;
    
    // Simple markdown rendering
    return content.split('\n').map((line, index) => {
      if (line.startsWith('# ')) {
        return <h1 key={index} style={{ fontSize: '2em', fontWeight: 'bold', margin: '1em 0 0.5em 0', color: '#1a202c' }}>{line.slice(2)}</h1>;
      } else if (line.startsWith('## ')) {
        return <h2 key={index} style={{ fontSize: '1.5em', fontWeight: 'bold', margin: '1.5em 0 0.5em 0', color: '#2d3748' }}>{line.slice(3)}</h2>;
      } else if (line.startsWith('### ')) {
        return <h3 key={index} style={{ fontSize: '1.2em', fontWeight: 'bold', margin: '1em 0 0.5em 0', color: '#4a5568' }}>{line.slice(4)}</h3>;
      } else if (line.trim() === '') {
        return <br key={index} />;
      } else {
        return <p key={index} style={{ margin: '0.5em 0', lineHeight: '1.6', color: '#2d3748' }}>{line}</p>;
      }
    });
  };

  return (
    <div style={{ 
      minHeight: '100vh',
      background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
      fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif'
    }}>
      {/* Header */}
      <div style={{
        background: 'rgba(255, 255, 255, 0.95)',
        backdropFilter: 'blur(20px)',
        borderBottom: '1px solid rgba(255, 255, 255, 0.2)',
        padding: '1rem 0'
      }}>
        <div style={{ maxWidth: '1200px', margin: '0 auto', padding: '0 2rem' }}>
          <h1 style={{ 
            margin: 0, 
            fontSize: '2.5rem', 
            fontWeight: '700',
            background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent',
            textAlign: 'center'
          }}>
            ✨ Deep Crawler AI Research
          </h1>
          <p style={{ 
            textAlign: 'center', 
            margin: '0.5rem 0 0 0', 
            color: '#6b7280',
            fontSize: '1.1rem'
          }}>
            Advanced AI-powered research assistant
          </p>
        </div>
      </div>

      <div style={{ maxWidth: '1200px', margin: '0 auto', padding: '2rem' }}>
        
        {/* Search Section */}
        <div style={{
          background: 'rgba(255, 255, 255, 0.95)',
          backdropFilter: 'blur(20px)',
          borderRadius: '24px',
          padding: '2rem',
          marginBottom: '2rem',
          boxShadow: '0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)',
          border: '1px solid rgba(255, 255, 255, 0.2)'
        }}>
          <div style={{ marginBottom: '1.5rem' }}>
            <div style={{ position: 'relative' }}>
              <input 
                style={{ 
                  width: '100%',
                  padding: '1rem 1.5rem',
                  fontSize: '1.1rem',
                  border: '2px solid #e2e8f0',
                  borderRadius: '16px',
                  outline: 'none',
                  transition: 'all 0.3s ease',
                  background: '#ffffff',
                  boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)'
                }} 
                value={question} 
                onChange={e => setQuestion(e.target.value)} 
                placeholder="Ask me anything... e.g., 'Latest trends in AI', 'Climate change solutions'"
                disabled={isLoading}
                onKeyPress={e => e.key === 'Enter' && !isLoading && handleSubmit()}
                onFocus={e => e.target.style.borderColor = '#667eea'}
                onBlur={e => e.target.style.borderColor = '#e2e8f0'}
              />
            </div>
          </div>
          
          <div style={{ display: 'flex', gap: '1rem', alignItems: 'center' }}>
            <button 
              style={{
                background: isLoading 
                  ? 'linear-gradient(135deg, #9ca3af 0%, #6b7280 100%)' 
                  : 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                color: 'white',
                border: 'none',
                borderRadius: '12px',
                padding: '0.75rem 2rem',
                fontSize: '1.1rem',
                fontWeight: '600',
                cursor: isLoading ? 'not-allowed' : 'pointer',
                transition: 'all 0.3s ease',
                boxShadow: '0 4px 15px rgba(102, 126, 234, 0.4)',
                transform: isLoading ? 'scale(0.98)' : 'scale(1)'
              }}
              onClick={handleSubmit}
              disabled={isLoading || !question.trim()}
              onMouseEnter={e => {
                if (!isLoading) {
                  e.target.style.transform = 'scale(1.05)';
                  e.target.style.boxShadow = '0 6px 20px rgba(102, 126, 234, 0.6)';
                }
              }}
              onMouseLeave={e => {
                if (!isLoading) {
                  e.target.style.transform = 'scale(1)';
                  e.target.style.boxShadow = '0 4px 15px rgba(102, 126, 234, 0.4)';
                }
              }}
            >
              {isLoading ? '🔄 Researching...' : '🔍 Start Research'}
            </button>
            
            <button 
              style={{
                background: 'rgba(107, 114, 128, 0.1)',
                color: '#374151',
                border: '2px solid #e5e7eb',
                borderRadius: '12px',
                padding: '0.75rem 1.5rem',
                fontSize: '1rem',
                fontWeight: '500',
                cursor: 'pointer',
                transition: 'all 0.3s ease'
              }}
              onClick={() => setShowPrevious(!showPrevious)}
              onMouseEnter={e => {
                e.target.style.background = 'rgba(107, 114, 128, 0.2)';
                e.target.style.borderColor = '#9ca3af';
              }}
              onMouseLeave={e => {
                e.target.style.background = 'rgba(107, 114, 128, 0.1)';
                e.target.style.borderColor = '#e5e7eb';
              }}
            >
              📚 History ({previousReports.length})
            </button>
          </div>
        </div>

        {/* Progress Section */}
        {isLoading && (
          <div style={{
            background: 'rgba(255, 255, 255, 0.95)',
            backdropFilter: 'blur(20px)',
            borderRadius: '20px',
            padding: '2rem',
            marginBottom: '2rem',
            boxShadow: '0 20px 25px -5px rgba(0, 0, 0, 0.1)',
            border: '1px solid rgba(255, 255, 255, 0.2)'
          }}>
            <div style={{ marginBottom: '1rem' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.5rem' }}>
                <span style={{ fontSize: '1.1rem', fontWeight: '600', color: '#374151' }}>{currentStep}</span>
                <span style={{ fontSize: '0.9rem', color: '#6b7280' }}>{Math.round(progress)}%</span>
              </div>
              <div style={{
                width: '100%',
                height: '8px',
                background: '#e5e7eb',
                borderRadius: '4px',
                overflow: 'hidden'
              }}>
                <div style={{
                  width: `${progress}%`,
                  height: '100%',
                  background: 'linear-gradient(90deg, #667eea 0%, #764ba2 100%)',
                  borderRadius: '4px',
                  transition: 'width 0.5s ease'
                }} />
              </div>
            </div>
          </div>
        )}

        {/* Current Research Results */}
        {researchId && !isLoading && (
          <div style={{
            background: 'rgba(255, 255, 255, 0.95)',
            backdropFilter: 'blur(20px)',
            borderRadius: '20px',
            padding: '2rem',
            marginBottom: '2rem',
            boxShadow: '0 20px 25px -5px rgba(0, 0, 0, 0.1)',
            border: '1px solid rgba(255, 255, 255, 0.2)'
          }}>
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
                  onMouseEnter={e => e.target.style.transform = 'translateY(-2px)'}
                  onMouseLeave={e => e.target.style.transform = 'translateY(0)'}
                >
                  📄 {format.toUpperCase()}
                </button>
              ))}
            </div>
          </div>
        )}
        
        {/* Previous Reports */}
        {showPrevious && (
          <div style={{
            background: 'rgba(255, 255, 255, 0.95)',
            backdropFilter: 'blur(20px)',
            borderRadius: '20px',
            padding: '2rem',
            marginBottom: '2rem',
            boxShadow: '0 20px 25px -5px rgba(0, 0, 0, 0.1)',
            border: '1px solid rgba(255, 255, 255, 0.2)'
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
                    background: 'rgba(249, 250, 251, 0.8)',
                    border: '1px solid #e5e7eb',
                    borderRadius: '16px',
                    padding: '1.5rem',
                    transition: 'all 0.3s ease'
                  }}
                  onMouseEnter={e => {
                    e.target.style.background = 'rgba(243, 244, 246, 0.9)';
                    e.target.style.transform = 'translateY(-2px)';
                    e.target.style.boxShadow = '0 10px 15px -3px rgba(0, 0, 0, 0.1)';
                  }}
                  onMouseLeave={e => {
                    e.target.style.background = 'rgba(249, 250, 251, 0.8)';
                    e.target.style.transform = 'translateY(0)';
                    e.target.style.boxShadow = 'none';
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
                            onMouseEnter={e => e.target.style.backgroundColor = '#4f46e5'}
                            onMouseLeave={e => e.target.style.backgroundColor = '#6366f1'}
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
                              onMouseEnter={e => e.target.style.opacity = '0.8'}
                              onMouseLeave={e => e.target.style.opacity = '1'}
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
                        onMouseEnter={e => e.target.style.backgroundColor = '#dc2626'}
                        onMouseLeave={e => e.target.style.backgroundColor = '#ef4444'}
                      >
                        🗑️ Delete
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
        
        {/* Research Output */}
        {(lines.length > 0 || isLoading) && (
          <div style={{
            background: 'rgba(255, 255, 255, 0.95)',
            backdropFilter: 'blur(20px)',
            borderRadius: '20px',
            padding: '2rem',
            marginBottom: '2rem',
            boxShadow: '0 20px 25px -5px rgba(0, 0, 0, 0.1)',
            border: '1px solid rgba(255, 255, 255, 0.2)'
          }}>
            <h3 style={{ 
              margin: '0 0 1.5rem 0', 
              fontSize: '1.5rem', 
              fontWeight: '700',
              color: '#1f2937'
            }}>
              🔬 Research Progress
            </h3>
            <div style={{ 
              background: '#1f2937',
              color: '#f9fafb',
              borderRadius: '12px',
              padding: '1.5rem',
              fontFamily: 'Monaco, Menlo, "Ubuntu Mono", monospace',
              fontSize: '0.9rem',
              lineHeight: '1.6',
              maxHeight: '500px',
              overflowY: 'auto',
              border: '1px solid #374151'
            }}>
              {lines.map((line, index) => (
                <div key={index} style={{ marginBottom: '0.5rem' }}>
                  {line}
                </div>
              ))}
              {isLoading && (
                <div style={{ 
                  color: '#60a5fa',
                  animation: 'pulse 2s infinite'
                }}>
                  ● {currentStep}
                </div>
              )}
            </div>
          </div>
        )}
      </div>

      {/* Preview Modal */}
      {showPreview && previewReport && (
        <div style={{
          position: 'fixed',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          background: 'rgba(0, 0, 0, 0.7)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          zIndex: 1000,
          padding: '2rem'
        }} onClick={() => setShowPreview(false)}>
          <div style={{
            background: 'white',
            borderRadius: '20px',
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
              borderBottom: '2px solid #f3f4f6',
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
                onMouseEnter={e => e.target.style.background = '#dc2626'}
                onMouseLeave={e => e.target.style.background = '#ef4444'}
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
      )}

      <style>
        {`
          @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
          }
          
          body {
            margin: 0;
            padding: 0;
          }
          
          * {
            box-sizing: border-box;
          }
        `}
      </style>
    </div>
  );
}

createRoot(document.getElementById('root')).render(<App />);
