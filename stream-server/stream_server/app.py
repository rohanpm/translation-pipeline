import os
import textwrap
from fastapi import FastAPI, Response, WebSocket

from stream_server.streamsource import STREAM_PATH, StreamSource

app = FastAPI()

THIS_DIR = os.path.dirname(__file__)
STREAM_HTML = os.path.join(THIS_DIR, "stream.html")


@app.get("/")
async def streamer():
    return Response(content=open(STREAM_HTML).read(), media_type="text/html")


@app.get("/status")
async def status():
    return Response(
        textwrap.dedent(
            f"""
                Stream server is running.\n\n
                Stream location: {STREAM_PATH}\n
            """
        ),
        media_type="text/plain",
    )


@app.websocket("/stream")
async def stream(ws: WebSocket):
    await ws.accept()
    await ws.send_json({"status": "connected"})

    src = StreamSource()

    while True:
        async for event in src.text_events:
            if event is None:
                await ws.send_json({"status": "connected"})
            else:
                await ws.send_json({"msg": event})


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("stream_server.app:app", host="0.0.0.0", port=8051, log_level="info")
