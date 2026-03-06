from __future__ import annotations

import secrets
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates

from app.bot import start_bot
from app.oauth import DiscordOAuth
from app.storage import UserStorage


oauth = DiscordOAuth()
storage = UserStorage()
templates = Jinja2Templates(directory="templates")
state_store: set[str] = set()


@asynccontextmanager
async def lifespan(_: FastAPI):
    await start_bot()
    yield


app = FastAPI(title="Discord OAuth Link Bot", lifespan=lifespan)


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "linked_users": len(storage.get_all_users()),
        },
    )


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/login")
async def login() -> RedirectResponse:
    state = secrets.token_urlsafe(24)
    state_store.add(state)
    auth_url = oauth.get_authorize_url(state)
    return RedirectResponse(url=auth_url, status_code=302)


@app.get("/callback")
async def callback(code: str | None = None, state: str | None = None, error: str | None = None):
    if error:
        raise HTTPException(status_code=400, detail=f"OAuth error: {error}")
    if not code or not state:
        raise HTTPException(status_code=400, detail="Missing code or state")
    if state not in state_store:
        raise HTTPException(status_code=400, detail="Invalid state")
    state_store.remove(state)

    token_data = await oauth.exchange_code(code)
    access_token = token_data.get("access_token")
    refresh_token = token_data.get("refresh_token")
    if not access_token:
        raise HTTPException(status_code=400, detail="No access token returned")

    user = await oauth.get_current_user(access_token)
    user_id = user["id"]

    storage.save_user(
        discord_user_id=user_id,
        payload={
            "user": user,
            "token": {
                "access_token": access_token,
                "refresh_token": refresh_token,
                "token_type": token_data.get("token_type"),
                "expires_in": token_data.get("expires_in"),
                "scope": token_data.get("scope"),
            },
        },
    )

    return JSONResponse(
        {
            "message": "Discord account linked successfully.",
            "user": {
                "id": user.get("id"),
                "username": user.get("username"),
                "global_name": user.get("global_name"),
            },
        }
    )


@app.get("/linked-users")
async def linked_users():
    data = storage.get_all_users()
    safe_summary = [
        {
            "id": user_id,
            "username": payload.get("user", {}).get("username"),
            "global_name": payload.get("user", {}).get("global_name"),
        }
        for user_id, payload in data.items()
    ]
    return {"count": len(safe_summary), "users": safe_summary}
