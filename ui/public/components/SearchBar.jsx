import React from 'react';

function SearchBar({ question, setQuestion, handleSubmit, isLoading, showPrevious, setShowPrevious, previousReports }) {
  return (
    <div style={{
      background: '#ffffff',
      borderRadius: '16px',
      padding: '2rem',
      marginBottom: '2rem',
      boxShadow: '0 10px 30px -5px rgba(0, 0, 0, 0.07)',
    }}>
      <div style={{ marginBottom: '1.5rem' }}>
        <div style={{ position: 'relative' }}>
          <input 
            style={{ 
              width: '100%',
              padding: '1rem 1.5rem',
              fontSize: '1.1rem',
              border: '1px solid #e2e8f0',
              borderRadius: '12px',
              outline: 'none',
              transition: 'all 0.3s ease',
              background: '#f7fafc',
            }} 
            value={question} 
            onChange={e => setQuestion(e.target.value)} 
            placeholder="Ask me anything... e.g., 'Latest trends in AI', 'Climate change solutions'"
            disabled={isLoading}
            onKeyPress={e => e.key === 'Enter' && !isLoading && handleSubmit()}
          />
        </div>
      </div>
      
      <div style={{ display: 'flex', gap: '1rem', alignItems: 'center' }}>
        <button 
          style={{
            background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
            color: 'white',
            border: 'none',
            borderRadius: '12px',
            padding: '0.75rem 2rem',
            fontSize: '1.1rem',
            fontWeight: '600',
            cursor: isLoading ? 'not-allowed' : 'pointer',
            transition: 'all 0.3s ease',
            boxShadow: '0 4px 15px rgba(102, 126, 234, 0.4)',
          }}
          onClick={handleSubmit}
          disabled={isLoading || !question.trim()}
        >
          {isLoading ? '🔄 Researching...' : '🔍 Start Research'}
        </button>
        
        <button 
          style={{
            background: '#f1f5f9',
            color: '#475569',
            border: 'none',
            borderRadius: '12px',
            padding: '0.75rem 1.5rem',
            fontSize: '1rem',
            fontWeight: '500',
            cursor: 'pointer',
            transition: 'all 0.3s ease'
          }}
          onClick={() => setShowPrevious(!showPrevious)}
        >
          📚 History ({previousReports.length})
        </button>
      </div>
    </div>
  );
}

export default SearchBar;
