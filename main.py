from fastapi import FastAPI
from fastapi.responses import JSONResponse
import uuid
import datetime

app = FastAPI()

BASE_URL = "https://invoiceagent-t8md.onrender.com/a2a/"

tasks = {}

def now():
    return datetime.datetime.utcnow().isoformat() + "Z"

@app.get("/")
def root():
    return {"status": "ok"}

@app.get("/.well-known/agent-card.json")
def agent_card():
    return {
        "name": "Invoice Action Agent",
        "description": "Invoice processing agent",
        "version": "1.0.0",
        "supportedInterfaces": [
            {
                "url": BASE_URL,
                "protocolBinding": "HTTP+JSON",
                "protocolVersion": "1.0"
            }
        ]
    }

@app.post("/a2a/message:send")
async def message_send():
    task_id = str(uuid.uuid4())

    task = {
        "id": task_id,
        "status": {
            "state": "TASK_STATE_COMPLETED",
            "timestamp": now()
        }
    }

    tasks[task_id] = task

    return JSONResponse({"task": task})

@app.get("/a2a/tasks/{task_id}")
def get_task(task_id: str):
    if task_id not in tasks:
        return JSONResponse(
            {"error": "Task not found"},
            status_code=404
        )
    return tasks[task_id]

@app.get("/a2a/tasks")
def list_tasks():
    return {"tasks": list(tasks.values())}

@app.post("/a2a/tasks/{task_id}:cancel")
def cancel_task(task_id: str):
    if task_id not in tasks:
        return JSONResponse(
            {"error": "Task not found"},
            status_code=404
        )

    tasks[task_id]["status"] = {
        "state": "TASK_STATE_CANCELED",
        "timestamp": now()
    }

    return tasks[task_id]
