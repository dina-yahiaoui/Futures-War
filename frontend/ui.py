# ui.py — Sert la page HTML via FastAPI (remplace l'ancien Flask)
# À importer dans app.py avec : from ui import register_ui
# Puis appeler : register_ui(app)

from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
import os

def register_ui(app: FastAPI):
    """Monte la route GET / qui sert le fichier visio_standalone.html"""

    html_path = os.path.join(os.path.dirname(__file__), "templates", "visio_standalone.html")

    @app.get("/", response_class=HTMLResponse, tags=["ui"])
    async def serve_ui():
        with open(html_path, "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())