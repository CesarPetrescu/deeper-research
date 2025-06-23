const express = require('express');
const { spawn } = require('child_process');
const path = require('path');
const fs = require('fs');

// Load configuration
const config = JSON.parse(fs.readFileSync(path.join(__dirname, 'config.json'), 'utf8'));

const app = express();
const PORT = config.server.port || process.env.PORT || 3000;
const API_BASE_URL = config.api.baseUrl;

app.use(express.static(path.join(__dirname, 'dist')));

app.get('/api/research', (req, res) => {
  const question = req.query.q;
  if (!question) {
    res.status(400).send('Missing q parameter');
    return;
  }
  res.setHeader('Content-Type', 'text/event-stream');
  res.setHeader('Cache-Control', 'no-cache');
  res.setHeader('Connection', 'keep-alive');

  // Forward the request to the Python API server using config
  const apiUrl = `${API_BASE_URL}/api/research?q=${encodeURIComponent(question)}`;
  
  const http = require('http');
  const url = require('url');
  const parsedUrl = url.parse(apiUrl);
  
  const options = {
    hostname: parsedUrl.hostname,
    port: parsedUrl.port,
    path: parsedUrl.path,
    method: 'GET',
    headers: {
      'Accept': 'text/event-stream',
      'Cache-Control': 'no-cache'
    }
  };

  const apiReq = http.request(options, (apiRes) => {
    apiRes.on('data', (chunk) => {
      res.write(chunk);
    });
    
    apiRes.on('end', () => {
      res.end();
    });
    
    apiRes.on('error', (error) => {
      res.write(`data: ERROR: ${error.message}\n\n`);
      res.end();
    });
  });

  apiReq.on('error', (error) => {
    res.write(`data: ERROR: Could not connect to Python API server: ${error.message}\n\n`);
    res.end();
  });

  apiReq.end();
});

// Proxy reports list endpoint
app.get('/api/reports', (req, res) => {
  const limit = req.query.limit || 50;
  const offset = req.query.offset || 0;
  const apiUrl = `${API_BASE_URL}/api/reports?limit=${limit}&offset=${offset}`;
  
  const http = require('http');
  const url = require('url');
  const parsedUrl = url.parse(apiUrl);
  
  const options = {
    hostname: parsedUrl.hostname,
    port: parsedUrl.port,
    path: parsedUrl.path,
    method: 'GET'
  };

  const apiReq = http.request(options, (apiRes) => {
    // Copy headers from API response
    Object.keys(apiRes.headers).forEach(key => {
      res.setHeader(key, apiRes.headers[key]);
    });
    res.status(apiRes.statusCode);
    
    apiRes.pipe(res);
  });

  apiReq.on('error', (error) => {
    res.status(500).send(`Could not connect to Python API server: ${error.message}`);
  });

  apiReq.end();
});

// Proxy individual report endpoint
app.get('/api/reports/:researchId', (req, res) => {
  const { researchId } = req.params;
  const apiUrl = `${API_BASE_URL}/api/reports/${researchId}`;
  
  const http = require('http');
  const url = require('url');
  const parsedUrl = url.parse(apiUrl);
  
  const options = {
    hostname: parsedUrl.hostname,
    port: parsedUrl.port,
    path: parsedUrl.path,
    method: 'GET'
  };

  const apiReq = http.request(options, (apiRes) => {
    // Copy headers from API response
    Object.keys(apiRes.headers).forEach(key => {
      res.setHeader(key, apiRes.headers[key]);
    });
    res.status(apiRes.statusCode);
    
    apiRes.pipe(res);
  });

  apiReq.on('error', (error) => {
    res.status(500).send(`Could not connect to Python API server: ${error.message}`);
  });

  apiReq.end();
});

// Proxy delete report endpoint
app.delete('/api/reports/:researchId', (req, res) => {
  const { researchId } = req.params;
  const apiUrl = `${API_BASE_URL}/api/reports/${researchId}`;
  
  const http = require('http');
  const url = require('url');
  const parsedUrl = url.parse(apiUrl);
  
  const options = {
    hostname: parsedUrl.hostname,
    port: parsedUrl.port,
    path: parsedUrl.path,
    method: 'DELETE'
  };

  const apiReq = http.request(options, (apiRes) => {
    // Copy headers from API response
    Object.keys(apiRes.headers).forEach(key => {
      res.setHeader(key, apiRes.headers[key]);
    });
    res.status(apiRes.statusCode);
    
    apiRes.pipe(res);
  });

  apiReq.on('error', (error) => {
    res.status(500).send(`Could not connect to Python API server: ${error.message}`);
  });

  apiReq.end();
});

// Proxy download endpoints
app.get('/api/download/:researchId/:format', (req, res) => {
  const { format, researchId } = req.params;
  const apiUrl = `${API_BASE_URL}/api/download/${researchId}/${format}`;
  
  const http = require('http');
  const url = require('url');
  const parsedUrl = url.parse(apiUrl);
  
  const options = {
    hostname: parsedUrl.hostname,
    port: parsedUrl.port,
    path: parsedUrl.path,
    method: 'GET'
  };

  const apiReq = http.request(options, (apiRes) => {
    // Copy headers from API response
    Object.keys(apiRes.headers).forEach(key => {
      res.setHeader(key, apiRes.headers[key]);
    });
    res.status(apiRes.statusCode);
    
    apiRes.pipe(res);
  });

  apiReq.on('error', (error) => {
    res.status(500).send(`Could not connect to Python API server: ${error.message}`);
  });

  apiReq.end();
});

app.listen(PORT, config.server.host, () => {
  console.log(`Server running on http://${config.server.host}:${PORT}`);
});
