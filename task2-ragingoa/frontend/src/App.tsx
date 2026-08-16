import { useState } from "react";
import "./App.css";
import VoiceRecorder from "./components/VoiceRecorder";
import TranscriptCard from "./components/TranscriptCard";
import AnswerCard from "./components/AnswerCard";
import LatencyCard from "./components/LatencyCard";
import logoSvg from "./assets/NerdRats RAG IN GOA.svg";
import footerTrees from "./assets/Trees.png";
import twitterIcon from "./assets/180-frame-1948754793-54-30952.svg";
import telegramIcon from "./assets/181-frame-1948754789-54-30958.svg";
function App() {
  const [isRecording, setIsRecording] = useState(false);
  const [transcript, setTranscript] = useState("");
  const [answer, setAnswer] = useState("");
  const [latency, setLatency] = useState<number | null>(null);
  const [isProcessing, setIsProcessing] = useState(false);

  const handleVoiceStart = () => {
    setIsRecording(true);
    setTranscript("");
    setAnswer("");
    setLatency(null);
  };

  const handleVoiceStop = async (audioBlob: Blob) => {
    setIsRecording(false);
    setIsProcessing(true);

    const formData = new FormData();
    formData.append("audio", audioBlob, "recording.wav");

    const start = performance.now();

    try {
      const response = await fetch("http://localhost:8000/api/query", {
        method: "POST",
        body: formData,
      });
      const data = await response.json();

      setTranscript(data.transcript || "");
      setAnswer(data.answer || "");
      setLatency(Math.round(performance.now() - start));
    } catch (error) {
      console.error("Error processing voice:", error);
      setAnswer("Sorry, there was an error processing your request.");
    } finally {
      setIsProcessing(false);
    }
  };

  return (
    <div className="app">
      <nav className="navbar">
        <div className="brand">
          <img src={logoSvg} alt="RAG in Goa" className="logo" />
        </div>

        <div className="social-icons">
          <a href="https://twitter.com" target="_blank" rel="noopener noreferrer" aria-label="Twitter">
            <img src={twitterIcon} alt="" />
          </a>
          <a href="https://t.me" target="_blank" rel="noopener noreferrer" aria-label="Telegram">
            <img src={telegramIcon} alt="" />
          </a>
        </div>
      </nav>

      <main className="main-content">
        <section className="hero">
          <img src={footerTrees} alt="" className="hero-trees" />

          <div className="hero-inner">
            <div className="hero-copy">
              <div className="badge">
                <span className="badge-dot" />
                VOICE-POWERED RAG
              </div>

              <h1 className="hero-title">
                <span className="small-caps">Ask anything</span>
                <span className="highlight">In your language.</span>
              </h1>

              <p className="hero-description">
                Speak naturally. We transcribe your question and retrieve a precise answer from the RAG we
                developed, We used the HF MSMARCO-XI dataset.We also used the Sarvam AI,for the STT.
                <br />
                Thank You-NerdRats.
              </p>
            </div>

            <div className="hero-panel">
              <VoiceRecorder
                isRecording={isRecording}
                isProcessing={isProcessing}
                onStart={handleVoiceStart}
                onStop={handleVoiceStop}
              />
            </div>
          </div>
        </section>

        <section className="results">
          <div className="results-heading">
            <span>RESPONSE WORKSPACE</span>
            <h2>Your conversation, grounded.</h2>
            <p>Your transcription and source-backed answer will live here after you speak.This should take no time!</p>
          </div>

          <div className="results-grid">
            <TranscriptCard transcript={transcript} isProcessing={isProcessing} />
            <AnswerCard answer={answer} isProcessing={isProcessing} />
          </div>

          {latency !== null && (
            <div className="latency-section">
              <LatencyCard latency={latency} />
            </div>
          )}
        </section>
      </main>

      <footer className="footer">
        <div className="footer-content">
          <div className="footer-identity">
            <p className="footer-brand">
              <span>N3RDRATS</span> x HACKER HOUSE GOA
            </p>
            <p className="footer-note">Voice-first answers, grounded in context.</p>
          </div>
          <p className="footer-task">HH GOA 2026 - TASK #2 - #RAGInGoa</p>
        </div>
      </footer>
    </div>
  );
}
export default App;
