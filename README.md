# deeper-research

This repository contains a small research assistant built around the
`deep_crawler` package.  The original `monolithic.py` script has been broken
up into a minimal set of modules.  Configuration lives in `deep_crawler/config.toml`
and can be overridden via environment variables (see `.env.example`).

## Structure

```
deep_crawler/
├── config.toml
├── cli.py
├── crawler/
│   ├── firecrawl_async.py
│   └── extractor.py
├── indexing/
│   ├── embed_cache.py
│   └── faiss_store.py
└── llm/
    ├── core.py
    ├── planner.py
    ├── summariser.py
    └── verifier.py
```

Run `deep_crawler/cli.py` with a research question to produce a referenced
Markdown report.

## Browser UI

A simple web interface lives in the `ui/` folder.  It uses Node, Express and
[`@llm-ui/react`](https://www.npmjs.com/package/@llm-ui/react) to stream the
Markdown report to your browser.  Build the frontend and start the server:

```bash
cd ui
npm install
npm run build
npm start
```

Then visit [http://localhost:3000](http://localhost:3000) and enter a research
question to see the report appear live.
