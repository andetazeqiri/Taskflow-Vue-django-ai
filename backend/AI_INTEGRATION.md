# OpenRouter AI Integration

This document describes the AI-powered features integrated into the Taskflow backend using OpenRouter.

## Overview

Taskflow now includes AI-powered features to help users manage their tasks more effectively:

1. **Generate Task Suggestions** - Generate task ideas based on a project or context
2. **Enhance Task Descriptions** - Improve task descriptions with AI assistance
3. **Analyze Task Priority** - Get AI-powered priority recommendations with reasoning
4. **Break Down Tasks** - Break complex tasks into smaller, actionable subtasks

## Setup

### 1. Get an OpenRouter API Key

1. Visit [https://openrouter.ai/](https://openrouter.ai/)
2. Sign up or log in to your account
3. Navigate to [API Keys](https://openrouter.ai/keys)
4. Create a new API key

### 2. Configure Environment Variables

Create a `.env` file in the backend directory (or update your existing one):

```bash
# Copy the example file
cp .env.example .env
```

Then edit `.env` and add your OpenRouter API key:

```env
OPENROUTER_API_KEY=your-actual-api-key-here
OPENROUTER_MODEL=openai/gpt-3.5-turbo  # Optional: change to different model
```

### 3. Install Dependencies

The `requests` library is required (should already be installed):

```bash
pip install requests
```

## API Endpoints

All AI endpoints require authentication (Bearer token in Authorization header).

### 1. Generate Task Suggestions

Generate AI-powered task suggestions based on a project description or context.

**Endpoint:** `POST /api/ai/generate-suggestions/`

**Request Body:**
```json
{
  "context": "Build a mobile app for task management",
  "num_suggestions": 5  // Optional, default 3, max 10
}
```

**Response:**
```json
{
  "suggestions": [
    "Design user interface mockups",
    "Set up development environment",
    "Implement user authentication",
    "Create task CRUD operations",
    "Add push notifications"
  ]
}
```

**Example cURL:**
```bash
curl -X POST http://localhost:8000/api/ai/generate-suggestions/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "context": "Build a mobile app for task management",
    "num_suggestions": 5
  }'
```

### 2. Enhance Task Description

Enhance a task description with more details and clarity using AI.

**Endpoint:** `POST /api/ai/enhance-description/`

**Request Body:**
```json
{
  "title": "Implement user authentication",
  "description": "Add login functionality"  // Optional
}
```

**Response:**
```json
{
  "enhanced_description": "Implement a secure user authentication system with login and registration functionality. Include password hashing, session management, and JWT token generation. Add email verification and password reset features for enhanced security."
}
```

**Example cURL:**
```bash
curl -X POST http://localhost:8000/api/ai/enhance-description/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Implement user authentication",
    "description": "Add login functionality"
  }'
```

### 3. Analyze Task Priority

Get AI-powered priority recommendations with reasoning.

**Endpoint:** `POST /api/ai/analyze-priority/`

**Request Body:**
```json
{
  "title": "Fix production server crash",
  "description": "Server is down and users cannot access the app",
  "due_date": "2024-03-15"  
}
```

**Response:**
```json
{
  "priority": "high",
  "reasoning": "This task requires immediate attention as it directly impacts user access and business operations. A production server crash is critical and should be resolved as a top priority."
}
```

**Example cURL:**
```bash
curl -X POST http://localhost:8000/api/ai/analyze-priority/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Fix production server crash",
    "description": "Server is down and users cannot access the app"
  }'
```

### 4. Break Down Task into Subtasks

Break down a complex task into smaller, actionable subtasks using AI.

**Endpoint:** `POST /api/tasks/{id}/ai-breakdown/`

**Request Body (optional):**
```json
{
  "num_steps": 5  // Number of subtasks to generate (1-10, default: 5)
}
```

**Response:**
```json
{
  "subtasks": [
    "Design user interface mockups",
    "Set up authentication system",
    "Implement task CRUD operations",
    "Add real-time updates",
    "Write unit tests"
  ],
  "notes": "Focus on MVP features first. Consider using existing UI libraries to speed up development."
}
```

**Example cURL:**
```bash
curl -X POST http://localhost:8000/api/tasks/123/ai-breakdown/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "num_steps": 5
  }'
```

**Features:**
- Uses the task's existing title and description
- Generates actionable, specific subtasks
- Provides optional notes with helpful context
- Validates user ownership (users can only breakdown their own tasks)
- Returns 404 if task doesn't exist or doesn't belong to the user

## Error Handling

All AI endpoints return appropriate error responses:

### 400 Bad Request
Missing or invalid input parameters:
```json
{
  "error": "Title is required"
}
```

### 401 Unauthorized
Missing or invalid authentication token:
```json
{
  "detail": "Authentication credentials were not provided."
}
```

### 503 Service Unavailable
OpenRouter API errors (API key issues, rate limits, service down):
```json
{
  "error": "Invalid API key"
}
```

### 500 Internal Server Error
Unexpected errors:
```json
{
  "error": "An unexpected error occurred"
}
```

## Supported Models

You can configure different AI models via the `OPENROUTER_MODEL` environment variable. Some popular options:

- `openai/gpt-3.5-turbo` (default, fast and cost-effective)
- `openai/gpt-4` (more powerful, higher cost)
- `anthropic/claude-2` (good for detailed analysis)
- `meta-llama/llama-2-70b-chat` (open source alternative)

See the full list at [https://openrouter.ai/models](https://openrouter.ai/models)

## Implementation Details

### AIService Class

Located in `tasks/ai_service.py`, the `AIService` class handles all communication with OpenRouter:

- **Error Handling**: Comprehensive error handling with custom `OpenRouterError` exception
- **Timeout**: 30-second timeout for API requests
- **Logging**: All errors are logged for debugging
- **Singleton Pattern**: Single instance (`ai_service`) used throughout the application

### Security

- API key is loaded from environment variables (never hardcoded)
- All endpoints require authentication
- User context is maintained (tasks are user-specific)
- Request/response validation


## Testing

You can test the AI integration without setting up the frontend:

```python
# In Django shell
from tasks.ai_service import ai_service

# Generate suggestions
suggestions = ai_service.generate_task_suggestions(
    context="Build a blog platform",
    num_suggestions=3
)
print(suggestions)

# Enhance description
enhanced = ai_service.enhance_task_description(
    title="Write blog post",
    description="Technical article"
)
print(enhanced)

# Analyze priority
analysis = ai_service.analyze_task_priority(
    title="Fix critical bug",
    description="Users cannot login"
)
print(analysis)
```

## Troubleshooting

### "OpenRouter API key not configured"
- Ensure `.env` file exists in backend directory
- Check that `OPENROUTER_API_KEY` is set in `.env`
- Restart the Django development server

### "Invalid API key"
- Verify your API key at https://openrouter.ai/keys
- Ensure the key is correctly copied (no extra spaces)

### "Rate limit exceeded"
- OpenRouter has rate limits based on your plan
- Wait a few minutes before trying again
- Consider upgrading your OpenRouter plan

### API timeouts
- OpenRouter can be slow during high traffic
- The service has a 30-second timeout
- Try again or consider adjusting the timeout in `ai_service.py`


