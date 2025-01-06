from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from starlette.middleware.sessions import SessionMiddleware
from authlib.integrations.starlette_client import OAuth
import os
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

load_dotenv()

# FastAPI app setup
app = FastAPI()

CLIENT_ID = os.environ.get("CLIENT_ID")
CLIENT_SECRET = os.environ.get("CLIENT_SECRET")

# Add session middleware
app.add_middleware(SessionMiddleware, secret_key=os.urandom(24))
# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust this to your needs
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# OAuth configuration
oauth = OAuth()
oidc = oauth.register(
    name="oidc",
    authority="https://cognito-idp.eu-west-2.amazonaws.com/eu-west-2_P52DmW0az",
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    server_metadata_url="https://cognito-idp.eu-west-2.amazonaws.com/eu-west-2_P52DmW0az/.well-known/openid-configuration",
    client_kwargs={"scope": "email openid phone"},
)


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    user = request.session.get("user")
    if user:
        return f'Hello, {user["email"]}. <a href="/logout">Logout</a>'
    else:
        return 'Welcome! Please <a href="/login">Login</a>.'


@app.get("/login")
async def login(request: Request):
    redirect_uri = "http://localhost:5000/cognito/callback"
    return await oidc.authorize_redirect(request, redirect_uri)


@app.get("/cognito/callback")
async def authorize(request: Request):
    token = await oidc.authorize_access_token(request)
    user = token.get("userinfo")
    if user:
        request.session["user"] = user
    return RedirectResponse(url="/")


@app.get("/logout")
async def logout(request: Request):
    request.session.pop("user", None)
    return RedirectResponse(url="/")
