# AI Voice Agents & Real-Time Voice Engineering

## Architecture
Our voice agents leverage ultra-low latency real-time streaming pipelines. Rather than cascading separate Speech-to-Text (STT), LLM text completion, and Text-to-Speech (TTS) layers (which typically introduce 2.5 to 4 seconds of unnatural lag), we utilize native multimodal models like the Gemini Live API.

### Audio Pipeline Specifications
1. **Audio Ingest**: Captured in the browser via Web Audio API and custom `AudioWorkletNode` streaming 16kHz 16-bit mono Linear PCM chunks directly over a persistent WebSocket.
2. **Backend Gateway**: FastAPI async WebSocket endpoint receives audio frames and forwards them to Gemini Live session.
3. **Reasoning & Tool Execution**: As the user speaks, Gemini Live transcribes and reasons in real time. When structured business operations are needed, it dispatches tool calls (`check_pricing`, `search_knowledge`, `check_calendar`, `book_meeting`).
4. **Audio Output**: 24kHz PCM audio frames stream from the model back through the WebSocket directly to the client's Web Audio buffer queue for immediate, stutter-free playback.

## Interruption & Turn-Taking Handling
- Supports natural user interruptions. When user speech is detected while the assistant is speaking, client playback is immediately stopped or ducked, and the agent transitions to LISTENING mode.
- Half-duplex and full-duplex conversational buffering prevents audio distortion or repeated frames.

## Security & Reliability Guardrails
- **Prompt Injection Defense**: System instructions enforce strict tool validation boundaries; the model cannot execute arbitrary shell or SQL commands.
- **Fail-Safe Text Fallback**: If the user denies microphone permissions or has an unstable network connection, the system gracefully falls back to text mode with 100% feature parity.
