import { Zap } from "lucide-react";
import "./Card.css";
interface LatencyCardProps { latency: number; }
export default function LatencyCard({ latency }: LatencyCardProps) {
  const getLatencyColor = (lat: number) => lat < 200 ? "#0B6839" : lat < 500 ? "#FEE101" : "#FF0080";
  return <div className="card latency-card"><div className="card-header"><h3>Latency</h3><span className="card-icon"><Zap size={18} /></span></div><div className="card-content"><div className="latency-display"><span className="latency-value" style={{ color: getLatencyColor(latency) }}>{latency}ms</span><div className="latency-bar"><div className="latency-fill" style={{ width: `${Math.min((latency / 1000) * 100, 100)}%`, background: getLatencyColor(latency) }} /></div><p className="latency-label">{latency < 200 ? "Blazing fast" : latency < 500 ? "Fast" : "Optimize"}</p></div></div></div>;
}
