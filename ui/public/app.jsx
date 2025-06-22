import React, { useState } from 'react';
import { createRoot } from 'react-dom/client';
import { Markdown } from '@llm-ui/react';

function App() {
  const [question, setQuestion] = useState('');
  const [lines, setLines] = useState([]);
  const handleSubmit = () => {
    setLines([]);
    const evtSrc = new EventSource(`/api/research?q=${encodeURIComponent(question)}`);
    evtSrc.onmessage = (e) => {
      if (e.data === '[DONE]') evtSrc.close();
      else setLines((l) => [...l, e.data]);
    };
  };
  return (
    <div style={{ margin: '2em' }}>
      <h1>Deep Crawler</h1>
      <input style={{ width: '60%' }} value={question} onChange={e => setQuestion(e.target.value)} placeholder="Research question" />
      <button onClick={handleSubmit}>Run</button>
      <Markdown>{lines.join('\n')}</Markdown>
    </div>
  );
}

createRoot(document.getElementById('root')).render(<App />);
