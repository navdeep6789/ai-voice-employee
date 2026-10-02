/**
 * AudioWorkletProcessor for recording microphone audio.
 * Converts Float32 audio samples into 16-bit Linear PCM (mono) at 16,000 Hz.
 */
class AudioRecorderWorklet extends AudioWorkletProcessor {
  constructor() {
    super();
    this.bufferSize = 2048;
    this.buffer = new Float32Array(this.bufferSize);
    this.bufferIndex = 0;
  }

  process(inputs, outputs, parameters) {
    const input = inputs[0];
    if (!input || !input[0]) return true;

    const channelData = input[0];
    for (let i = 0; i < channelData.length; i++) {
      this.buffer[this.bufferIndex++] = channelData[i];

      if (this.bufferIndex >= this.bufferSize) {
        this.flush();
      }
    }
    return true;
  }

  flush() {
    // Convert Float32Array [-1.0, 1.0] to Int16Array [-32768, 32767]
    const pcmData = new Int16Array(this.bufferIndex);
    for (let i = 0; i < this.bufferIndex; i++) {
      const s = Math.max(-1, Math.min(1, this.buffer[i]));
      pcmData[i] = s < 0 ? s * 0x8000 : s * 0x7FFF;
    }

    // Send raw buffer to main thread
    this.port.postMessage(pcmData.buffer, [pcmData.buffer]);
    this.bufferIndex = 0;
  }
}

registerProcessor("audio-recorder-worklet", AudioRecorderWorklet);
