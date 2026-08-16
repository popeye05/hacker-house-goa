import { Mic } from "lucide-react";
import "./Card.css";
interface TranscriptCardProps { transcript: string; isProcessing: boolean; }
export default function TranscriptCard({ transcript, isProcessing }: TranscriptCardProps) {
  return <div className="card"><div className="card-header"><h3>You said</h3><span className="card-icon"><Mic size={18} /></span></div><div className="card-content">{isProcessing ? <div className="loading"><div className="loading-dots"><span /><span /><span /></div></div> : transcript ? <p className="transcript">{transcript}</p> : <p className="placeholder">Your transcript will appear here...</p>}</div></div>;
}
