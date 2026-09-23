import httpx
import time

def test_live_servers():
    print("Testing Backend on http://127.0.0.1:8000 ...")
    try:
        r = httpx.get("http://127.0.0.1:8000/", timeout=3.0)
        print("Backend Root Response:", r.status_code, r.json())
    except Exception as e:
        print("Backend Error:", e)

    print("\nTesting Frontend on http://127.0.0.1:5173 ...")
    try:
        r = httpx.get("http://127.0.0.1:5173/", timeout=3.0)
        print("Frontend Response Status:", r.status_code)
    except Exception as e:
        print("Frontend Error:", e)

    print("\nTesting Chat Endpoint via HTTP POST ...")
    try:
        r = httpx.post("http://127.0.0.1:8000/api/chat", json={"prompt": "Schedule a meeting with HR tomorrow at 10 AM."}, timeout=5.0)
        print("Chat Endpoint Response Status:", r.status_code)
        data = r.json()
        print("Governance Decision:", data["governance"]["decision"])
        print("Tool Execution Status:", data["tool_result"]["status"] if data.get("tool_result") else "None")
    except Exception as e:
        print("Chat Endpoint Error:", e)

if __name__ == "__main__":
    test_live_servers()
