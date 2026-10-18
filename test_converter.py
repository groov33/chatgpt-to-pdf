import chatpeek_lib
import markdown
import weasyprint

def test():
    url = 'https://chatgpt.com/share/6ad2ecbd-b380-83e8-8a26-dc8521a8a582'
    print("Fetching share page...")
    html_doc = chatpeek_lib.fetch_share_page(url)
    chat = chatpeek_lib.parse_share_html(html_doc)
    print("Extracted title:", chat.title)
    print("Replies:", len(chat.replies))
    
    md_text = chat.to_markdown()
    body_html = markdown.markdown(md_text, extensions=['fenced_code', 'tables'])
    
    styled_html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>{chat.title}</title>
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
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
    font-size: 10pt;
    line-height: 1.6;
    color: #1e293b;
}}
h1 {{ color: #0f172a; border-bottom: 2px solid #e2e8f0; padding-bottom: 8px; font-size: 18pt; }}
h2, h3 {{ color: #1e293b; margin-top: 18px; }}
h3 {{ color: #2563eb; background: #f8fafc; padding: 6px 10px; border-left: 4px solid #2563eb; border-radius: 4px; }}
pre {{ background: #f1f5f9; padding: 12px; border-radius: 6px; font-family: Consolas, monospace; font-size: 8.5pt; page-break-inside: avoid; }}
table {{ border-collapse: collapse; width: 100%; margin: 12px 0; }}
th, td {{ border: 1px solid #cbd5e1; padding: 6px 10px; text-align: left; }}
th {{ background: #f8fafc; }}
blockquote {{ border-left: 4px solid #94a3b8; margin: 0; padding-left: 12px; color: #475569; }}
</style>
</head>
<body>
{body_html}
</body>
</html>"""

    print("Generating PDF...")
    pdf_bytes = weasyprint.HTML(string=styled_html).write_pdf()
    with open('test_output.pdf', 'wb') as f:
        f.write(pdf_bytes)
    print("SUCCESS! Generated test_output.pdf, size in bytes:", len(pdf_bytes))

if __name__ == '__main__':
    test()
