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
GEMINI_LIVE_MODEL = "gemini-3.1-flash-live-preview"

DEFAULT_PROMPT = "You are {agent_name}, a helpful AI employee. Be concise and natural."


@router.websocket("/api/voice/agent/{agent_name}")
async def voice_agent_ws(websocket: WebSocket, agent_name: str):
    await websocket.accept()
    print(f"[VOICE] Client connected for agent: {agent_name}", flush=True)

    api_key = os.environ.get("GOOGLE_API_KEY") or os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("[VOICE] ERROR: GOOGLE_API_KEY not configured", flush=True)
        await websocket.send_json({"type": "error", "message": "GOOGLE_API_KEY not configured"})
        await websocket.close()
        return

    voice = AGENT_VOICES.get(agent_name, DEFAULT_VOICE)
    system_prompt = AGENT_PROMPTS.get(agent_name, DEFAULT_PROMPT.format(agent_name=agent_name))
    print(f"[VOICE] Using voice: {voice}, model: {GEMINI_LIVE_MODEL}", flush=True)

    try:
        from google import genai
        from google.genai import types
    except ImportError:
        print("[VOICE] ERROR: google-genai package not installed", flush=True)
        await websocket.send_json({
            "type": "error",
            "message": "google-genai package not installed. Run: pip install google-genai",
        })
        await websocket.close()
        return

    client = genai.Client(api_key=api_key, http_options={"api_version": "v1beta"})
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
            print("[VOICE] Gemini session opened successfully", flush=True)

            async def client_to_gemini():
                while True:
                    raw = await websocket.receive_text()
                    msg = json.loads(raw)
                    mtype = msg.get("type")

                    if mtype == "audio":
                        print("[VOICE] Received audio chunk from browser", flush=True)
                        pcm_bytes = base64.b64decode(msg["data"])
                        await session.send_realtime_input(
                            audio=types.Blob(data=pcm_bytes, mime_type="audio/pcm;rate=16000")
                        )
                    elif mtype == "text":
                        print(f"[VOICE] Received text from browser: {msg.get('text', '')[:80]}", flush=True)
                        await session.send_client_content(
                            turns=[types.Content(role="user", parts=[types.Part(text=msg["text"])])],
                            turn_complete=True,
                        )
                    elif mtype == "end":
                        print("[VOICE] Received end signal from browser", flush=True)
                        return

            async def gemini_to_client():
                while True:
                    async for response in session.receive():
                        print(f"[VOICE] Received response from Gemini: {type(response).__name__}", flush=True)
                        if response.data:
                            print("[VOICE] Sending audio chunk back to browser", flush=True)
                            await websocket.send_json({
                                "type": "audio",
                                "data": base64.b64encode(response.data).decode(),
                            })
                        if response.text:
                            role = "agent"
                            text = response.text
                            print(f"[VOICE] Sending transcript: role={role}, text={text[:80]}", flush=True)
                            await websocket.send_json({
                                "type": "transcript",
                                "role": role,
                                "text": text,
                            })
                        if response.server_content and response.server_content.turn_complete:
                            print("[VOICE] Turn complete, sending idle status", flush=True)
                            await websocket.send_json({"type": "status", "status": "idle"})

            await asyncio.gather(client_to_gemini(), gemini_to_client())

    except WebSocketDisconnect:
        print("[VOICE] WebSocket disconnected", flush=True)
    except Exception as exc:
        print(f"[VOICE] ERROR: {str(exc)}", flush=True)
        import traceback
        traceback.print_exc()
        try:
            await websocket.send_json({"type": "error", "message": str(exc)})
        except Exception:
            pass
    finally:
        print(f"[VOICE] Closing websocket for agent: {agent_name}", flush=True)
        try:
            await websocket.close()
        except Exception:
            pass
