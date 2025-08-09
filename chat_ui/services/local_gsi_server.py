from __future__ import annotations

import threading
import webbrowser
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse


HTML_TEMPLATE = """<!doctype html>
<html>
  <head>
    <meta charset=\"utf-8\" />
    <title>Sign in with Google</title>
    <script src=\"https://accounts.google.com/gsi/client\" async defer></script>
    <script>
      function handleCredentialResponse(resp) {
        fetch('/token', {
          method: 'POST', headers: {'Content-Type': 'application/json'},
          body: JSON.stringify({credential: resp.credential})
        }).then(() => {
          document.getElementById('status').innerText = 'Signed in. Closing…';
          setTimeout(() => { try { window.close(); } catch(e) {} try { window.open('', '_self'); window.close(); } catch(e) {} }, 300);
        });
      }
      window.onload = () => {
        google.accounts.id.initialize({ client_id: '%CLIENT_ID%', callback: handleCredentialResponse });
        google.accounts.id.renderButton(document.getElementById('gsi'), { theme: 'outline', size: 'large' });
        google.accounts.id.prompt();
      };
    </script>
  </head>
  <body>
    <div id=\"gsi\"></div>
    <p id=\"status\">Sign in to generate an ID token…</p>
  </body>
  </html>
"""


class TokenStore:
    id_token: str | None = None


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):  # noqa: N802
        if urlparse(self.path).path == "/":
            page = (HTML_TEMPLATE.replace('%CLIENT_ID%', self.server.google_client_id))  # type: ignore[attr-defined]
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(page.encode("utf-8"))
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):  # noqa: N802
        if urlparse(self.path).path == "/token":
            length = int(self.headers.get("Content-Length", "0"))
            data = self.rfile.read(length).decode("utf-8")
            import json
            try:
                payload = json.loads(data)
                TokenStore.id_token = payload.get("credential")
                self.send_response(200)
                self.end_headers()
            except Exception:
                self.send_response(400)
                self.end_headers()
        else:
            self.send_response(404)
            self.end_headers()


def get_id_token_via_local_gsi(google_client_id: str, host: str = "127.0.0.1", port: int = 8787) -> str:
    TokenStore.id_token = None
    httpd = HTTPServer((host, port), Handler)
    # attach client id to server instance
    setattr(httpd, 'google_client_id', google_client_id)
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    webbrowser.open(f"http://{host}:{port}/")
    # wait for token up to 2 minutes
    for _ in range(120):
        if TokenStore.id_token:
            break
        threading.Event().wait(1.0)
    try:
        httpd.shutdown()
    except Exception:
        pass
    if not TokenStore.id_token:
        raise RuntimeError("No ID token received. Ensure http://127.0.0.1:%d is an Authorized JavaScript origin." % port)
    return TokenStore.id_token  # type: ignore[return-value]


