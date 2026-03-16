# Localelive Frontend

The web interface for the **Localelive IoT Agentic Search Engine** — an AI-powered, location-aware search engine that recommends nearby services using real-time IoT data, map visualization, and multi-agent reasoning.

- [Research Paper (arXiv)](https://www.mdpi.com/1424-8220/25/19/5995)
- [GitHub Repository](https://github.com/SensorsConnect/IoT-Agentic-Search-Engine)

---

## Tech Stack

| Technology | Purpose |
|---|---|
| [Next.js 14](https://nextjs.org/) | React framework with App Router (file-based routing, server components) |
| [React 18](https://react.dev/) | UI library |
| [TypeScript](https://www.typescriptlang.org/) | Type-safe JavaScript |
| [Tailwind CSS](https://tailwindcss.com/) | Utility-first CSS styling |
| [Radix UI](https://www.radix-ui.com/) | Accessible, unstyled UI primitives |
| [Mapbox GL](https://www.mapbox.com/) | Interactive map rendering |
| [Clerk](https://clerk.com/) | Authentication (sign-in, sign-up, session management) |

---

## Project Structure

```
frontend/
├── app/                        # Next.js App Router (pages & API routes)
│   ├── layout.tsx              # Root layout (wraps every page with providers & header)
│   ├── page.tsx                # Landing page (hero, features, contact)
│   ├── not-found.tsx           # Custom 404 page
│   ├── chat/                   # Main explorer/chat page
│   │   ├── page.tsx            # Chat page entry point
│   │   ├── PersonaModal.tsx    # Persona selection modal
│   │   └── ...
│   ├── sign-in/                # Clerk sign-in page
│   ├── sign-up/                # Clerk sign-up page
│   └── api/chat/               # Backend-proxying API route for chat
├── components/                 # Reusable UI components
│   ├── Chat/                   # Chat interface, sidebar, message bubbles, state management
│   ├── Explorer/               # Map-based explorer layout (orchestrates map + search + results)
│   ├── Map/                    # Mapbox map integration
│   ├── PlaceCard/              # Cards that display place details (rating, distance, etc.)
│   ├── Location/               # Geolocation context (GPS position tracking)
│   ├── Header/                 # Top navigation bar
│   ├── Themes/                 # Dark/light mode toggle
│   ├── Markdown/               # Markdown renderer for AI responses
│   └── Link.tsx                # Custom link wrapper
├── hooks/                      # Custom React hooks
│   ├── useConversations.ts     # Conversation history management
│   └── useCopyToClipboard.ts   # Clipboard utility
├── lib/                        # API utilities
│   └── api.ts                  # HTTP client for backend calls
├── providers/                  # App-wide providers
│   └── ThemesProvider.tsx      # Theme context provider
├── utils/                      # Environment config
│   └── environment.ts          # Env variable accessors
├── middleware.ts                # Clerk auth middleware (protects routes)
└── public/                     # Static assets (logos, icons)
```

---

## Architecture Explained

This section explains how the frontend is organized, written for developers who may be new to Next.js or React.

### What is Next.js App Router?

Next.js uses **file-based routing**: every folder inside `app/` becomes a URL path, and the `page.tsx` file inside that folder is what the user sees.

| Folder | URL | What it renders |
|---|---|---|
| `app/` | `/` | Landing page |
| `app/chat/` | `/chat` | Main search & explore interface |
| `app/sign-in/` | `/sign-in` | Sign-in page |
| `app/sign-up/` | `/sign-up` | Sign-up page |

The `layout.tsx` file wraps every page — it sets up the HTML structure, loads fonts, and wraps the app in **providers**.

### Providers & Context

Providers are like **global variables that any component can read**. Instead of passing data down through every level of components, a provider makes data available to all components inside it. The app uses these providers:

- **ClerkProvider** — handles authentication. Any component can check if the user is signed in and get their session token.
- **ThemesProvider** — manages dark/light mode. Components read this to style themselves correctly.
- **LocationProvider** (`components/Location/`) — tracks the user's GPS coordinates. The search engine needs your location to find nearby places.
- **MapProvider** (`components/Map/`) — shares map state (center position, zoom, markers) between the search bar, results panel, and map view.
- **ChatProvider** (`components/Chat/`) — manages conversation state: message history, the current thread, and sending/receiving messages.

### Pages

- **Landing page** (`app/page.tsx`) — marketing page with feature highlights, example conversations, and a "Try Demo" button that links to `/chat`.
- **Chat / Explorer page** (`app/chat/page.tsx`) — the main interface. Combines an interactive map, a search bar, AI-generated responses, and place cards into a single explorer layout.
- **Sign-in / Sign-up** — Clerk-powered auth pages. Users must sign in before accessing `/chat`.

### How Components Compose Together

The chat page uses an **ExplorerLayout** component that orchestrates several panels:

```
ExplorerLayout
├── MapPanel          — interactive Mapbox map showing place markers
├── SearchBar         — text input where users type queries
├── AIResponsePanel   — displays the AI's markdown-formatted answer
├── PlaceCards        — cards for each recommended place (name, rating, distance)
└── ChatSidebar       — conversation history list
```

Each component reads from shared providers (ChatProvider, MapProvider, LocationProvider) so they stay in sync — when the AI returns results, the places appear on both the map and as cards simultaneously.

### Data Flow

Here's what happens when a user searches for something:

1. **User types a query** in the SearchBar (e.g., "best coffee shops nearby")
2. **SearchBar sends the query** to the backend API via `PUT /query` with the user's text, thread ID, and GPS location
3. **Backend processes the query** through its multi-agent pipeline (intent classification → IoT search → response generation)
4. **Response comes back** with a text answer and a list of recommended places (with coordinates, ratings, etc.)
5. **ChatProvider updates state** — the AI response appears in the AIResponsePanel
6. **MapProvider updates markers** — place pins appear on the map
7. **PlaceCards render** — each recommended place gets a clickable card

### Authentication

[Clerk](https://clerk.com/) handles all authentication:

- `middleware.ts` protects the `/chat` route — unauthenticated users are redirected to sign-in
- The Clerk session token is sent with API calls to the backend
- Sign-in and sign-up pages are pre-built Clerk components mounted at `/sign-in` and `/sign-up`

### Theming

The app supports dark and light mode:

- `ThemesProvider` reads the user's system preference (e.g., macOS dark mode) on first load
- Users can manually toggle via the theme switch in the header
- The preference is saved to `localStorage` so it persists across visits
- Tailwind's `dark:` variant classes handle all the styling (e.g., `bg-white dark:bg-gray-800`)

---

## Local Setup

### Prerequisites

- **Node.js 20+** and **npm**
- A running instance of the [backend](../backend/) (or access to a deployed one)

### Steps

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Create your environment file:
   ```bash
   cp .env.example .env.local
   ```

4. Fill in the required environment variables in `.env.local`:

   | Variable | Description |
   |---|---|
   | `NEXT_PUBLIC_BACKEND_URL` | Backend API URL (e.g., `http://localhost:8000`) |
   | `NEXT_PUBLIC_MAPBOX_TOKEN` | [Mapbox GL](https://account.mapbox.com/access-tokens/) access token |
   | `NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY` | [Clerk](https://dashboard.clerk.com/) publishable key |
   | `CLERK_SECRET_KEY` | Clerk secret key |

5. Start the dev server:
   ```bash
   npm run dev
   ```

6. Open [http://localhost:3000](http://localhost:3000) in your browser.

---

## Production Deployment

### Docker (standalone)

```bash
docker build -t localelive-frontend ./frontend
docker run -d -p 3000:3000 \
  -e NEXT_PUBLIC_BACKEND_URL="https://api.yourdomain.com" \
  -e NEXT_PUBLIC_MAPBOX_TOKEN="pk.xxx" \
  -e NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY="pk_xxx" \
  -e CLERK_SECRET_KEY="sk_xxx" \
  localelive-frontend
```

### Docker Compose (full stack with Traefik + TLS)

From the repository root:

```bash
docker-compose up --build
```

This starts Traefik (ports 80/443), the frontend (port 3000), and the backend (port 8000). See the root `docker-compose.yml` for configuration.

### Production Environment Variables

| Variable | Required | Description |
|---|---|---|
| `NEXT_PUBLIC_BACKEND_URL` | Yes | Backend API URL |
| `NEXT_PUBLIC_MAPBOX_TOKEN` | Yes | Mapbox access token |
| `NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY` | Yes | Clerk publishable key |
| `CLERK_SECRET_KEY` | Yes | Clerk secret key |
| `BACKEND_DOMAIN_NAME` | No | Used for Traefik routing config |

> The Next.js config uses `output: 'standalone'` mode, which produces a minimal production build that doesn't need `node_modules` at runtime — ideal for Docker containers.

---

## Available Scripts

| Command | Description |
|---|---|
| `npm run dev` | Start development server with hot reload |
| `npm run build` | Create optimized production build |
| `npm run start` | Start production server (run `build` first) |
| `npm run lint` | Run ESLint to check for code issues |
| `npm run lint:fix` | Auto-fix ESLint issues |
| `npm run format` | Format code with Prettier |
| `npm run format:check` | Check if code is properly formatted |
