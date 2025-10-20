## Computer Use v2

This monorepo implements a modern alternative to the Anthropic's open-source [Computer Use demo](https://github.com/anthropics/anthropic-quickstarts/tree/main/computer-use-demo) using Next.js and FastAPI, featuring real-time task execution, file management, and VNC integration.

## Getting Started

### Prerequisites

- Node.js 18+
- Python 3.11+
- Docker
- Anthropic API key

### Development Setup

1. Create environment file:

   ```bash
   npm run setup:env
   ```

2. Configure your environment:

   - Get your API key from [Anthropic's Console](https://console.anthropic.com)
   - Open `apps/backend/.env` and replace `your_anthropic_api_key_here` with your actual API key
   - The API key should look something like:
     ```env
     ANTHROPIC_API_KEY=sk-ant-xxxx...
     ```

3. Start the API server:

   ```bash
   npm run dev:api
   ```

4. In a new terminal, start the web server:

   ```bash
   npm run dev:web
   ```

5. Open [http://localhost:3000](http://localhost:3000) in your browser.

The following services are exposed on localhost:

- Frontend: port 3000
- API: port 8000
- VNC: port 5900 (raw VNC) or port 6080 (noVNC)

### VS Code Extensions

This project includes recommended VS Code extensions for Python and JavaScript development. VS Code will automatically suggest installing these when you open the project:

- Python tooling (language support, Black formatter, isort)
- JavaScript/TypeScript tooling (Prettier, ESLint, Tailwind CSS)
- Docker support
- Code formatting and wrapping

## Tech Stack

- **Frontend**: Next.js
- **Backend**: Python FastAPI
- **Database**: SQLite
- **Real-time**: WebSockets
- **UI Components**: shadcn/ui
- **AI Integration**: Anthropic Claude API
- **Infrastructure**: Docker, Kubernetes (GCP)

## System Architecture

![mermaid-diagram-2025-04-06-192932](https://github.com/user-attachments/assets/5260e56e-8e28-4420-9aae-d58433b275df)

## Features

- Real-time task execution with progress streaming
- File upload and management
- VNC integration for remote desktop view
- Chat-like interface with message history

## Database Schema

The application uses SQLite with the following table structure:

### Sessions Table

```sql
CREATE TABLE sessions (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    status TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NOT NULL
)
```

### Files Table

```sql
CREATE TABLE files (
    id TEXT PRIMARY KEY,
    filename TEXT NOT NULL,
    path TEXT NOT NULL,
    mime_type TEXT,
    size INTEGER NOT NULL,
    uploaded_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP,
    session_id TEXT,
    FOREIGN KEY (session_id) REFERENCES sessions (id) ON DELETE CASCADE
)
```

### Messages Table

```sql
CREATE TABLE messages (
    id TEXT PRIMARY KEY,
    session_id TEXT NOT NULL,
    role TEXT NOT NULL, -- 'user' or 'assistant'
    content TEXT NOT NULL,  -- JSON object of content block
    message TEXT,  -- Optional human-readable message text
    created_at TIMESTAMP NOT NULL,
    FOREIGN KEY (session_id) REFERENCES sessions (id) ON DELETE CASCADE
)
```

#### Relationships

- Each session can have multiple messages (one-to-many)
- Each session can have multiple files (one-to-many)
- Messages and files are deleted when their parent session is deleted (CASCADE)
