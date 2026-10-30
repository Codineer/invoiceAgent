from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import uuid
import datetime

app = FastAPI()

MEDIA = "application/a2a+json"

BASE_URL = "https://invoiceagent-t8md.onrender.com/a2a/"

tasks = {}


def now():
    return datetime.datetime.utcnow().isoformat() + "Z"


def a2a(data, status_code=200):
    return JSONResponse(
        content=data,
        status_code=status_code,
        media_type=MEDIA
    )


@app.get("/")
def root():
    return a2a({
        "status": "ok"
    })


@app.get("/.well-known/agent-card.json")
def agent_card():
    return a2a({
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
    })


@app.post("/a2a/message:send")
async def message_send(request: Request):
    try:
        body = await request.json()
    except Exception:
        body = {}

    task_id = str(uuid.uuid4())

    task = {
        "id": task_id,
        "status": {
            "state": "TASK_STATE_COMPLETED",
            "timestamp": now()
        },
        "input": body
    }

    tasks[task_id] = task

    return a2a({
        "task": task
    })


@app.get("/a2a/tasks")
def list_tasks():
    return a2a({
        "tasks": list(tasks.values())
    })


@app.get("/a2a/tasks/{task_id}")
def get_task(task_id: str):
    task = tasks.get(task_id)

    if task is None:
        return a2a({
            "error": {
                "code": "NOT_FOUND",
                "message": "Task not found"
            }
        }, 404)

    return a2a(task)


@app.post("/a2a/tasks/{task_id}:cancel")
def cancel_task(task_id: str):
    task = tasks.get(task_id)

    if task is None:
        return a2a({
            "error": {
                "code": "NOT_FOUND",
                "message": "Task not found"
            }
        }, 404)

    task["status"] = {
        "state": "TASK_STATE_CANCELED",
        "timestamp": now()
    }

    return a2a(task)
