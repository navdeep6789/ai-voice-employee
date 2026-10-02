"use client";

import { useState, useRef, useCallback, useEffect } from "react";
import { VoiceState, ChatMessage, AgentActivityEvent, CustomerContext, ConversationSummary, BookingDetails } from "@/types";
import { WS_BASE_URL, fetchConversationSummary } from "@/lib/api";

interface UseVoiceSessionProps {
  sessionId: string;
  leadId?: string;
}

export function useVoiceSession({ sessionId, leadId }: UseVoiceSessionProps) {
  const [voiceState, setVoiceState] = useState<VoiceState>("IDLE");
  const [transcript, setTranscript] = useState<ChatMessage[]>([]);
  const [activityEvents, setActivityEvents] = useState<AgentActivityEvent[]>([]);
  const [customerContext, setCustomerContext] = useState<CustomerContext | null>(null);
  const [bookingConfirmed, setBookingConfirmed] = useState<BookingDetails | null>(null);
  const [summary, setSummary] = useState<ConversationSummary | null>(null);
  const [audioLevel, setAudioLevel] = useState<number>(0);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [isMuted, setIsMuted] = useState<boolean>(false);

  const socketRef = useRef<WebSocket | null>(null);
  const audioContextRef = useRef<AudioContext | null>(null);
  const mediaStreamRef = useRef<MediaStream | null>(null);
  const workletNodeRef = useRef<AudioWorkletNode | null>(null);
  const analyserRef = useRef<AnalyserNode | null>(null);
  const animationFrameRef = useRef<number | null>(null);

  // Audio playback queue scheduling
  const nextPlayTimeRef = useRef<number>(0);

  // Monitor audio levels for authentic visualization
  const startVolumeTracking = (analyser: AnalyserNode) => {
    const dataArray = new Uint8Array(analyser.frequencyBinCount);
    const updateLevel = () => {
      analyser.getByteFrequencyData(dataArray);
      let sum = 0;
      for (let i = 0; i < dataArray.length; i++) {
        sum += dataArray[i];
      }
      const avg = sum / dataArray.length;
      setAudioLevel(Math.min(100, Math.round((avg / 128) * 100)));
      animationFrameRef.current = requestAnimationFrame(updateLevel);
    };
    updateLevel();
  };

  const playPcmChunk = useCallback((arrayBuffer: ArrayBuffer) => {
    if (!audioContextRef.current) return;
    const ctx = audioContextRef.current;

    // Convert Int16Array PCM from server to Float32Array for Web Audio API
    const int16 = new Int16Array(arrayBuffer);
    const float32 = new Float32Array(int16.length);
    for (let i = 0; i < int16.length; i++) {
      float32[i] = int16[i] / 32768.0;
    }

    // Server output is typically 24kHz or 16kHz
    const audioBuffer = ctx.createBuffer(1, float32.length, 24000);
    audioBuffer.getChannelData(0).set(float32);

    const source = ctx.createBufferSource();
    source.buffer = audioBuffer;
    source.connect(ctx.destination);

    // Schedule contiguous playback to prevent pops
    const currentTime = ctx.currentTime;
    const startTime = Math.max(currentTime, nextPlayTimeRef.current);
    source.start(startTime);
    nextPlayTimeRef.current = startTime + audioBuffer.duration;
  }, []);

  const startVoice = useCallback(async () => {
    try {
      setErrorMessage(null);
      setVoiceState("CONNECTING");

      // 1. Initialize Web Audio Context
      const AudioCtx = window.AudioContext || (window as any).webkitAudioContext;
      const ctx = new AudioCtx({ sampleRate: 16000 });
      audioContextRef.current = ctx;

      // 2. Request user microphone
      const stream = await navigator.mediaDevices.getUserMedia({
        audio: {
          sampleRate: 16000,
          channelCount: 1,
          echoCancellation: true,
          noiseSuppression: true,
        },
      });
      mediaStreamRef.current = stream;

      // 3. Setup volume analyser
      const analyser = ctx.createAnalyser();
      analyser.fftSize = 256;
      analyserRef.current = analyser;
      startVolumeTracking(analyser);

      // 4. Load AudioWorklet for 16-bit PCM recording
      await ctx.audioWorklet.addModule("/audio-recorder-worklet.js");
      const source = ctx.createMediaStreamSource(stream);
      const workletNode = new AudioWorkletNode(ctx, "audio-recorder-worklet");
      workletNodeRef.current = workletNode;

      source.connect(analyser);
      source.connect(workletNode);
      workletNode.connect(ctx.destination);

      // 5. Connect WebSocket
      const wsUrl = `${WS_BASE_URL}/ws/voice?session_id=${sessionId}${leadId ? `&lead_id=${leadId}` : ""}`;
      const ws = new WebSocket(wsUrl);
      ws.binaryType = "arraybuffer";
      socketRef.current = ws;

      ws.onopen = () => {
        setVoiceState("CONNECTED");
        // Forward PCM chunks from AudioWorklet to WebSocket
        workletNode.port.onmessage = (event) => {
          if (ws.readyState === WebSocket.OPEN && !isMuted) {
            ws.send(event.data);
          }
        };
      };

      ws.onmessage = (event) => {
        if (event.data instanceof ArrayBuffer) {
          // Received binary audio chunk from model
          playPcmChunk(event.data);
        } else {
          try {
            const data = JSON.parse(event.data);
            if (data.type === "state_changed") {
              setVoiceState(data.state);
            } else if (data.type === "transcript") {
              setTranscript((prev) => [
                ...prev,
                {
                  id: `${Date.now()}-${Math.random().toString(36).substring(2, 6)}`,
                  speaker: data.speaker,
                  text: data.text,
                  timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
                },
              ]);
            } else if (data.type === "agent_event") {
              const evt: AgentActivityEvent = {
                id: `${Date.now()}-${Math.random().toString(36).substring(2, 6)}`,
                event_type: data.event.type,
                tool_name: data.event.tool,
                status: data.event.status || "success",
                duration_ms: data.event.duration_ms,
                payload: data.event.result || data.event.args || data.event,
                created_at: new Date().toISOString(),
              };
              setActivityEvents((prev) => [evt, ...prev]);

              if (data.event.tool === "book_meeting" && data.event.result?.ok) {
                setBookingConfirmed(data.event.result.data);
              }
            } else if (data.type === "customer_context_updated") {
              setCustomerContext(data.customer);
            } else if (data.type === "summary") {
              setSummary(data.summary);
            } else if (data.type === "error") {
              setErrorMessage(data.message);
              setVoiceState("ERROR");
            }
          } catch (e) {
            console.error("Failed to parse WebSocket JSON payload:", e);
          }
        }
      };

      ws.onerror = () => {
        setErrorMessage("Unable to connect to Voice Gateway. Please continue in Text Mode.");
        setVoiceState("ERROR");
      };

      ws.onclose = () => {
        if (voiceState !== "ENDED") {
          setVoiceState("IDLE");
        }
      };
    } catch (err: any) {
      console.error("Voice initialization error:", err);
      let msg = "Microphone access was denied or audio device unavailable.";
      if (err.name === "NotAllowedError" || err.name === "PermissionDeniedError") {
        msg = "Microphone permission was denied. You can continue using Text Mode.";
      }
      setErrorMessage(msg);
      setVoiceState("ERROR");
    }
  }, [sessionId, leadId, isMuted, playPcmChunk, voiceState]);

  const endVoice = useCallback(async () => {
    setVoiceState("ENDING");

    if (animationFrameRef.current) {
      cancelAnimationFrame(animationFrameRef.current);
    }
    if (socketRef.current && socketRef.current.readyState === WebSocket.OPEN) {
      socketRef.current.send(JSON.stringify({ type: "end" }));
      socketRef.current.close();
    }
    if (mediaStreamRef.current) {
      mediaStreamRef.current.getTracks().forEach((track) => track.stop());
      mediaStreamRef.current = null;
    }
    if (audioContextRef.current) {
      await audioContextRef.current.close().catch(() => {});
      audioContextRef.current = null;
    }

    setVoiceState("ENDED");
    setAudioLevel(0);

    // Fetch final summary from database
    try {
      const finalSummary = await fetchConversationSummary(sessionId);
      if (finalSummary) setSummary(finalSummary);
    } catch (e) {
      console.error("Could not fetch conversation summary on end:", e);
    }
  }, [sessionId]);

  const toggleMute = useCallback(() => {
    setIsMuted((prev) => !prev);
  }, []);

  const addManualTranscriptMessage = useCallback((speaker: "user" | "assistant", text: string) => {
    setTranscript((prev) => [
      ...prev,
      {
        id: `${Date.now()}-${Math.random().toString(36).substring(2, 6)}`,
        speaker,
        text,
        timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
      },
    ]);
  }, []);

  const recordManualEvents = useCallback((events: AgentActivityEvent[]) => {
    setActivityEvents((prev) => [...events, ...prev]);
  }, []);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (animationFrameRef.current) cancelAnimationFrame(animationFrameRef.current);
      if (socketRef.current) socketRef.current.close();
      if (mediaStreamRef.current) mediaStreamRef.current.getTracks().forEach((t) => t.stop());
      if (audioContextRef.current) audioContextRef.current.close().catch(() => {});
    };
  }, []);

  return {
    voiceState,
    transcript,
    activityEvents,
    customerContext,
    bookingConfirmed,
    summary,
    audioLevel,
    errorMessage,
    isMuted,
    startVoice,
    endVoice,
    toggleMute,
    setCustomerContext,
    setBookingConfirmed,
    addManualTranscriptMessage,
    recordManualEvents,
  };
}
