import json
from dataclasses import dataclass
from subprocess import Popen, PIPE
from fastapi import FastAPI
from fastapi.responses import HTMLResponse, Response, JSONResponse
from pydantic import BaseModel

from devices import Device, get_usb_buses
from momo import momo

server = FastAPI()

config = json.load(open("config/config.json"))

available_ports = config["ports"]


@dataclass
class MomoProcess:
    port: int
    process: Popen


processes: dict[str, MomoProcess] = {}


@server.get("/")
def index():
    index_html = open("src/page/index.html", "r").read()
    return HTMLResponse(content=index_html, status_code=200)


@server.get("/static/{file_path}")
async def get_static(file_path: str):
    files = {
        "index.css": {
            "path": "src/page/index.css",
            "content_type": "text/css",
        },
        "index.js": {
            "path": "src/page/index.js",
            "content_type": "application/javascript",
        },
    }
    file = files.get(file_path)
    if not file:
        return Response(content="Not Found", status_code=404)
    return Response(
        content=open(file["path"]).read(),
        media_type=file["content_type"],
        status_code=200,
    )


@server.get("/devices")
async def get_devices():
    data = []
    for device in get_usb_buses():
        if processes.get(device.bus) is not None:
            data.append(
                {
                    "name": device.name,
                    "bus": device.bus,
                    "port": processes[device.bus].port,
                    "status": "running",
                }
            )
        else:
            data.append(
                {
                    "name": device.name,
                    "bus": device.bus,
                    "port": None,
                    "status": "stopped",
                }
            )
    return data


class LaunchRequest(BaseModel):
    bus: str


class LaunchResponse(BaseModel):
    success: bool
    message: str


@server.post("/launch", response_model=LaunchResponse)
async def launch(request: LaunchRequest):
    if processes.get(request.bus) is not None:
        return JSONResponse(
            content=LaunchResponse(
                success=False,
                message="already running",
            ).model_dump(),
            status_code=400,
        )

    devices = get_usb_buses()

    if not (request.bus in [device.bus for device in devices]):
        return JSONResponse(
            content=LaunchResponse(
                success=False,
                message="no such device",
            ).model_dump(),
            status_code=400,
        )

    if len(available_ports) == 0:
        return JSONResponse(
            content=LaunchResponse(
                success=False,
                message="port limit",
            ).model_dump(),
            status_code=400,
        )

    port = available_ports.pop(0)
    process = momo(bus=request.bus, port=port)
    processes[request.bus] = MomoProcess(port=port, process=process)

    return JSONResponse(
        content=LaunchResponse(
            success=True,
            message="ok",
        ).model_dump(),
        status_code=200,
    )


class StopRequest(BaseModel):
    bus: str


@server.delete("/stop")
async def stop(request: StopRequest):
    process = processes.get(request.bus)
    if process is not None:
        process.process.terminate()
        process.process.kill()
        available_ports.append(process.port)
        del processes[request.bus]
    return Response(
        content="ok",
        status_code=200,
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:server", host="0.0.0.0", port=8000, reload=True)
