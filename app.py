from flask import Flask, redirect, request, url_for, session
import requests
import json
from urllib.parse import urlencode
from jose import jwt

app = Flask(__name__)
app.secret_key = 'YOUR_SECRET_KEY'

# Replace with your actual credentials from Google Cloud Console
GOOGLE_CLIENT_ID = '489703958449-iiqtp7trstd8rom3kbmpcag2da1dgvvf.apps.googleusercontent.com'
GOOGLE_CLIENT_SECRET = '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'
REDIRECT_URI = 'http://localhost:5000/callback'

# Google's OAuth 2.0 endpoints
AUTH_URI = "https://accounts.google.com/o/oauth2/v2/auth"
TOKEN_URI = "https://oauth2.googleapis.com/token"
USERINFO_URI = "https://openidconnect.googleapis.com/v1/userinfo"

@app.route('/')
def index():
    return '<a href="/login">Sign in with Google</a>'

@app.route('/login')
def login():
    params = {
        "response_type": "code",
        "client_id": GOOGLE_CLIENT_ID,
        "redirect_uri": REDIRECT_URI,
        "scope": "openid email profile",
        "access_type": "offline",
        "prompt": "consent"
    }
    return redirect(f"{AUTH_URI}?{urlencode(params)}")

@app.route('/callback')
def callback():
    code = request.args.get("code")
    if not code:
        return "No code provided."

    # Exchange code for tokens
    data = {
        "code": code,
        "client_id": GOOGLE_CLIENT_ID,
        "client_secret": GOOGLE_CLIENT_SECRET,
        "redirect_uri": REDIRECT_URI,
        "grant_type": "authorization_code"
    }

    token_response = requests.post(TOKEN_URI, data=data)
    print("Raw Token Response:", token_response.text)

    if token_response.status_code != 200:
        return f"Failed to get token: {token_response.text}"

    token_json = token_response.json()

    if "id_token" not in token_json:
        return "No ID token returned. Something went wrong."

    id_token = token_json["id_token"]

    # Decode the JWT without verifying the signature
    try:
        userinfo = jwt.decode(
            id_token,
            key='',
            options={"verify_signature": False, "verify_aud": False, "verify_at_hash": False}
        )
    except Exception as e:
        return f"Error decoding ID token: {str(e)}"

    return f"User info:<br>{json.dumps(userinfo, indent=2)}"

if __name__ == '__main__':
    app.run(debug=True)
