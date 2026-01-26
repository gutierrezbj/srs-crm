import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import axios from "axios";
import { GoogleLogin } from "@react-oauth/google";
import srsLogo from "@/assets/sr-logo-dark.png";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

export default function Login() {
  const navigate = useNavigate();
  const [checking, setChecking] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    // Check if already authenticated
    const checkAuth = async () => {
      try {
        await axios.get(`${API}/auth/me`, { withCredentials: true });
        navigate("/dashboard");
      } catch {
        setChecking(false);
      }
    };
    checkAuth();
  }, [navigate]);

  const handleGoogleSuccess = async (credentialResponse) => {
    try {
      setError(null);
      const response = await axios.post(
        `${API}/auth/google`,
        { token: credentialResponse.credential },
        { withCredentials: true }
      );

      if (response.data.success) {
        navigate("/dashboard");
      }
    } catch (err) {
      console.error("Login error:", err);
      setError(err.response?.data?.detail || "Error al iniciar sesión");
    }
  };

  const handleGoogleError = () => {
    setError("Error al iniciar sesión con Google");
  };

  if (checking) {
    return (
      <div className="min-h-screen bg-slate-950 flex items-center justify-center">
        <div className="text-cyan-400 animate-pulse">Verificando sesión...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-950 relative overflow-hidden">
      {/* Background with drone image */}
      <div
        className="absolute inset-0 bg-cover bg-center opacity-20"
        style={{
          backgroundImage: 'url(https://images.unsplash.com/photo-1589510969447-1c1f09db34e1?crop=entropy&cs=srgb&fm=jpg&q=85)'
        }}
      />
      <div className="absolute inset-0 bg-gradient-to-br from-slate-950 via-slate-950/95 to-slate-900/90" />

      {/* Content */}
      <div className="relative z-10 min-h-screen flex flex-col items-center justify-center px-4">
        {/* Logo/Brand */}
        <div className="mb-12 text-center">
          <div className="inline-flex items-center gap-3 mb-4">
            <img src={srsLogo} alt="System Rapid Solutions" className="w-16 h-16" />
            <span className="text-2xl font-bold text-white">System Rapid Solutions</span>
          </div>
          <p className="text-slate-400 text-lg">CRM Interno</p>
        </div>

        {/* Login Card */}
        <div className="w-full max-w-md">
          <div className="bg-slate-900/50 backdrop-blur-xl border border-white/5 rounded-2xl p-8 shadow-2xl">
            <div className="text-center mb-8">
              <h1 className="text-2xl font-bold text-white mb-2">Bienvenido</h1>
              <p className="text-slate-400 text-sm">
                Accede con tu cuenta corporativa de Google
              </p>
            </div>

            {error && (
              <div className="mb-4 p-3 bg-red-500/10 border border-red-500/20 rounded-lg text-red-400 text-sm text-center">
                {error}
              </div>
            )}

            <div className="flex justify-center">
              <GoogleLogin
                onSuccess={handleGoogleSuccess}
                onError={handleGoogleError}
                theme="filled_black"
                size="large"
                text="continue_with"
                shape="rectangular"
                logo_alignment="left"
              />
            </div>

            <div className="mt-6 text-center">
              <p className="text-xs text-slate-500">
                Solo cuentas @systemrapidsolutions.com
              </p>
            </div>
          </div>

          {/* Footer */}
          <div className="mt-8 text-center">
            <p className="text-xs text-slate-600">
              Servicios IT & Drones
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
