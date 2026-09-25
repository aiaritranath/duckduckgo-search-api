from flask import Flask, request, jsonify
import serpapi
import os

app = Flask(__name__)

# --- Config ---
VALID_API_KEY = os.environ.get("SEARCH_API_KEY", "aritra")  # private key
SERPAPI_KEY   = os.environ.get("SERPAPI_KEY", "")
DEVELOPER     = "@its_aritra_nath"

def build_response(data, status=200):
    payload = {
        "developer": DEVELOPER,
        "powered_by": "SerpAPI · DuckDuckGo Engine",
        **data
    }
    return jsonify(payload), status

@app.route("/")
@app.route("/api/search")
def search():
    # 1. Validate private key
    key = request.args.get("key", "")
    if not key or key != VALID_API_KEY:
        return build_response({
            "status": "error",
            "message": "Invalid or missing API key. Use ?key=YOUR_KEY"
        }, 401)

    # 2. Validate query
    query = request.args.get("q", "").strip()
    if not query:
        return build_response({
            "status": "error",
            "message": "Missing query parameter 'q'"
        }, 400)

    if not SERPAPI_KEY:
        return build_response({
            "status": "error",
            "message": "Server misconfigured: SERPAPI_KEY not set"
        }, 500)

    # 3. Run search
    try:
        client = serpapi.Client(api_key=SERPAPI_KEY)
        results = client.search({
            "engine": "duckduckgo",
            "q": query,
            "kl": request.args.get("kl", "us-en")
        })
        organic = results.get("organic_results", [])
        return build_response({
            "status": "success",
            "query": query,
            "count": len(organic),
            "results": organic
        })
    except Exception as e:
        return build_response({
            "status": "error",
            "message": str(e)
        }, 500)

# Vercel WSGI handler
handler = app