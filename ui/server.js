const express = require('express');
const { spawn } = require('child_process');
const path = require('path');

const app = express();
const PORT = process.env.PORT || 3000;

app.use(express.static(path.join(__dirname, 'public')));

app.get('/api/research', (req, res) => {
  const question = req.query.q;
  if (!question) {
    res.status(400).send('Missing q parameter');
    return;
  }
  res.setHeader('Content-Type', 'text/event-stream');
  res.setHeader('Cache-Control', 'no-cache');
  res.setHeader('Connection', 'keep-alive');

  const proc = spawn('python3', ['-m', 'deep_crawler.cli', question]);
  proc.stdout.on('data', (data) => {
    data.toString().split(/\r?\n/).forEach(line => {
      if (line) res.write(`data: ${line}\n\n`);
    });
  });
  proc.stderr.on('data', (data) => {
    data.toString().split(/\r?\n/).forEach(line => {
      if (line) res.write(`data: ERR ${line}\n\n`);
    });
  });
  proc.on('close', () => {
    res.write('data: [DONE]\n\n');
    res.end();
  });
});

app.listen(PORT, () => {
  console.log(`Server running on http://localhost:${PORT}`);
});
