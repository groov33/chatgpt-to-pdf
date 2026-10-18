import os
import re
import urllib.parse
from typing import Optional
from fastapi import FastAPI, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, Response
import markdown
import requests
import weasyprint

import chatpeek_lib

app = FastAPI(title="ChatGPT to PDF", description="Convert ChatGPT shared links or Markdown to PDF")

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
  <title>ChatGPT to PDF Converter</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap" rel="stylesheet">
  <style>
    :root {
      --primary: #10a37f;
      --primary-hover: #0e8c6d;
      --bg: #f8fafc;
      --card-bg: #ffffff;
      --text-main: #0f172a;
      --text-muted: #64748b;
      --border: #e2e8f0;
    }
    * {
      box-sizing: border-box;
      margin: 0;
      padding: 0;
    }
    body {
      font-family: 'Plus Jakarta Sans', system-ui, -apple-system, sans-serif;
      background: var(--bg);
      color: var(--text-main);
      min-height: 100vh;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      padding: 16px;
    }
    .container {
      width: 100%;
      max-width: 520px;
      background: var(--card-bg);
      border-radius: 16px;
      padding: 28px 24px;
      box-shadow: 0 10px 25px -5px rgba(15, 23, 42, 0.08), 0 8px 10px -6px rgba(15, 23, 42, 0.04);
      border: 1px solid var(--border);
    }
    .header {
      text-align: center;
      margin-bottom: 24px;
    }
    .badge {
      display: inline-flex;
      align-items: center;
      gap: 6px;
      background: #ecfdf5;
      color: #059669;
      font-size: 12px;
      font-weight: 600;
      padding: 4px 10px;
      border-radius: 999px;
      margin-bottom: 12px;
    }
    h1 {
      font-size: 24px;
      font-weight: 700;
      color: var(--text-main);
      margin-bottom: 6px;
    }
    p.subtitle {
      font-size: 14px;
      color: var(--text-muted);
    }
    .tabs {
      display: flex;
      background: #f1f5f9;
      padding: 4px;
      border-radius: 10px;
      margin-bottom: 20px;
      gap: 4px;
    }
    .tab-btn {
      flex: 1;
      padding: 10px;
      border: none;
      background: transparent;
      border-radius: 8px;
      font-size: 13px;
      font-weight: 600;
      color: var(--text-muted);
      cursor: pointer;
      transition: all 0.2s ease;
    }
    .tab-btn.active {
      background: white;
      color: var(--text-main);
      box-shadow: 0 1px 3px rgba(0,0,0,0.08);
    }
    .tab-content {
      display: none;
    }
    .tab-content.active {
      display: block;
    }
    label {
      display: block;
      font-size: 13px;
      font-weight: 600;
      color: #334155;
      margin-bottom: 6px;
    }
    input[type="url"], textarea {
      width: 100%;
      padding: 12px 14px;
      font-size: 14px;
      border: 1.5px solid var(--border);
      border-radius: 10px;
      background: #fff;
      color: var(--text-main);
      transition: border-color 0.2s;
      outline: none;
      font-family: inherit;
    }
    input[type="url"]:focus, textarea:focus {
      border-color: var(--primary);
    }
    textarea {
      min-height: 140px;
      resize: vertical;
    }
    .btn-submit {
      width: 100%;
      margin-top: 18px;
      padding: 14px;
      background: var(--primary);
      color: white;
      font-size: 15px;
      font-weight: 600;
      border: none;
      border-radius: 10px;
      cursor: pointer;
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 8px;
      transition: background 0.2s, transform 0.1s;
    }
    .btn-submit:hover {
      background: var(--primary-hover);
    }
    .btn-submit:active {
      transform: scale(0.99);
    }
    .btn-submit:disabled {
      background: #94a3b8;
      cursor: not-allowed;
    }
    .hint {
      margin-top: 14px;
      font-size: 12px;
      color: #64748b;
      line-height: 1.5;
      text-align: center;
    }
    .loading-spinner {
      display: none;
      width: 18px;
      height: 18px;
      border: 2px solid #ffffff;
      border-top-color: transparent;
      border-radius: 50%;
      animation: spin 0.8s linear infinite;
    }
    @keyframes spin {
      to { transform: rotate(360deg); }
    }
    .error-banner {
      display: none;
      margin-top: 16px;
      padding: 12px;
      background: #fef2f2;
      border: 1px solid #fee2e2;
      border-radius: 8px;
      color: #b91c1c;
      font-size: 13px;
      line-height: 1.4;
    }
  </style>
</head>
<body>
  <div class="container">
    <div class="header">
      <div class="badge">
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="20 6 9 17 4 12"/></svg>
        Android & Desktop Ready
      </div>
      <h1>ChatGPT to PDF</h1>
      <p class="subtitle">Convert any conversation link to a clean, readable PDF</p>
    </div>

    <div class="tabs">
      <button class="tab-btn active" onclick="switchTab('linkTab', this)">Shared Link</button>
      <button class="tab-btn" onclick="switchTab('pasteTab', this)">Direct Markdown</button>
    </div>

    <!-- Link Mode -->
    <div id="linkTab" class="tab-content active">
      <form id="linkForm" onsubmit="handleFormSubmit(event, 'link')">
        <label for="shareUrl">ChatGPT Share Link</label>
        <input 
          type="url" 
          id="shareUrl" 
          name="share_url" 
          placeholder="https://chatgpt.com/share/..." 
          required 
          autocomplete="off"
        >
        <button type="submit" class="btn-submit" id="linkBtn">
          <span class="loading-spinner" id="linkSpinner"></span>
          <span class="btn-text" id="linkText">Generate PDF</span>
        </button>
      </form>
      <p class="hint">Open ChatGPT on phone or desktop &rarr; Tap Share &rarr; Copy Link &rarr; Paste here.</p>
    </div>

    <!-- Direct Paste Mode -->
    <div id="pasteTab" class="tab-content">
      <form id="pasteForm" onsubmit="handleFormSubmit(event, 'paste')">
        <label for="rawMarkdown">Paste Conversation / Markdown</label>
        <textarea 
          id="rawMarkdown" 
          name="markdown_text" 
          placeholder="Paste ChatGPT answers or exported text here..." 
          required
        ></textarea>
        <button type="submit" class="btn-submit" id="pasteBtn">
          <span class="loading-spinner" id="pasteSpinner"></span>
          <span class="btn-text" id="pasteText">Generate PDF</span>
        </button>
      </form>
      <p class="hint">Instant offline conversion directly from your clipboard.</p>
    </div>

    <div class="error-banner" id="errorBanner"></div>
  </div>

  <script>
    function switchTab(tabId, el) {
      document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
      document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
      el.classList.add('active');
      document.getElementById(tabId).classList.add('active');
      document.getElementById('errorBanner').style.display = 'none';
    }

    async function handleFormSubmit(event, mode) {
      event.preventDefault();
      const errorBanner = document.getElementById('errorBanner');
      errorBanner.style.display = 'none';

      const btn = mode === 'link' ? document.getElementById('linkBtn') : document.getElementById('pasteBtn');
      const spinner = mode === 'link' ? document.getElementById('linkSpinner') : document.getElementById('pasteSpinner');
      const text = mode === 'link' ? document.getElementById('linkText') : document.getElementById('pasteText');

      btn.disabled = true;
      spinner.style.display = 'inline-block';
      text.innerText = 'Creating PDF...';

      const formData = new FormData(event.target);

      try {
        const response = await fetch('/convert', {
          method: 'POST',
          body: formData
        });

        if (!response.ok) {
          const errData = await response.json().catch(() => ({ detail: 'Conversion failed' }));
          throw new Error(errData.detail || 'Failed to generate PDF');
        }

        const blob = await response.blob();
        let filename = 'ChatGPT_Conversation.pdf';
        const disposition = response.headers.get('Content-Disposition');
        if (disposition && disposition.includes('filename=')) {
          const match = disposition.match(/filename="?([^";]+)"?/);
          if (match && match[1]) filename = match[1];
        }

        const downloadUrl = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = downloadUrl;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        a.remove();
        window.URL.revokeObjectURL(downloadUrl);
      } catch (err) {
        errorBanner.innerText = err.message;
        errorBanner.style.display = 'block';
      } finally {
        btn.disabled = false;
        spinner.style.display = 'none';
        text.innerText = 'Generate PDF';
      }
    }
  </script>
</body>
</html>
"""

def generate_pdf_from_html(title: str, body_markdown: str) -> bytes:
    """Converts markdown content into a clean, paginated PDF document."""
    rendered_body = markdown.markdown(body_markdown, extensions=['fenced_code', 'tables'])
    
    styled_html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>{title}</title>
<style>
@page {{
    size: A4;
    margin: 20mm;
    @bottom-right {{
        content: counter(page) " / " counter(pages);
        font-size: 9pt;
        color: #64748b;
    }}
}}
body {{
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    font-size: 10pt;
    line-height: 1.6;
    color: #1e293b;
}}
h1 {{
    color: #0f172a;
    border-bottom: 2px solid #e2e8f0;
    padding-bottom: 8px;
    font-size: 18pt;
    margin-bottom: 16px;
}}
h2, h3 {{
    color: #1e293b;
    margin-top: 18px;
    margin-bottom: 8px;
}}
h3 {{
    color: #2563eb;
    background: #f8fafc;
    padding: 6px 12px;
    border-left: 4px solid #2563eb;
    border-radius: 4px;
    page-break-inside: avoid;
}}
pre {{
    background: #f1f5f9;
    padding: 12px;
    border-radius: 6px;
    font-family: Consolas, "Liberation Mono", Menlo, monospace;
    font-size: 8.5pt;
    overflow-x: auto;
    page-break-inside: avoid;
    border: 1px solid #e2e8f0;
}}
code {{
    font-family: Consolas, monospace;
    font-size: 9pt;
    background: #f1f5f9;
    padding: 2px 4px;
    border-radius: 3px;
}}
table {{
    border-collapse: collapse;
    width: 100%;
    margin: 14px 0;
    page-break-inside: avoid;
}}
th, td {{
    border: 1px solid #cbd5e1;
    padding: 7px 10px;
    text-align: left;
    font-size: 9.5pt;
}}
th {{
    background: #f8fafc;
    font-weight: 600;
}}
blockquote {{
    border-left: 4px solid #94a3b8;
    margin: 12px 0;
    padding-left: 14px;
    color: #475569;
    font-style: italic;
}}
p {{
    margin-bottom: 10px;
}}
ul, ol {{
    margin-bottom: 10px;
    padding-left: 20px;
}}
li {{
    margin-bottom: 4px;
}}
</style>
</head>
<body>
{rendered_body}
</body>
</html>"""

    return weasyprint.HTML(string=styled_html).write_pdf()

@app.get("/", response_class=HTMLResponse)
async def home():
    return HTMLResponse(content=HTML_TEMPLATE)

@app.post("/convert")
async def convert(
    share_url: Optional[str] = Form(None),
    markdown_text: Optional[str] = Form(None)
):
    if share_url and share_url.strip():
        url = share_url.strip()
        if not ("chatgpt.com/share/" in url or "chat.openai.com/share/" in url):
            raise HTTPException(status_code=400, detail="Invalid link. Please provide a valid ChatGPT share link.")
        
        try:
            html_doc = chatpeek_lib.fetch_share_page(url)
            chat = chatpeek_lib.parse_share_html(html_doc)
            title = chat.title or "ChatGPT_Conversation"
            markdown_content = chat.to_markdown()
        except Exception as e:
            raise HTTPException(status_code=422, detail=f"Could not parse chat link: {str(e)}")
    elif markdown_text and markdown_text.strip():
        title = "ChatGPT_Notes"
        markdown_content = f"# {title}\n\n" + markdown_text.strip()
    else:
        raise HTTPException(status_code=400, detail="Please enter a share link or paste markdown text.")

    try:
        pdf_bytes = generate_pdf_from_html(title, markdown_content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDF generation failed: {str(e)}")

    safe_title = re.sub(r'[^a-zA-Z0-9_\- ]', '', title).strip().replace(" ", "_") or "ChatGPT_Export"
    
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{safe_title}.pdf"'}
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
