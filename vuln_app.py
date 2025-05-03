from flask import Flask, redirect, url_for, request, session
import requests
from jose import jwt
from urllib.parse import urlencode

app = Flask(__name__)
app.secret_key = 'THIS_IS_INSECURE_SECRET'

# Google OAuth 2.0 Configuration
GOOGLE_CLIENT_ID = ''
GOOGLE_CLIENT_SECRET = ''
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
        <img src="{user.get('picture', '')}" alt="Profile Picture" width="100">
        <br><br><a href="/logout">Logout</a>
        """
    return '''
        <a href="/login">Sign in with Google</a><br><br>
        <a href="/callback?id_token=FAKE_TOKEN_HERE">Test Forged Login</a>
    '''

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
    forged_token = request.args.get("id_token")

    if code:
        # Secure Flow (real OAuth)
        data = {
            "code": code,
            "client_id": GOOGLE_CLIENT_ID,
            "client_secret": GOOGLE_CLIENT_SECRET,
            "redirect_uri": REDIRECT_URI,
            "grant_type": "authorization_code"
        }

        token_response = requests.post(TOKEN_URI, data=data)
        token_json = token_response.json()

        if "id_token" not in token_json:
            return f"Error getting ID token: {token_json}"

        id_token = token_json["id_token"]
    elif forged_token:
        # Vulnerable flow (insecure direct token usage)
        id_token = forged_token
    else:
        return "No code or id_token provided."

    try:
        userinfo = jwt.decode(
            id_token,
            key='',
            options={
                "verify_signature": False,
                "verify_aud": False,
                "verify_iss": False,
                "verify_exp": False,
                "verify_at_hash":False
            }
        )
        session["user"] = userinfo
        return redirect(url_for("index"))
    except Exception as e:
        return f"Failed to decode token: {e}"

@app.route('/logout')
def logout():
    session.pop("user", None)
    return redirect(url_for("index"))

if __name__ == '__main__':
    app.run(debug=True)
