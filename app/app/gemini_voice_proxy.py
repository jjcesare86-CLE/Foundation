"""
gemini_voice_proxy.py

WebSocket proxy that bridges the frontend VoiceEmployeeChat component to
Gemini Live API. Handles per-agent voice selection, streams audio in/out,
and emits transcripts.

Frontend protocol:
  IN  (client -> server):
    {"type": "audio", "data": "<base64 pcm16 16kHz>"}
    {"type": "text",  "text": "..."}
    {"type": "end"}
  OUT (server -> client):
    {"type": "audio",      "data": "<base64 pcm16 24kHz>"}
    {"type": "transcript", "role": "user"|"agent", "text": "..."}
    {"type": "status",     "status": "idle"|"speaking"}
    {"type": "error",      "message": "..."}

ENV VAR:
  GOOGLE_API_KEY (already in Render env)
"""

import os
import asyncio
import base64
import json
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.foundation_agents import AGENT_VOICES, AGENT_PROMPTS

router = APIRouter()

DEFAULT_VOICE = "Aoede"
GEMINI_LIVE_MODEL = "models/gemini-2.0-flash-exp"

DEFAULT_PROMPT = "You are {agent_name}, a helpful AI employee. Be concise and natural."


@router.websocket("/api/voice/agent/{agent_name}")
async def voice_agent_ws(websocket: WebSocket, agent_name: str):
    await websocket.accept()

    api_key = os.environ.get("GOOGLE_API_KEY") or os.environ.get("GEMINI_API_KEY")
    if not api_key:
        await websocket.send_json({"type": "error", "message": "GOOGLE_API_KEY not configured"})
        await websocket.close()
        return

    voice = AGENT_VOICES.get(agent_name, DEFAULT_VOICE)
    system_prompt = AGENT_PROMPTS.get(agent_name, DEFAULT_PROMPT.format(agent_name=agent_name))

    try:
        from google import genai
        from google.genai import types
    except ImportError:
        await websocket.send_json({
            "type": "error",
            "message": "google-genai package not installed. Run: pip install google-genai",
        })
        await websocket.close()
        return

    client = genai.Client(api_key=api_key, http_options={"api_version": "v1alpha"})
    config = types.LiveConnectConfig(
        response_modalities=["AUDIO"],
        speech_config=types.SpeechConfig(
            voice_config=types.VoiceConfig(
                prebuilt_voice_config=types.PrebuiltVoiceConfig(voice_name=voice)
            )
        ),
        system_instruction=types.Content(parts=[types.Part(text=system_prompt)]),
    )

    try:
        async with client.aio.live.connect(model=GEMINI_LIVE_MODEL, config=config) as session:

            async def client_to_gemini():
                while True:
                    raw = await websocket.receive_text()
                    msg = json.loads(raw)
                    mtype = msg.get("type")

                    if mtype == "audio":
                        pcm_bytes = base64.b64decode(msg["data"])
                        await session.send_realtime_input(
                            audio=types.Blob(data=pcm_bytes, mime_type="audio/pcm;rate=16000")
                        )
                    elif mtype == "text":
                        await session.send_client_content(
                            turns=[types.Content(role="user", parts=[types.Part(text=msg["text"])])],
                            turn_complete=True,
                        )
                    elif mtype == "end":
                        return

            async def gemini_to_client():
                while True:
                    async for response in session.receive():
                        if response.data:
                            await websocket.send_json({
                                "type": "audio",
                                "data": base64.b64encode(response.data).decode(),
                            })
                        if response.text:
                            await websocket.send_json({
                                "type": "transcript",
                                "role": "agent",
                                "text": response.text,
                            })
                        if response.server_content and response.server_content.turn_complete:
                            await websocket.send_json({"type": "status", "status": "idle"})

            await asyncio.gather(client_to_gemini(), gemini_to_client())

    except WebSocketDisconnect:
        pass
    except Exception as exc:
        try:
            await websocket.send_json({"type": "error", "message": str(exc)})
        except Exception:
            pass
    finally:
        try:
            await websocket.close()
        except Exception:
            pass
