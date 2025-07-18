import json
import os

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, PlainTextResponse

app = FastAPI()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(BASE_DIR, 'src', 'config.json')
LOG_PATH = os.path.join(BASE_DIR, 'logs', 'run.log')

@app.get("/status")
def get_status():
    # Show current config and last log line
    try:
        with open(CONFIG_PATH, 'r') as f:
            config = json.load(f)
    except Exception as e:
        config = {"error": str(e)}
    try:
        with open(LOG_PATH, 'r') as f:
            lines = f.readlines()
            last_log = lines[-10:] if len(lines) > 10 else lines
    except Exception as e:
        last_log = [f"Error reading log: {e}"]
    return {"config": config, "last_log": last_log}

@app.get("/config")
def get_config():
    try:
        with open(CONFIG_PATH, 'r') as f:
            config = json.load(f)
        return config
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

@app.post("/config")
async def set_config(request: Request):
    try:
        new_config = await request.json()
        with open(CONFIG_PATH, 'w') as f:
            json.dump(new_config, f, indent=2)
        return {"status": "ok"}
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

@app.get("/log")
def get_log():
    try:
        with open(LOG_PATH, 'r') as f:
            return PlainTextResponse(f.read())
    except Exception as e:
        return PlainTextResponse(f"Error reading log: {e}", status_code=500)

# To run: uvicorn api_server:app --reload
