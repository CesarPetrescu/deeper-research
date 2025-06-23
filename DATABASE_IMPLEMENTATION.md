# Persistent Research Storage Implementation

## Overview

The Deep Crawler system now uses SQLite database storage for research reports instead of in-memory storage. This allows users to come back later and download their previous research results.

## Database Implementation

### Database Module (`deep_crawler/reports_db.py`)
- **Thread-safe SQLite connections**: Uses thread-local storage to avoid SQLite threading issues
- **Structured schema**: Stores research ID, question, content, errors, and timestamps
- **Comprehensive API**: Store, retrieve, list, and delete research reports

### Database Schema
```sql
CREATE TABLE research_reports (
    id TEXT PRIMARY KEY,           -- Unique research session ID
    question TEXT NOT NULL,        -- Original research question
    content TEXT,                  -- Generated markdown content
    error TEXT,                    -- Error message (if failed)
    stream_output TEXT,            -- Console output during generation
    generated_at TEXT NOT NULL,    -- When research completed
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Database Location
- **File**: `deep_crawler/research_reports.db`
- **Gitignored**: Added to `.gitignore` to avoid committing user data
- **Automatic creation**: Database and schema created automatically on first use

## API Enhancements

### New Endpoints
- `GET /api/reports` - List recent research reports with pagination
- `GET /api/reports/<id>` - Get specific research report details  
- `DELETE /api/reports/<id>` - Delete a research report

### Enhanced Endpoints
- `GET /api/download/<id>/<format>` - Now works with persistent storage
- `POST /api/research` - Now stores results in database

### Response Format
```json
{
  "reports": [
    {
      "id": "uuid-string",
      "question": "Research question",
      "generated_at": "2025-06-22T...",
      "created_at": "2025-06-22T...",
      "has_content": 1,
      "has_error": 0
    }
  ],
  "limit": 50,
  "offset": 0
}
```

## UI Improvements

### Previous Reports Section
- **Toggle view**: Show/hide previous reports list
- **Report status**: Visual indicators for complete/error/processing
- **Direct downloads**: Download buttons for each completed report
- **Auto-refresh**: Updates list after new research completes

### Enhanced UX
- **Persistent access**: Users can close browser and return later
- **Quick access**: Download any previous report without re-running research
- **Visual status**: Clear indication of report completion status

## Configuration Updates

### Gitignore Additions
```ignore
# Database files
*.sqlite
*.db
research_reports.db
```

### No Config Changes Required
- Uses existing configuration system
- Database location relative to project root
- No additional settings needed

## Benefits

### User Experience
- **Persistent storage**: Research results survive server restarts
- **Easy access**: Download previous reports anytime
- **No re-work**: Don't lose research if browser closes
- **History tracking**: See all previous research questions

### System Benefits
- **Scalable**: Database handles many concurrent users
- **Reliable**: SQLite ACID compliance ensures data integrity
- **Efficient**: No memory bloat from storing reports in RAM
- **Searchable**: Future enhancement potential for search/filtering

### Development Benefits
- **Thread-safe**: Proper SQLite connection handling
- **Maintainable**: Clean separation of storage logic
- **Testable**: Database module can be tested independently
- **Extensible**: Easy to add features like search, tags, etc.

## Usage Examples

### CLI Testing
```bash
# Test database module
venv/bin/python deep_crawler/reports_db.py

# View database location
ls -la deep_crawler/research_reports.db
```

### API Testing
```bash
# List all reports
curl "http://localhost:3001/api/reports"

# Get specific report
curl "http://localhost:3001/api/reports/<research-id>"

# Download report
curl "http://localhost:3001/api/download/<research-id>/markdown"
```

### Web Interface
1. Visit http://localhost:3000
2. Click "Show Previous Reports" to see research history
3. Use download buttons to get reports in different formats
4. Reports persist between browser sessions

## Future Enhancements

### Potential Features
- **Search functionality**: Search reports by question or content
- **Tags/categories**: Organize reports by topic
- **Export options**: Bulk export of multiple reports
- **Report sharing**: Generate shareable links
- **Analytics**: Usage statistics and popular research topics

### Database Maintenance
- **Cleanup**: Built-in function to remove old reports
- **Backup**: Easy database backup/restore procedures
- **Migration**: Schema migration support for future updates

## Migration from Memory Storage

### Automatic Migration
- Existing in-memory reports are lost (expected behavior)
- New research automatically uses database storage
- No manual migration required
- Previous functionality preserved

### Backward Compatibility
- All existing API endpoints work unchanged
- UI behavior remains the same for current research
- Download functionality enhanced, not changed

The persistent storage implementation provides a much more professional and user-friendly research experience while maintaining all existing functionality!
