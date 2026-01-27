import { useEffect } from "react";
import { useNavigate } from "react-router-dom";
import srsLogo from "@/assets/sr-logo-dark.png";

export default function Login() {
  const navigate = useNavigate();

  useEffect(() => {
    // Auto-redirect to dashboard (no auth required in dev)
    navigate("/dashboard");
  }, [navigate]);

  return (
    <div className="min-h-screen bg-slate-950 flex items-center justify-center">
      <div className="text-center">
        <img src={srsLogo} alt="System Rapid Solutions" className="w-16 h-16 mx-auto mb-4" />
        <div className="text-cyan-400 animate-pulse">Redirigiendo...</div>
      </div>
    </div>
  );
}
