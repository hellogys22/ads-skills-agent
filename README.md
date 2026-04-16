# Digital Marketing Agent System

An AI-powered digital marketing automation platform that orchestrates multiple intelligent agents to manage social media content, advertising campaigns, affiliate products, and performance analytics — all from a single dashboard.

---

## Overview

| Feature | Description |
|---|---|
| **AI Content Generation** | Claude-powered copy, captions, and creative briefs tailored per platform |
| **Campaign Management** | Create, optimize, and track ad campaigns across Instagram, Facebook, and YouTube |
| **Social Media Automation** | Schedule posts, manage calendars, and publish via platform APIs |
| **Analytics Dashboard** | Real-time performance metrics, engagement stats, and reach reports |
| **Affiliate Product Tracking** | Add, promote, and monitor affiliate product performance |
| **Background Job Queue** | Celery + Redis for async tasks, scheduling, and webhooks |
| **Multi-Agent Architecture** | Specialized agents for strategy, content, ads, analytics, and Instagram |

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Frontend (Next.js 14)                 │
│         Dashboard · Campaigns · Analytics · Calendar    │
└───────────────────────┬─────────────────────────────────┘
                        │ HTTP / WebSocket
┌───────────────────────▼─────────────────────────────────┐
│                  Backend (FastAPI)                       │
│  /api/auth  /api/campaigns  /api/content  /api/analytics│
│  /api/products  /api/webhooks                           │
└──────┬─────────────────┬──────────────────┬─────────────┘
       │                 │                  │
┌──────▼──────┐  ┌───────▼───────┐  ┌──────▼──────┐
│  Agent Layer │  │  Job Queue    │  │  Data Layer  │
│  Coordinator │  │  Celery       │  │  MongoDB     │
│  Strategy    │  │  APScheduler  │  │  Supabase    │
│  Content     │  │  Redis        │  │              │
│  Ad Manager  │  └───────────────┘  └──────────────┘
│  Analytics   │
│  Instagram   │
└─────────────┘
       │
┌──────▼──────────────────────────────────────────────────┐
│              External APIs                              │
│  Anthropic Claude · Instagram Graph · Facebook Marketing│
│  YouTube Data API · Google Ads                          │
└─────────────────────────────────────────────────────────┘
```

---

## Quick Start

### Prerequisites

- Docker & Docker Compose **or** Python 3.11+ and Node.js 20+
- MongoDB Atlas account (free tier works)
- Supabase project
- Redis instance (local or Redis Cloud)

### Option A — Docker Compose (recommended)

```bash
# 1. Clone the repository
git clone https://github.com/your-org/ads-skills-agent.git
cd ads-skills-agent

# 2. Copy and fill in environment variables
cp backend/.env.example backend/.env
# Edit backend/.env with your credentials

# 3. Start all services
docker compose up --build

# Frontend → http://localhost:3000
# Backend  → http://localhost:8000
# API docs → http://localhost:8000/docs
```

### Option B — Manual Setup

```bash
# ── Backend ──────────────────────────────────────────────
cd backend
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env               # fill in your values
uvicorn main:app --reload --port 8000

# ── Celery worker (separate terminal) ───────────────────
cd backend
source .venv/bin/activate
celery -A jobs.tasks worker --loglevel=info

# ── Frontend (separate terminal) ─────────────────────────
cd frontend
npm install
cp .env.example .env.local         # fill in NEXT_PUBLIC_API_URL
npm run dev
```

---

## Environment Variables

### Backend (`backend/.env`)

| Variable | Description | Example |
|---|---|---|
| `ANTHROPIC_API_KEY` | Claude LLM API key | `sk-ant-...` |
| `MONGODB_URI` | MongoDB Atlas connection string | `mongodb+srv://...` |
| `SUPABASE_URL` | Supabase project URL | `https://xyz.supabase.co` |
| `SUPABASE_KEY` | Supabase service role key | `eyJ...` |
| `INSTAGRAM_APP_ID` | Meta app ID for Instagram | `123456789` |
| `INSTAGRAM_APP_SECRET` | Meta app secret | `abc123...` |
| `INSTAGRAM_ACCESS_TOKEN` | Long-lived Instagram access token | `IGQVJ...` |
| `FACEBOOK_APP_ID` | Facebook app ID | `123456789` |
| `FACEBOOK_APP_SECRET` | Facebook app secret | `abc123...` |
| `FACEBOOK_PAGE_ID` | Facebook Page ID to manage | `123456789` |
| `FACEBOOK_PAGE_ACCESS_TOKEN` | Facebook Page access token | `EAA...` |
| `YOUTUBE_API_KEY` | YouTube Data API v3 key | `AIzaSy...` |
| `YOUTUBE_CLIENT_ID` | Google OAuth client ID | `xxx.apps.googleusercontent.com` |
| `YOUTUBE_CLIENT_SECRET` | Google OAuth client secret | `GOCSPX-...` |
| `REDIS_URL` | Redis connection URL | `redis://localhost:6379/0` |
| `CELERY_BROKER_URL` | Celery broker URL | `redis://localhost:6379/1` |
| `JWT_SECRET_KEY` | Secret for JWT signing (≥32 chars) | `your-random-secret` |
| `API_BASE_URL` | Public URL of the backend | `https://api.yourdomain.com` |
| `FRONTEND_URL` | Public URL of the frontend | `https://yourdomain.com` |
| `ENVIRONMENT` | Runtime environment | `development` / `production` |
| `LOG_LEVEL` | Logging verbosity | `INFO` / `DEBUG` |

### Frontend (`frontend/.env.local`)

| Variable | Description | Example |
|---|---|---|
| `NEXT_PUBLIC_API_URL` | Backend API base URL | `http://localhost:8000` |

---

## API Documentation

Interactive docs available at `http://localhost:8000/docs` (Swagger UI) and `/redoc`.

### Auth — `/api/auth`

| Method | Path | Description |
|---|---|---|
| `POST` | `/api/auth/connect-instagram` | Start Instagram OAuth flow |
| `GET` | `/api/auth/callback/instagram` | Instagram OAuth callback |
| `POST` | `/api/auth/connect-facebook` | Start Facebook OAuth flow |
| `GET` | `/api/auth/callback/facebook` | Facebook OAuth callback |
| `POST` | `/api/auth/connect-youtube` | Start YouTube OAuth flow |
| `GET` | `/api/auth/callback/youtube` | YouTube OAuth callback |
| `POST` | `/api/auth/refresh/{platform}` | Refresh access token for platform |
| `DELETE` | `/api/auth/disconnect/{platform}` | Disconnect a social platform |

### Campaigns — `/api/campaigns`

| Method | Path | Description |
|---|---|---|
| `POST` | `/api/campaigns/create` | Create a new ad campaign |
| `GET` | `/api/campaigns/list` | List all campaigns |
| `GET` | `/api/campaigns/status/{campaign_id}` | Get campaign status |
| `POST` | `/api/campaigns/optimize/{campaign_id}` | Run AI optimization on campaign |
| `PUT` | `/api/campaigns/update/{campaign_id}` | Update campaign settings |
| `DELETE` | `/api/campaigns/cancel/{campaign_id}` | Cancel a campaign |

### Content — `/api/content`

| Method | Path | Description |
|---|---|---|
| `POST` | `/api/content/generate` | AI-generate social media content |
| `POST` | `/api/content/schedule` | Schedule a post for publishing |
| `GET` | `/api/content/library` | Paginated content library |
| `GET` | `/api/content/calendar` | Content calendar view |
| `PUT` | `/api/content/update/{post_id}` | Update a scheduled post |
| `DELETE` | `/api/content/delete/{post_id}` | Delete a post |

### Analytics — `/api/analytics`

| Method | Path | Description |
|---|---|---|
| `GET` | `/api/analytics/dashboard` | Aggregated dashboard metrics |
| `GET` | `/api/analytics/performance` | Campaign performance data |
| `GET` | `/api/analytics/engagement` | Engagement metrics by platform |
| `GET` | `/api/analytics/reach` | Reach and impression data |
| `POST` | `/api/analytics/export` | Export analytics report (PDF) |

### Products — `/api/products`

| Method | Path | Description |
|---|---|---|
| `GET` | `/api/products/list` | List affiliate products |
| `POST` | `/api/products/add` | Add an affiliate product |
| `PUT` | `/api/products/update/{product_id}` | Update product details |
| `DELETE` | `/api/products/remove/{product_id}` | Remove a product |
| `GET` | `/api/products/performance/{product_id}` | Product performance stats |
| `POST` | `/api/products/promote/{product_id}` | Generate promotional content |

### Webhooks — `/api/webhooks`

| Method | Path | Description |
|---|---|---|
| `GET` | `/api/webhooks/instagram` | Instagram webhook verification |
| `POST` | `/api/webhooks/instagram` | Receive Instagram events |
| `GET` | `/api/webhooks/facebook` | Facebook webhook verification |
| `POST` | `/api/webhooks/facebook` | Receive Facebook events |
| `GET` | `/api/webhooks/verify/{platform}` | Verify webhook subscription |

---

## Agent Architecture

The system uses a multi-agent design where a **Coordinator** delegates tasks to specialized sub-agents:

```
CoordinatorAgent
├── StrategyAgent      — Analyzes goals, generates marketing strategy
├── ContentCreatorAgent — Writes captions, ad copy, and creative briefs
├── AdManagerAgent     — Creates and optimizes ad campaigns via platform APIs
├── AnalyticsAgent     — Pulls metrics, identifies trends, suggests actions
└── InstagramManagerAgent — Handles Instagram-specific publishing and DMs
```

Each agent is powered by **Anthropic Claude** and exposes a set of skills (defined in `skills/`) that can be composed into automated workflows.

| Agent | File | Responsibilities |
|---|---|---|
| Coordinator | `agents/coordinator.py` | Task routing, workflow orchestration |
| Strategy | `agents/strategy_agent.py` | Campaign planning, audience targeting |
| Content Creator | `agents/content_creator.py` | AI copywriting, caption generation |
| Ad Manager | `agents/ad_manager.py` | Campaign CRUD, budget allocation, A/B tests |
| Analytics | `agents/analytics_agent.py` | KPI tracking, report generation |
| Instagram Manager | `agents/instagram_manager.py` | Post scheduling, story management |

---

## Deployment

### Frontend → Vercel

1. Import your GitHub repository at [vercel.com/new](https://vercel.com/new)
2. Set the **Root Directory** to `frontend`
3. Add environment variable: `NEXT_PUBLIC_API_URL` = your backend URL
4. Deploy — Vercel auto-deploys on every push to `main`

For CI/CD via GitHub Actions, set these repository secrets:

```
VERCEL_TOKEN
VERCEL_ORG_ID
VERCEL_PROJECT_ID
NEXT_PUBLIC_API_URL
```

### Backend → Railway

1. Create a new project at [railway.app](https://railway.app)
2. Connect your GitHub repository
3. Set the **Start Command** to `uvicorn main:app --host 0.0.0.0 --port $PORT`
4. Set root directory to `backend/`
5. Add all environment variables from `backend/.env.example`
6. Copy the deploy hook URL into `RAILWAY_DEPLOY_HOOK` GitHub secret

### Backend → Render

1. Create a **Web Service** at [render.com](https://render.com)
2. Connect your GitHub repository
3. Set **Build Command**: `pip install -r backend/requirements.txt`
4. Set **Start Command**: `cd backend && uvicorn main:app --host 0.0.0.0 --port $PORT`
5. Add environment variables
6. Copy the deploy hook URL into `RENDER_DEPLOY_HOOK` GitHub secret

### Database → MongoDB Atlas

1. Create a free cluster at [mongodb.com/atlas](https://www.mongodb.com/atlas)
2. Create a database user and whitelist `0.0.0.0/0` for cloud access
3. Copy the connection string into `MONGODB_URI`

### Auth / Relational → Supabase

1. Create a project at [supabase.com](https://supabase.com)
2. Copy **Project URL** → `SUPABASE_URL`
3. Copy **service_role** key → `SUPABASE_KEY`

### Task Queue → Redis Cloud

1. Create a free database at [redis.io/cloud](https://redis.io/cloud)
2. Copy the connection URL into both `REDIS_URL` and `CELERY_BROKER_URL`

---

## Social Media Setup

### Instagram Graph API

1. Go to [developers.facebook.com](https://developers.facebook.com) and create an app (type: **Business**)
2. Add the **Instagram Graph API** product
3. Connect a Facebook Page linked to your Instagram Business/Creator account
4. Generate a long-lived **Page Access Token**
5. Set `INSTAGRAM_APP_ID`, `INSTAGRAM_APP_SECRET`, `INSTAGRAM_ACCESS_TOKEN`
6. Register your webhook endpoint: `POST /api/webhooks/instagram`

### Facebook Marketing API

1. In the same Meta app, add the **Marketing API** product
2. Request `ads_management` and `pages_manage_posts` permissions
3. Generate a **Page Access Token** with the required scopes
4. Set `FACEBOOK_APP_ID`, `FACEBOOK_APP_SECRET`, `FACEBOOK_PAGE_ID`, `FACEBOOK_PAGE_ACCESS_TOKEN`

### YouTube Data API & OAuth

1. Enable **YouTube Data API v3** in [Google Cloud Console](https://console.cloud.google.com)
2. Create an **API Key** → `YOUTUBE_API_KEY`
3. Create **OAuth 2.0 Client ID** (Web Application)
4. Add `http://localhost:8000/api/auth/callback/youtube` as an authorized redirect URI
5. Set `YOUTUBE_CLIENT_ID` and `YOUTUBE_CLIENT_SECRET`

---

## Usage Guide

### Dashboard Overview

The main dashboard (`/`) shows:
- **KPI cards** — total reach, impressions, clicks, and conversions
- **Performance chart** — campaign performance over time
- **Engagement breakdown** — likes, comments, shares by platform
- **Recent activity feed** — latest posts and campaign updates

### Content Generation Workflow

1. Navigate to **Content → Generate**
2. Select target platform (Instagram, Facebook, YouTube)
3. Enter your product/topic and tone preferences
4. The AI agent produces captions, hashtags, and a creative brief
5. Review and edit the output
6. Schedule for publishing or save to your Content Library

### Campaign Creation

1. Navigate to **Campaigns → New Campaign**
2. Define objective (awareness, engagement, conversions), budget, and date range
3. Select target audience parameters
4. The **Ad Manager Agent** creates the campaign via the platform API
5. Monitor performance in **Campaigns → Status**
6. Use **Optimize** to let the AI agent adjust targeting and bids automatically

### Analytics Interpretation

- **Performance tab** — CTR, CPC, ROAS per campaign; compare against previous period
- **Engagement tab** — post-level engagement rates; identify top-performing content
- **Reach tab** — unique reach and frequency metrics
- **Export** — generate a branded PDF report via the Analytics Agent

---

## Development

```bash
# Run backend tests
cd backend && python -m pytest tests/ -v

# Lint frontend
cd frontend && npm run lint

# Type-check frontend
cd frontend && npx tsc --noEmit
```

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feat/your-feature`
3. Commit your changes: `git commit -m "feat: add your feature"`
4. Push and open a Pull Request

## License

MIT
