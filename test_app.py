from fastapi.testclient import TestClient
from app import app
import pypdf
import io

client = TestClient(app)

def test_home_page():
    print("Testing GET / ...")
    response = client.get("/")
    assert response.status_code == 200
    assert "ChatGPT to PDF" in response.text
    print("[PASS] GET / returned 200 with HTML UI")

def test_convert_markdown():
    print("Testing POST /convert with direct markdown...")
    data = {
        "markdown_text": "### User\nWhat is Python?\n\n### Assistant\nPython is a high-level programming language."
    }
    response = client.post("/convert", data=data)
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/pdf"
    
    # Verify PDF is valid
    pdf_reader = pypdf.PdfReader(io.BytesIO(response.content))
    assert len(pdf_reader.pages) >= 1
    print(f"[PASS] POST /convert with markdown succeeded (PDF pages: {len(pdf_reader.pages)})")

def test_convert_live_link():
    print("Testing POST /convert with live ChatGPT share link...")
    data = {
        "share_url": "https://chatgpt.com/share/6ad2ecbd-b380-83e8-8a26-dc8521a8a582"
    }
    response = client.post("/convert", data=data)
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/pdf"
    
    pdf_reader = pypdf.PdfReader(io.BytesIO(response.content))
    assert len(pdf_reader.pages) >= 1
    print(f"[PASS] POST /convert with live link succeeded (PDF pages: {len(pdf_reader.pages)})")

if __name__ == "__main__":
    test_home_page()
    test_convert_markdown()
    test_convert_live_link()
    print("\nALL TESTS PASSED SUCCESSFULLY!")
