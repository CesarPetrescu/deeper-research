import React, { useState, useEffect } from 'react';
import { createRoot } from 'react-dom/client';
import ReactMarkdown from 'react-markdown';
import SearchBar from './components/SearchBar';
import ProgressDisplay from './components/ProgressDisplay';
import ReportHistory from './components/ReportHistory';
import PreviewModal from './components/PreviewModal';
import ResearchOutput from './components/ResearchOutput';

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

  useEffect(() => {
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

        if (e.data.includes('🤖 AI Planner:')) {
          setCurrentStep('AI analyzing question and creating strategy...');
          setProgress(5);
        } else if (e.data.includes('Research Plan:') && e.data.includes('keywords')) {
          setCurrentStep('Research plan created, identifying sources...');
          setProgress(10);
        } else if (e.data.includes('🔍 Searching for sources')) {
          setCurrentStep('Searching for relevant sources...');
          setProgress(15);
        } else if (e.data.includes('🔎') && e.data.includes('Searching:')) {
          const searchMatch = e.data.match(/\[(\d+)\/(\d+)\]/);
          if (searchMatch) {
            const current = parseInt(searchMatch[1]);
            const total = parseInt(searchMatch[2]);
            const searchProgress = 15 + (current / total * 10);
            setProgress(searchProgress);
            setCurrentStep(`Searching sources (${current}/${total})...`);
          }
        } else if (e.data.includes('🕷️ Starting web crawling')) {
          setCurrentStep('Starting web crawling process...');
          setProgress(25);
        } else if (e.data.includes('🌐') && e.data.includes('Crawling:')) {
          const crawlMatch = e.data.match(/\[(\d+)\/(\d+)\]/);
          if (crawlMatch) {
            const current = parseInt(crawlMatch[1]);
            const total = parseInt(crawlMatch[2]);
            const crawlProgress = 25 + (current / total * 25);
            setProgress(crawlProgress);
            setCurrentStep(`Crawling websites (${current}/${total})...`);
          }
        } else if (e.data.includes('✅ Crawling complete')) {
          setCurrentStep('Building knowledge index...');
          setProgress(50);
        } else if (e.data.includes('🔗 Building knowledge index')) {
          setCurrentStep('Processing documents and building search index...');
          setProgress(55);
        } else if (e.data.includes('✅ Search index built')) {
          setCurrentStep('Starting AI content generation...');
          setProgress(60);
        } else if (e.data.includes('🤖 AI Writer:')) {
          setCurrentStep('AI analyzing content and preparing sections...');
          setProgress(65);
        } else if (e.data.includes('📝 Section') && e.data.includes('/')) {
          const sectionMatch = e.data.match(/Section (\d+)\/(\d+)/);
          if (sectionMatch) {
            const current = parseInt(sectionMatch[1]);
            const total = parseInt(sectionMatch[2]);
            const sectionProgress = 65 + (current / total * 25);
            setProgress(sectionProgress);
            setCurrentStep(`AI writing section ${current} of ${total}...`);
          }
        } else if (e.data.includes('🤖 AI Analyzing:')) {
          setCurrentStep('AI analyzing sources for current section...');
        } else if (e.data.includes('🔍 AI Processing:')) {
          setCurrentStep('AI processing and synthesizing information...');
        } else if (e.data.includes('✅ AI Generated:')) {
          setCurrentStep('AI completed section, moving to next...');
        } else if (e.data.includes('📚 Adding references')) {
          setCurrentStep('Adding references and citations...');
          setProgress(90);
        } else if (e.data.includes('🔍 AI Verifier:')) {
          setCurrentStep('AI verifying citations and accuracy...');
          setProgress(95);
        } else if (e.data.includes('🎉 Research Complete')) {
          setCurrentStep('Finalizing report...');
          setProgress(98);
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

  return (
    <div style={{ 
      minHeight: '100vh',
      background: '#f0f2f5',
      fontFamily: '"Inter", -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif'
    }}>
      <div style={{ maxWidth: '1200px', margin: '0 auto', padding: '2rem' }}>
        <SearchBar 
          question={question} 
          setQuestion={setQuestion} 
          handleSubmit={handleSubmit} 
          isLoading={isLoading} 
        />
        <ProgressDisplay 
          isLoading={isLoading} 
          currentStep={currentStep} 
          progress={progress} 
        />
        <ResearchOutput 
          lines={lines} 
          isLoading={isLoading} 
          currentStep={currentStep} 
          progress={progress} 
          researchId={researchId} 
          downloadReport={downloadReport} 
        />
        <ReportHistory 
          showPrevious={showPrevious} 
          previousReports={previousReports} 
          previewReportContent={previewReportContent} 
          downloadReport={downloadReport} 
          deleteReport={deleteReport} 
        />
        <PreviewModal 
          showPreview={showPreview} 
          setShowPreview={setShowPreview} 
          previewReport={previewReport} 
          renderMarkdown={(content) => <ReactMarkdown>{content}</ReactMarkdown>} 
        />
      </div>
      <style>
        {`
          @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
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
