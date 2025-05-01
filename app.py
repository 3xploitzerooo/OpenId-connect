from flask import Flask, redirect, url_for, request, session
from jose import jwt
from urllib.parse import urlencode

app = Flask(__name__)
app.secret_key = 'THIS_IS_INSECURE_SECRET'

# OpenID Connect (OIDC) config
GOOGLE_CLIENT_ID = ''
REDIRECT_URI = "http://localhost:5000/callback"
AUTH_URI = "https://accounts.google.com/o/oauth2/v2/auth"

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
    return '<a href="/login">Sign in with Google</a><br><br><a href="/callback?id_token=FAKE_TOKEN_HERE">Test Forged Login</a>'

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
    forged_token = request.args.get("id_token")
    if not forged_token:
        return "No id_token provided (we're simulating a vulnerable app)."

    try:
        # Do NOT verify the signature - this is insecure and intentionally vulnerable
        userinfo = jwt.decode(
            forged_token,
            key='',  # No key since we are skipping signature verification
            options={
                "verify_signature": False,
                "verify_aud": False,
                "verify_iss": False,
                "verify_exp": False
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
