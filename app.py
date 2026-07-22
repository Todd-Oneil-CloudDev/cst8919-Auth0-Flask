import os
import asyncio
import logging
import json
from flask import Flask, redirect, render_template, request, url_for, g, session
from auth0_server_python.auth_types import LogoutOptions
from auth import auth0
from dotenv import load_dotenv
from datetime import datetime, timezone

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('AUTH0_SECRET')
app.logger.setLevel(logging.INFO)
app.logger.propagate = False

domain = os.getenv('AUTH0_REDIRECT_URI').strip('callback')

# logging.basicConfig(level=logging.WARNING)
# logger = logging.getLogger(__name__)

# Configure session for Auth0
app.config.update(
    SESSION_COOKIE_SECURE=False,  # Set to True in production with HTTPS
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE='Lax',
)

def run_async(thing):
    """Run async Auth0 SDK calls safely inside Flask."""
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        # No event loop exists yet
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    if loop.is_running():
        # Flask already has an active loop → create a new one just for this task
        new_loop = asyncio.new_event_loop()
        try:
            return new_loop.run_until_complete(thing)
        finally:
            new_loop.close()
    else:
        return loop.run_until_complete(thing)

@app.before_request
def store_request_response():
    """Make request/response available for Auth0 SDK"""
    g.store_options = {"request": request}

@app.route('/')
def index():
    """Home page - shows login button or user profile"""
    user = run_async(auth0.get_user(g.store_options))
    return render_template('index.html', user=user)

@app.route('/login')
def login():
    """Redirect to Auth0 login"""
    authorization_url = run_async(auth0.start_interactive_login({}, g.store_options))

    return redirect(authorization_url)

@app.route('/callback')
def callback():
    print(f"CALLBACK ARGS: {request.args}", flush=True)
    """Handle Auth0 callback after login"""
    timestamp = datetime.now(timezone.utc).isoformat()
    try:
        result = run_async(auth0.complete_interactive_login(str(request.url), g.store_options))
        user = run_async(auth0.get_user(g.store_options))

        email = user.get("email") or user.get("sub")
        un = GetUsername(str(email))

        app.logger.info(json.dumps({
                "event_type": "LOGIN_SUCCESS",
                "timestamp": timestamp,
                "user_id": un,
                "email": email,
                "ip": request.remote_addr,
                "user_agent": request.headers.get("User-Agent"),
            }))
        return redirect(url_for('index'))
    except Exception as e:
        app.logger.warning(json.dumps({
                "event_type": "LOGIN_FAILURE",
                "timestamp": timestamp,
                "user_id": un,
                "email": email,
                "ip": request.remote_addr,
                "user_agent": request.headers.get("User-Agent"),
                "reason": type(e).__name__
            }))
        return f"Authentication error: {str(e)}", 400

@app.route('/profile')
def profile():
    """Protected route - shows user profile"""
    user = run_async(auth0.get_user(g.store_options))
    
    if not user:
        return redirect(url_for('login'))
    
    return render_template('profile.html', user=user)

@app.route('/logout')
def logout():
    """Logout and redirect to Auth0 logout"""
    options = LogoutOptions(return_to=url_for("index", _external=True))
    logout_url = run_async(auth0.logout(options, g.store_options))
    return redirect(logout_url)

@app.route('/protected')
def protected():
    """protected endpoint for authorized users"""
    user = run_async(auth0.get_user(g.store_options))

    if not user:
        app.logger.warning(json.dumps({
                "event_type": 'UNAUTHORIZED_ACCESS',
                "reason": "not_authenticated",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "ip": request.remote_addr,
                "user_agent": request.headers.get("User-Agent"),
            }))
        return redirect(url_for('login'))
    
    un = GetUsername(user.get('email'))
    roles = user.get(f"{domain}/roles") or []
    authorized = 'protected-access' in roles
    
    if not authorized:
        app.logger.warning(json.dumps({
                "event_type": 'UNAUTHORIZED_ACCESS',
                "reason": "not_authorized",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "user_id": un,
                "email": user.get('email'),
                "ip": request.remote_addr,
                "user_agent": request.headers.get("User-Agent"),
            }))
        return "Forbidden: insufficient permissions", 403
    
    app.logger.info(json.dumps({
                "event_type": 'PROTECTED_ACCESS',
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "user_id": un,
                "email": user.get('email'),
                "authorized": authorized,
                "ip": request.remote_addr,
                "user_agent": request.headers.get("User-Agent"),
            }))

    return render_template('protected.html', user=user)

def GetUsername(email: str):
    return str(email[:email.find('@')])

# if __name__ == '__main__':
#     app.run(debug=True, port=5000)