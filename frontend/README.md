# TaskFlow Frontend — Vue.js 3 + PrimeVue

Frontend for TaskFlow task management application.

## Tech Stack

- **Vue.js 3** (Composition API `<script setup>`)
- **PrimeVue 4** - Professional UI component library
- **Pinia** - State management
- **Vue Router** - Client-side routing
- **Vite** - Lightning-fast build tool
- **Axios** - HTTP client with auth interceptors

## Setup & Running

See main [README.md](../README.md) for full setup instructions.

Quick start:
```bash
npm install
npm run dev
```

Frontend will be available at `http://localhost:5173`

## Project Structure

```
src/
├── main.js                 # PrimeVue config (Aura theme)
├── App.vue                 # Root component with layout
├── api/
│   └── axios.js            # HTTP client + auth interceptor
├── router/
│   └── index.js            # Route definitions
├── stores/
│   ├── auth.js             # Auth state & token management
│   └── tasks.js            # Task + AI operations
├── components/             # Reusable UI components
│   ├── AIBreakdownDialog.vue
│   ├── AIEnhanceDescriptionDialog.vue
│   ├── AIAnalyzePriorityDialog.vue
│   └── AIGenerateSuggestionsDialog.vue
└── views/                  # Page components
    ├── LoginView.vue       # Authentication form
    ├── TasksView.vue       # Task list + filters + AI suggestions
    └── TaskDetailView.vue  # Detail view + all AI features
```

## Key Components

### Authentication (stores/auth.js)
- Login/logout state management
- Token storage in localStorage
- Token refresh on 401 responses
- Routes protected with meta guards

### Task Management (stores/tasks.js)
Handles both task CRUD and AI operations.

## PrimeVue Usage

Theme: **Aura** (configured explicitly in main.js).

Components used:
- Dialog - AI features & editing
- DataTable - Task list with filtering & pagination
- Dropdown - Status selection
- Slider - Number selection (subtask count)
- Button - Actions
- Tag - Status badges
- Message - Error/info feedback
- Toast - Success notifications

## Routing

Protected routes require authentication. Unauthenticated users redirected to `/login`.

## Error Handling

- 401 Unauthorized → Redirect to login
- 4xx Client errors → User-friendly messages
- 5xx Server errors → "System error, try again later"

## Build for Production

```bash
npm run build
```

See main [README.md](../README.md) for complete documentation.
