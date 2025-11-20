# Media Insight API

A natural language interface for YouTube channel analytics.

## Overview

Media Insight API provides a natural language interface for accessing social media analytics, starting with YouTube channel metrics. Through LLM tool calling, users can query their analytics data using conversational language.

**Current Status**: YouTube channel analytics integration is fully functional. Support for YouTube video data and Reddit metrics is in development.

## Features

- **Natural Language Processing**: Query your YouTube metrics using conversational language
- **OAuth 2.0 Authentication**: Secure Google sign-in with automatic token refresh
- **Intelligent Tool Selection**: AI automatically determines which YouTube API endpoints to call
- **Session Management**: Redis-backed session storage for scalable user management
- **Type-Safe Architecture**: Full Pydantic validation for requests and responses

## Tech Stack

### Core Framework
- **FastAPI**: Modern async web framework for building APIs
- **Pydantic**: Data validation and settings management using Python type hints

### AI & Orchestration
- **Pydantic AI**: Orchestrates tool calling and manages LLM interactions
- **OpenAI GPT-4o-mini**: Powers natural language understanding and response generation

### Storage & Session Management
- **Redis**: Server-side session storage with JSON support for complex data structures

### Observability
- **Logfire**: Traces LLM interactions and monitors agent performance

### Authentication
- **Authlib**: OAuth 2.0 client implementation for Google and Reddit integration

## Getting Started

### Prerequisites

- Python 3.13+
- Redis server
- Google Cloud Console project with YouTube Data API v3 enabled
- OpenAI API key

### Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/media-insight-api.git
cd media-insight-api
```

2. Install dependencies:
```bash
pip install fastapi uvicorn redis authlib httpx pydantic-ai openai logfire pydantic-settings python-multipart
```

3. Copy `.env.example` to `.env` and fill in your configuration values:
```bash
cp .env.example .env
```
Then edit `.env` with your actual credentials and settings.

4. Start Redis server:
```bash
redis-server
```

5. Run the application:
```bash
cd src
uvicorn main:app --reload
```

## API Routes

### Web Routes (OAuth Flow)

These routes handle the OAuth authentication flow:

#### `GET /auth/{platform}`
Initiates OAuth authentication for the specified platform.
- **Platforms**: `google`, `reddit`
- **Response**: Redirects to OAuth provider for authorization

#### `GET /auth/{platform}/callback`
Handles OAuth provider callbacks after user authorization.
- **Response**: Redirects to frontend URL with session cookie set

### API Routes (Data Access)

These routes provide programmatic access to user data and AI features:

#### `GET /api/connected_platforms`
Returns list of platforms the user has authenticated with.
- **Authentication**: Required
- **Response**: `["google", "reddit"]`

#### `POST /api/prompt`
Main AI endpoint for natural language queries about YouTube channel metrics.
- **Authentication**: Required
- **Request Body**:
  ```json
  {
    "prompt": "How many subscribers do I have?"
  }
  ```
- **Response**:
  ```json
  {
    "result": "You have 1,234 subscribers on your YouTube channel."
  }
  ```

## Project Structure
```
src/
├── main.py                 # Application entry point and middleware setup
├── config/
│   ├── settings.py        # Environment configuration
│   ├── oauth_manager.py   # OAuth client management
│   └── agent.py          # Pydantic AI agent configuration
├── models/
│   ├── channel_public_stats.py   # YouTube public statistics models
│   └── channel_analytics.py      # YouTube analytics models
├── routers/
│   ├── auth.py           # OAuth authentication endpoints
│   └── api.py           # API data endpoints
├── dependencies.py       # FastAPI dependency injection
└── utils.py             # Utility functions
```



