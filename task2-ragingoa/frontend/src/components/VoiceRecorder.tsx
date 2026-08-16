import { useRef } from "react";
import { Mic, Square } from "lucide-react";
import "./VoiceRecorder.css";

interface VoiceRecorderProps {
  isRecording: boolean;
  isProcessing: boolean;
  onStart: () => void;
  onStop: (audioBlob: Blob) => void;
}

export default function VoiceRecorder({
  isRecording,
  isProcessing,
  onStart,
  onStop,
}: VoiceRecorderProps) {
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const chunksRef = useRef<Blob[]>([]);

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const mediaRecorder = new MediaRecorder(stream);
      mediaRecorderRef.current = mediaRecorder;
      chunksRef.current = [];

      mediaRecorder.ondataavailable = (e) => {
        if (e.data.size > 0) {
          chunksRef.current.push(e.data);
        }
      };

      mediaRecorder.onstop = () => {
        const audioBlob = new Blob(chunksRef.current, { type: "audio/wav" });
        onStop(audioBlob);
        stream.getTracks().forEach((track) => track.stop());
      };

      mediaRecorder.start();
      onStart();
    } catch (error) {
      console.error("Error accessing microphone:", error);
      alert("Please allow microphone access to use voice recording.");
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && mediaRecorderRef.current.state !== "inactive") {
      mediaRecorderRef.current.stop();
    }
  };

  return (
    <div className="voice-recorder">
      <button
        className={`mic-button ${isRecording ? "recording" : ""} ${
          isProcessing ? "processing" : ""
        }`}
        onClick={isRecording ? stopRecording : startRecording}
        disabled={isProcessing}
      >
        {isRecording ? (
          <Square size={32} fill="currentColor" />
        ) : (
          <Mic size={32} />
        )}
      </button>

      <div className="mic-label">
        {isProcessing
          ? "Processing..."
          : isRecording
          ? "Click to stop recording"
          : "Click to start speaking"}
      </div>

      {isRecording && (
        <div className="recording-indicator">
          <span className="recording-dot" />
          <span>Recording...</span>
        </div>
      )}
    </div>
  );
}

