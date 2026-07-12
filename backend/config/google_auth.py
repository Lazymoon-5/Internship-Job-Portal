"""
Google Sign-In ("Continue with Google") token verification.

HOW TO SET THIS UP (takes about 5 minutes):
1. Go to https://console.cloud.google.com/
2. Create a new project (or use an existing one).
3. Go to "APIs & Services" -> "OAuth consent screen" -> configure it
   (External, add app name, your email, save).
4. Go to "APIs & Services" -> "Credentials" -> "Create Credentials"
   -> "OAuth client ID" -> Application type: "Web application".
5. Under "Authorized JavaScript origins", add your frontend URL
   (e.g. http://localhost:3000).
6. Copy the generated "Client ID" (looks like
   123456789-abc...apps.googleusercontent.com).
7. Put it in .env as GOOGLE_CLIENT_ID.
8. On the FRONTEND (React), use this Client ID with Google's
   "Sign In With Google" button/library. When a user signs in, Google
   gives the frontend an "id_token" — send that to our backend's
   POST /api/student/google-login endpoint as {"id_token": "..."}.

Until GOOGLE_CLIENT_ID is set, google_login() in the controller returns
a clear 501 error instead of crashing, so the rest of the app works fine.
"""

import os

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID")


def verify_google_token(id_token_str: str):
    """
    Returns (payload, error_message).
    payload contains at least: sub (Google's unique user id), email, name.
    """
    try:
        from google.oauth2 import id_token as google_id_token
        from google.auth.transport import requests as google_requests
    except ImportError:
        return None, "Google auth library not installed. Run: pip install google-auth"

    try:
        payload = google_id_token.verify_oauth2_token(
            id_token_str, google_requests.Request(), GOOGLE_CLIENT_ID
        )

        # Extra safety: confirm the token was issued by Google, not forged
        if payload.get("iss") not in ["accounts.google.com", "https://accounts.google.com"]:
            return None, "Invalid token issuer."

        if not payload.get("email_verified", False):
            return None, "Google account email is not verified."

        return payload, None
    except ValueError as e:
        return None, f"Invalid Google token: {str(e)}"
    except Exception as e:
        # Catches network errors (e.g. can't reach Google's cert servers),
        # or any other unexpected failure — so this never crashes the
        # request with a raw 500, always returns a clean JSON error.
        return None, f"Google verification failed: {str(e)}"
