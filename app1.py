from flask import Flask, redirect, url_for, request, session, render_template
import requests
import json
from jose import jwt
from urllib.parse import urlencode

app = Flask(__name__)
app.secret_key = 'YOUR_SECRET_KEY'  # Replace with any random string you want

# Replace with your actual credentials
GOOGLE_CLIENT_ID = '489703958449-iiqtp7trstd8rom3kbmpcag2da1dgvvf.apps.googleusercontent.com'
GOOGLE_CLIENT_SECRET = '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'
REDIRECT_URI = "http://localhost:5000/callback"

AUTH_URI = "https://accounts.google.com/o/oauth2/v2/auth"
TOKEN_URI = "https://oauth2.googleapis.com/token"

@app.route('/')
def index():
    user = session.get("user")
    if user:
        return f"""
        <h2>Welcome, {user.get('name')}</h2>
        <p>Email: {user.get('email')}</p>
        <img src="{user.get('picture')}" alt="Profile Picture">
        <br><br>
        <a href="/logout">Logout</a>
        """
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

    data = {
        "code": code,
        "client_id": GOOGLE_CLIENT_ID,
        "client_secret": GOOGLE_CLIENT_SECRET,
        "redirect_uri": REDIRECT_URI,
        "grant_type": "authorization_code"
    }

    # Exchange code for tokens
    token_response = requests.post(TOKEN_URI, data=data)
    token_json = token_response.json()

    if "id_token" not in token_json:
        return f"Error getting ID token: {token_json}"

    id_token = token_json["id_token"]

    try:
        userinfo = jwt.decode(
            id_token,
            key='',
            options={
                "verify_signature": False,
                "verify_aud": True,
                "verify_iss": False,
                "verify_at_hash": False
            },
            audience=GOOGLE_CLIENT_ID
        )
        session["user"] = userinfo
        return redirect(url_for("index"))
    except Exception as e:
        return f"Failed to decode ID token: {str(e)}"

@app.route('/logout')
def logout():
    session.pop("user", None)
    return redirect(url_for("index"))

if __name__ == '__main__':
    app.run(debug=True)

