# ChatGPT to PDF Converter 📄✨

A mobile-friendly web app to convert any public ChatGPT conversation link (`https://chatgpt.com/share/...`) or raw Markdown into a beautifully formatted, paginated, and readable PDF.

## Features
- **Android & Mobile Ready**: Clean, responsive UI designed for mobile browsers.
- **Direct Link Extraction**: Fetches public ChatGPT shared links and parses modern React Server Component streams without requiring headless browser overhead.
- **Direct Markdown Fallback**: Paste answers directly from clipboard with instant offline conversion.
- **Engineered for Reading & Revision**:
  - Paginated with page counters (`Page X / Y`)
  - Formatted user questions & assistant responses
  - Crisp code blocks with syntax styling
  - Markdown tables and blockquotes

## Local Testing
```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run local server
python -m uvicorn app:app --reload --host 0.0.0.0 --port 8000
```
Open [http://localhost:8000](http://localhost:8000) in your browser.

## Deploying to Render

### Option 1: Automatic Deploy via GitHub (Recommended)
1. Push this repository to your GitHub account:
   ```bash
   git add .
   git commit -m "Initial commit"
   gh repo create chatgpt-to-pdf --public --source=. --push
   ```
2. In your [Render Dashboard](https://dashboard.render.com), click **New +** &rarr; **Blueprint** (or **Web Service**).
3. Connect your repository. Render automatically reads `render.yaml`, installs dependencies, and deploys your service.

### Option 2: Render CLI
1. Log in to Render:
   ```bash
   render login
   ```
2. Set your workspace:
   ```bash
   render workspace set
   ```
3. Deploy Blueprint:
   ```bash
   render blueprints launch
   ```
