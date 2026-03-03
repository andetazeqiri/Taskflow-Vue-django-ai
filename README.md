# TaskFlow — AI-Powered Personal Task Management

A full-stack web application for personal task management with AI-powered assistance. Built with Vue.js 3 + Django REST Framework.

## Quick Start

### Prerequisites
- Python 3.9+
- Node.js 16+
- pip and npm

### Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env
# Edit .env and add your OpenRouter API key

# Apply migrations
python manage.py migrate

# Create a superuser (optional, for admin panel)
python manage.py createsuperuser

# Run development server
python manage.py runserver
```

The backend will be available at `http://localhost:8000`

### Frontend Setup

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Create .env file 
# Update API endpoint if running on different port

# Run development server
npm run dev
```

The frontend will be available at `http://localhost:5173`

### Running Tests

```bash
# Backend tests (authentication & data isolation)
cd backend
python manage.py test tasks.tests




## Environment Variables

### Backend (`/backend/.env`)

Create a `.env` file in the backend directory using `.env.example` as template:

```env
# Django
SECRET_KEY=your-secret-key-here
DEBUG=True  # Set to False in production

# OpenRouter API (Required for AI features)
OPENROUTER_API_KEY=your-openrouter-api-key  # Get from https://openrouter.ai/keys
OPENROUTER_MODEL=openai/gpt-3.5-turbo  # Model to use (optional)

# Database
DATABASE_URL=sqlite:///db.sqlite3  # Optional SQLite path

# CORS (if frontend runs on different port)
CORS_ALLOWED_ORIGINS=http://localhost:5173,http://localhost:8000
```

**Important**: Never commit `.env` to version control. It's already in `.gitignore`.

---

## Architecture & Design Decisions

### Why These 4 AI Features?

TaskFlow implements **four distinct AI-powered features** to demonstrate comprehensive LLM integration while providing genuine value to task management:

#### 1. **Break Down Tasks** (Task Detail View)
- **Reason**: Breaking tasks into actionable subtasks improves execution clarity.
- **UX**: User clicks "Break Down Task" → AI generates 3-10 step-by-step subtasks with optional guidance notes
- **Implementation**: `POST /api/tasks/{id}/ai-breakdown/` returns array of subtasks

#### 2. **Enhance Task Description** (Task Detail View)
- **Reason**: Users use to write vague descriptions for this AI is implemented topolish and improve context for future review.
- **UX**: Users can enhance descriptions and then manually update task with the improved version
- **Implementation**: `POST /api/ai/enhance-description/` — takes task title and the  description, returns improved version

#### 3. **Analyze Task Priority** (Task Detail View)
- **Reason**: The priority is subjective so the use of an AI analysis provides objective reasoning based on title, description, and due date.
- **UX**: Shows AI-recommended priority level (Low/Medium/High/Critical) with structured reasoning
- **Implementation**: `POST /api/ai/analyze-priority/` — takes task context and returns recommended priority and the reasoning

#### 4. **Generate Task Suggestions** (Main Tasks View)
- **Reason**: based on the project context, AI suggests concrete tasks to help users get started.
- **UX**: Hero section has "Generate Suggestions" button → Dialog captures project context → Shows list of suggestions with "Add as Task" buttons
- **Implementation**: `POST /api/ai/generate-suggestions/` — returns array of suggestions that can be instantly created as tasks

**Why frontend-only callout of AI endpoints?** All four features are backend-exclusive (API key never exposed). Frontend calls are authenticated and rate-limited by Django permissions.

### API Design Philosophy

- **RESTful**: Task CRUD follows standard REST patterns
- **Composable**: AI endpoints are independent; frontend can mix/match features
- **Stateless**: Each AI call is independent; no session state needed
- **Authenticated**: All endpoints require JWT token; users see only their own data

### Frontend Architecture

- **Stores (Pinia)**: `tasks` store handles all task and the AI operations
- **Composition API**: Components use `<script setup>` for cleaner reactive code
- **PrimeVue Components**: Consistent use of:
  - `Dialog` for AI feature inputs/outputs
  - `DataTable` for task list
  - `Tag` for status visualization
  - `Button`, `Dropdown`, `Slider`, `Calendar` for forms
  - `Toast` & `Message` for feedback
  - `ProgressSpinner` for loading states

### Authentication & Security

- **JWT tokens**: Token lifecycle managed in `auth.js` store
- **Axios interceptor**: Auto-attaches token to all requests
- **Token refresh**: Frontend handles 401 responses gracefully
- **Data isolation**: Backend queries filtered by `request.user`; users **cannot** access other users' tasks

### Backend Tests

Located in `backend/tasks/tests.py`:

1. **UnauthorizedAccessTests**: Verify all endpoints return 401 without valid token
2. **DataIsolationTests**: Verify User A cannot see/modify User B's tasks

Run with: `python manage.py test tasks.tests`

---

## Project Structure

```
.
├── backend/
│   ├── config/               # Django project settings
│   ├── tasks/                # Task app (models, views, serializers)
│   │   ├── ai_service.py     # OpenRouter integration
│   │   ├── models.py         # Task model
│   │   ├── views.py          # REST API endpoints + AI actions
│   │   └── tests.py          # Authentication & isolation tests
│   ├── users/                # User app (authentication)
│   ├── manage.py
│   ├── requirements.txt
│   ├── .env.example          # Template for environment variables
│   └── db.sqlite3            # SQLite database (not in git)
│
├── frontend/
│   ├── src/
│   │   ├── main.js           # App entry, PrimeVue config
│   │   ├── App.vue           # Root component
│   │   ├── api/
│   │   │   └── axios.js      # API client with auth interceptor
│   │   ├── router/
│   │   │   └── index.js      # Route definitions
│   │   ├── stores/
│   │   │   ├── auth.js       # Authentication state
│   │   │   └── tasks.js      # Task + AI operations
│   │   ├── components/       # Reusable components
│   │   │   ├── AIBreakdownDialog.vue
│   │   │   ├── AIEnhanceDescriptionDialog.vue
│   │   │   ├── AIAnalyzePriorityDialog.vue
│   │   │   └── AIGenerateSuggestionsDialog.vue
│   │   └── views/            # Page components
│   │       ├── LoginView.vue
│   │       ├── TasksView.vue (list + filtering + suggestions)
│   │       └── TaskDetailView.vue (detail + all AI features)
│   └── package.json
│
└── README.md (this file)
```

---

## API Endpoints

All endpoints require `Authorization: Bearer <token>` header.

### Task Management

| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/api/tasks/` | List tasks (with filters/search) |
| POST | `/api/tasks/` | Create task |
| GET | `/api/tasks/{id}/` | Retrieve single task |
| PATCH | `/api/tasks/{id}/` | Update task |
| DELETE | `/api/tasks/{id}/` | Delete task |

**Query params** (on GET `/api/tasks/`):
- `search=query` - Search title/description
- `status=pending|in_progress|completed|cancelled` - Filter by status
- `ordering=-created_at` - Sort by field
- `limit=10&offset=0` - Pagination

### AI Features

| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | `/api/tasks/{id}/ai-breakdown/` | Break down a task |
| POST | `/api/ai/generate-suggestions/` | Generate task ideas |
| POST | `/api/ai/enhance-description/` | Enhance description |
| POST | `/api/ai/analyze-priority/` | Analyze priority |

### Authentication

| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | `/api/auth/login/` | Get JWT token |
| POST | `/api/auth/refresh/` | Refresh expired token |
| POST | `/api/auth/register/` | Create new user (if enabled) |

---


## Known Limitations & Future Improvements

### What Would Be Done With More Time

1. **Frontend Tests**
   - Unit tests for Pinia stores (task operations, auth state)
   - Component tests for dialogs and forms
   - E2E tests with Cypress/Playwright
   - Current: No automated frontend tests

2. **Advanced Features**
   - Subtask management (persist AI-generated subtasks as child tasks)
   - Recurring tasks
   - Task categories/labels
   - Kanban board view (drag-drop) instead of table
   - Task templates
   - Activity history/audit log

3. **Backend Improvements**
   - Rate limiting on AI endpoints
   - Caching of suggestions (avoid duplicate API calls)
   - Logging/monitoring of AI feature usage
   - Error retry logic for OpenRouter failures
   - Admin panel for managing AI quotas

4. **Deployment & DevOps**
   - Docker setup for reproducible environment
   - GitHub Actions CI/CD pipeline
   - Production-ready database (PostgreSQL)
   - Static file serving (WhiteNoise)
   - HTTPS enforcement
   - Sentry for error tracking

5. **UX Polish**
   - Dark mode toggle
   - Undo/redo functionality
   - Bulk operations (multi-select tasks)
   - Drag-drop file upload for descriptions

### Current Limitations

- **Database**: SQLite suitable for demo; PostgreSQL recommended for production
- **AI Model**: Free tier uses openai/gpt-3.5-turbo
- **Frontend Tests**: UI works correctly but no test suite but only manual QA was performed
- **Scaling**: No caching for AI results; each call hits OpenRouter
- **Persistence**: AI-generated subtasks not saved to database


---

## Troubleshooting

### Common Issues

**"OpenRouter API key not configured"**
- Ensure `.env` file exists in `/backend` directory
- Verify `OPENROUTER_API_KEY` is set (check `echo $OPENROUTER_API_KEY`)
- Restart Django dev server: `python manage.py runserver`

**"Invalid API key" error**
- Go to https://openrouter.ai/keys and verify key is correct
- Check for extra spaces or typos in `.env`
- Test key with `curl` directly:
  ```bash
  curl https://openrouter.ai/api/v1/models \
    -H "Authorization: Bearer YOUR_KEY"
  ```

**"Rate limit exceeded"**
- OpenRouter free tier has request limits
- Wait a few minutes before retrying
- Consider upgrading plan at https://openrouter.ai

**Frontend can't reach backend**
- Verify backend running: `http://localhost:8000/api/tasks/` should return 401 (not connection error)
- Check `CORS_ALLOWED_ORIGINS` in backend `.env`

---

## Deployment Notes

### Required Environment Variables for Production

```env
# Django
SECRET_KEY=<generate-with-django-secret-key-generator>
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

# Database (switch to PostgreSQL)
DATABASE_URL=postgresql://user:pass@localhost/dbname

# OpenRouter
OPENROUTER_API_KEY=<your-api-key>

# CORS
CORS_ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
```





