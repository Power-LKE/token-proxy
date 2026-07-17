# LinkPower - AI API Proxy Service

Built with FastAPI + DeepSeek. Supports user registration, balance management, multi-model access.

## Quick Start

### 1. Clone

`ash
git clone https://github.com/Power-LKE/token-proxy.git
cd token-proxy
`

### 2. Install

`ash
pip install -r requirements.txt
`

### 3. Configure

Copy .env.example to .env, fill in your DeepSeek API Key:

`ash
cp .env.example .env
`

### 4. Run locally

`ash
python main.py
`

Visit http://localhost:8000

### 5. Deploy to Render

1. Push code to GitHub
2. Go to Render Dashboard -> Manual Deploy -> Deploy latest commit

## Collaborate with VS Code Live Share

1. Both install VS Code Live Share extension
2. One clicks Live Share -> Start session -> Copy link
3. Other clicks Live Share -> Join session -> Paste link

## Project Structure

`	ext
├── main.py              # Entry point
├── config.py            # Configuration (pricing, API keys)
├── requirements.txt     # Dependencies
├── proxy/
│   ├── router.py        # API routes (register, login, chat, admin)
│   ├── auth.py          # User authentication & management
│   ├── upstream.py      # Forward requests to upstream API
│   ├── storage.py       # Data storage (Supabase / file)
│   ├── models.py        # Data models
│   └── file_handler.py  # File upload processing
└── static/
    ├── index.html       # Main page (landing + chat)
    ├── admin.html       # Admin dashboard
    ├── user.html        # User guide
    ├── dashboard.html   # User dashboard
    └── reseller.html    # Reseller management
`