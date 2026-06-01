import subprocess
import re
import time
from pathlib import Path

SCRIPT_JS = "script.js"

# Replace this exact string in script.js
PLACEHOLDER = "API_URL_PLACEHOLDER"


def update_script_js(tunnel_url):
    path = Path("script.js")

    text = path.read_text()

    text = re.sub(
        r'const\s+API_URL\s*=\s*"[^"]*"',
        f'const API_URL = "{tunnel_url}"',
        text
    )

    path.write_text(text)

    print(f"Updated script.js with {tunnel_url}")


def main():

    print("Starting FastAPI server...")

    uvicorn_proc = subprocess.Popen(
        [
            "uvicorn",
            "server:app",
            "--host",
            "0.0.0.0",
            "--port",
            "8000",
        ]
    )

    time.sleep(3)

    print("Starting Cloudflare tunnel...")

    tunnel_proc = subprocess.Popen(
        [
            "cloudflared",
            "tunnel",
            "--url",
            "http://localhost:8000",
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
    )

    tunnel_url = None

    url_pattern = re.compile(
        r"https://[a-zA-Z0-9\-]+\.trycloudflare\.com"
    )

    for line in tunnel_proc.stdout:
        print(line, end="")

        match = url_pattern.search(line)

        if match:
            tunnel_url = match.group(0)
            print(f"\nTunnel URL found: {tunnel_url}")

            update_script_js(tunnel_url)
            subprocess.run(["git", "add", "."])
            subprocess.run(["git", "commit", "-m", "Update tunnel URL"])
            subprocess.run(["git", "push"])
            break

    if not tunnel_url:
        print("Failed to find tunnel URL")
        return

    try:
        uvicorn_proc.wait()
    except KeyboardInterrupt:
        print("\nStopping processes...")
        uvicorn_proc.terminate()
        tunnel_proc.terminate()


if __name__ == "__main__":
    main()