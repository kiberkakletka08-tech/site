from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from typing import Dict, Any
import asyncio
import logging
from datetime import datetime
import json

from database import init_db, update_pc_status, get_all_computers
from telegram_bot import send_telegram_notification

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("pc_monitor")

app = FastAPI()

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Templates
templates = Jinja2Templates(directory="templates")

# Store active connections: {computer_name: {"websocket": ws, "last_seen": timestamp}}
active_connections: Dict[str, Dict[str, Any]] = {}

@app.on_event("startup")
async def startup_event():
    await init_db()
    asyncio.create_task(cleanup_connections())

@app.get("/", response_class=HTMLResponse)
async def get_dashboard(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/api/status")
async def get_status_api():
    """Returns the current status of all computers (both online and historical)."""
    all_computers = await get_all_computers()
    
    # Mark online status based on active connections
    for pc in all_computers:
        if pc["name"] in active_connections:
            pc["is_online"] = True
        else:
            pc["is_online"] = False
            
    # Calculate stats
    total = len(all_computers)
    online = sum(1 for pc in all_computers if pc.get("is_online"))
    offline = total - online
    
    return {
        "computers": all_computers,
        "stats": {
            "total": total,
            "online": online,
            "offline": offline
        }
    }

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    computer_name = None
    try:
        # Initial handshake: expect "online:COMPUTER_NAME"
        data = await websocket.receive_text()
        if data.startswith("online:"):
            computer_name = data.split(":", 1)[1]
            active_connections[computer_name] = {
                "websocket": websocket,
                "last_seen": datetime.now()
            }
            await update_pc_status(computer_name, "online")
            logger.info(f"New connection: {computer_name}")
            
            # Use a ping loop to keep connection alive and update last_seen
            while True:
                try:
                    # Wait for message with a timeout to detect dead connections
                    message = await asyncio.wait_for(websocket.receive_text(), timeout=15)
                    if message == "ping":
                        active_connections[computer_name]["last_seen"] = datetime.now()
                        await websocket.send_text("pong")
                except asyncio.TimeoutError:
                    # If timeout, we check if client is still there by sending a ping?
                    # Or simpler: client should send pings. If no ping in 15s (assuming client pings every 5-10s), consider dead?
                    # Let's assume client sends "ping" every 5 seconds.
                    logger.warning(f"Timeout waiting for ping from {computer_name}")
                    break
        else:
            logger.warning(f"Invalid handshake: {data}")
            await websocket.close()
            
    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected: {computer_name}")
    except Exception as e:
        logger.error(f"Error in websocket connection: {e}")
    finally:
        if computer_name and computer_name in active_connections:
            del active_connections[computer_name]
            await update_pc_status(computer_name, "offline")
            await send_telegram_notification(f"🔴 ПК *{computer_name}* ушел в оффлайн!")

async def cleanup_connections():
    """Background task to remove stale connections."""
    while True:
        await asyncio.sleep(30)
        now = datetime.now()
        to_remove = []
        for name, data in active_connections.items():
            # If no activity for 30 seconds, force close
            if (now - data["last_seen"]).total_seconds() > 30:
                to_remove.append(name)
        
        for name in to_remove:
            logger.warning(f"Removing stale connection: {name}")
            ws = active_connections[name]["websocket"]
            try:
                await ws.close()
            except:
                pass
            if name in active_connections:
                del active_connections[name]
            await update_pc_status(name, "offline")
            await send_telegram_notification(f"🔴 ПК *{name}* отключен по таймауту!")
