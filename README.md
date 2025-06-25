# Deeper Research

An AI-powered research assistant with a modern web interface and a powerful command-line tool.

## Features

*   **Modern UI**: A clean, responsive, and intuitive web interface for a seamless research experience.
*   **Real-time Feedback**: Live progress updates and detailed step-by-step feedback during research.
*   **Persistent Storage**: SQLite database for storing all research reports.
*   **Multiple Export Formats**: Download reports in Markdown, PDF, and DOCX formats.
*   **Research History**: View, preview, and manage all previous research.
*   **Unified Configuration**: A single `config.toml` file for all settings.

## Getting Started

### Prerequisites

*   Python 3.8+
*   Node.js 14+

### Installation

1.  **Clone the repository:**

    ```bash
    git clone https://github.com/your-username/deeper-research.git
    cd deeper-research
    ```

2.  **Install Python dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

3.  **Install UI dependencies:**

    ```bash
    cd ui
    npm install
    npm run build
    cd ..
    ```

### Configuration

1.  **Copy the example configuration file:**

    ```bash
    cp .env.example .env
    ```

2.  **Edit the `config.toml` file:**

    ```toml
    [llm]
    base_url      = "http://192.168.100.199:5515/v1"
    api_key       = "none"
    chat_model    = "mistral-small-3.2-24b-instruct-2506"
    embed_model   = "text-embedding-granite-embedding-278m-multilingual"
    temperature   = 0.7
    max_tokens    = 4096
    use_langgraph = false

    [firecrawl]
    base_url      = "http://localhost:3002"
    concurrency   = 8
    limit_per_url = 15

    [search]
    searx_url         = "https://searx.sprk.ro/search"
    urls_per_keyword  = 6

    [index]
    snippets_per_sec  = 12

    [server]
    api_host     = "0.0.0.0"
    api_port     = 3001
    ui_host      = "0.0.0.0"
    ui_port      = 3000
    api_backend  = "http://127.0.0.1:3001"
    ```

### Running the Application

1.  **Start the backend server:**

    ```bash
    ./start_services.sh
    ```

2.  **Access the web interface:**

    Open [http://localhost:3000](http://localhost:3000) in your browser.

## Usage

### Web Interface

The web interface provides a user-friendly way to interact with the research assistant. You can:

*   **Start a new research:** Enter a question in the search bar and click "Start Research".
*   **View research history:** Click the "History" button to see a list of your previous research reports.
*   **Preview a report:** Click the "Preview" button to see a preview of a report.
*   **Download a report:** Click the "Markdown", "PDF", or "DOCX" buttons to download a report in the corresponding format.
*   **Delete a report:** Click the "Delete" button to delete a report.

### Command-Line Interface

You can also use the command-line interface to run the research assistant:

```bash
python deep_crawler/cli.py "Your research question"
```

## Project Structure

```
├── config.toml
├── deep_crawler
│   ├── __init__.py
│   ├── api_server.py
│   ├── cli.py
│   ├── enhanced_cli.py
│   ├── reports_db.py
│   ├── crawler
│   ├── indexing
│   └── llm
├── tests
│   └── test_reports_db.py
└── ui
    ├── public
    │   ├── components
    │   │   ├── PreviewModal.jsx
    │   │   ├── ProgressDisplay.jsx
    │   │   ├── ReportHistory.jsx
    │   │   ├── ResearchOutput.jsx
    │   │   └── SearchBar.jsx
    │   ├── app.jsx
    │   └── index.html
    ├── server.js
    └── package.json
```