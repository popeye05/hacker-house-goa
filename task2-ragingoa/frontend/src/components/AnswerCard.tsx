import { Sparkles } from "lucide-react";
import "./Card.css";
interface AnswerCardProps { answer: string; isProcessing: boolean; }
export default function AnswerCard({ answer, isProcessing }: AnswerCardProps) {
  return <div className="card answer-card"><div className="card-header"><h3>RAG answer</h3><span className="card-icon"><Sparkles size={18} /></span></div><div className="card-content">{isProcessing ? <div className="loading"><div className="loading-dots"><span /><span /><span /></div></div> : answer ? <p className="answer">{answer}</p> : <p className="placeholder">Your grounded answer will appear here...</p>}</div></div>;
}
