import { useState } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import axios from "axios";
import {
  LayoutDashboard,
  Users,
  Kanban,
  LogOut,
  Menu,
  X,
  ChevronRight,
  Sun,
  Moon,
  Shield,
  BarChart3,
  Target
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { useTheme } from "@/context/ThemeContext";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const navItems = [
  { name: "Dashboard", path: "/dashboard", icon: LayoutDashboard },
  { name: "Leads", path: "/leads", icon: Users },
  { name: "Pipeline", path: "/pipeline", icon: Kanban },
  { name: "Oportunidades", path: "/oportunidades", icon: Target },
  { name: "Reportes", path: "/reports", icon: BarChart3 },
];

const adminNavItems = [
  { name: "Admin", path: "/admin", icon: Shield },
];

export default function Layout({ children, user }) {
  const navigate = useNavigate();
  const location = useLocation();
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const { theme, toggleTheme } = useTheme();

  // Combine nav items based on user role
  const allNavItems = user?.role === "admin"
    ? [...navItems, ...adminNavItems]
    : navItems;

  const handleLogout = async () => {
    try {
      await axios.post(`${API}/auth/logout`, {}, { withCredentials: true });
    } catch (e) {
      console.error("Logout error:", e);
    }
    navigate("/login");
  };

  const NavLink = ({ item }) => {
    const isActive = location.pathname === item.path;
    const Icon = item.icon;

    return (
      <button
        onClick={() => {
          navigate(item.path);
          setSidebarOpen(false);
        }}
        data-testid={`nav-${item.name.toLowerCase()}`}
        className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg transition-all duration-200 group ${isActive
            ? "bg-gradient-to-r from-cyan-400/10 to-blue-600/10 text-cyan-400 border-l-2 border-cyan-400"
            : "theme-text-secondary hover:text-cyan-500 hover:bg-cyan-400/10"
          }`}
      >
        <Icon className={`w-5 h-5 ${isActive ? "text-cyan-400" : "group-hover:text-cyan-500"}`} />
        <span className="font-medium">{item.name}</span>
        {isActive && <ChevronRight className="w-4 h-4 ml-auto" />}
      </button>
    );
  };

  return (
    <div className="min-h-screen theme-bg flex">
      {/* Mobile overlay */}
      {sidebarOpen && (
        <div
          className="fixed inset-0 bg-black/60 z-40 lg:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* Sidebar */}
      <aside
        className={`fixed lg:static inset-y-0 left-0 z-50 w-64 theme-bg-tertiary backdrop-blur-xl border-r transform transition-transform duration-300 ease-in-out ${sidebarOpen ? "translate-x-0" : "-translate-x-full lg:translate-x-0"
          }`}
        style={{ borderColor: 'var(--theme-border)' }}
      >
        <div className="flex flex-col h-full">
          {/* Logo */}
          <div className="p-6 border-b" style={{ borderColor: 'var(--theme-border)' }}>
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-cyan-500 to-blue-600 flex items-center justify-center shadow-lg shadow-cyan-500/20">
                <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                </svg>
              </div>
              <div>
                <h1 className="font-bold theme-text text-sm">System Rapid</h1>
                <p className="text-xs theme-text-muted">CRM</p>
              </div>
            </div>
          </div>

          {/* Navigation */}
          <nav className="flex-1 p-4 space-y-1">
            {allNavItems.map((item) => (
              <NavLink key={item.path} item={item} />
            ))}
          </nav>

          {/* User section */}
          <div className="p-4 border-t" style={{ borderColor: 'var(--theme-border)' }}>
            <div className="flex items-center gap-3 px-3 py-2 rounded-lg theme-bg-secondary mb-3" style={{ border: '1px solid var(--theme-border)' }}>
              <Avatar className="w-9 h-9">
                <AvatarImage src={user?.picture} />
                <AvatarFallback className="bg-gradient-to-br from-cyan-400 to-blue-600 text-white text-sm">
                  {user?.name?.charAt(0) || "U"}
                </AvatarFallback>
              </Avatar>
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium theme-text truncate">{user?.name}</p>
                <p className="text-xs theme-text-muted truncate">{user?.role === "admin" ? "Administrador" : "Usuario"}</p>
              </div>
            </div>

            {/* Theme Toggle */}
            <Button
              onClick={toggleTheme}
              variant="ghost"
              data-testid="theme-toggle-btn"
              className="w-full justify-start theme-text-secondary hover:text-cyan-400 hover:bg-cyan-400/10 mb-2"
            >
              {theme === "dark" ? (
                <>
                  <Sun className="w-4 h-4 mr-2" />
                  Modo claro
                </>
              ) : (
                <>
                  <Moon className="w-4 h-4 mr-2" />
                  Modo oscuro
                </>
              )}
            </Button>

            <Button
              onClick={handleLogout}
              variant="ghost"
              data-testid="logout-btn"
              className="w-full justify-start theme-text-secondary hover:text-red-400 hover:bg-red-400/10"
            >
              <LogOut className="w-4 h-4 mr-2" />
              Cerrar sesión
            </Button>
          </div>
        </div>
      </aside>

      {/* Main content */}
      <div className="flex-1 flex flex-col min-h-screen">
        {/* Mobile header */}
        <header className="lg:hidden sticky top-0 z-30 theme-bg-secondary/90 backdrop-blur-xl px-4 py-3" style={{ borderBottom: '1px solid var(--theme-border)' }}>
          <div className="flex items-center justify-between">
            <Button
              variant="ghost"
              size="icon"
              onClick={() => setSidebarOpen(true)}
              className="theme-text-secondary"
            >
              <Menu className="w-6 h-6" />
            </Button>
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-cyan-500 to-blue-600 flex items-center justify-center">
                <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                </svg>
              </div>
              <span className="font-semibold theme-text text-sm">SRS CRM</span>
            </div>
            <Avatar className="w-8 h-8">
              <AvatarImage src={user?.picture} />
              <AvatarFallback className="bg-gradient-to-br from-cyan-500 to-blue-600 text-white text-xs">
                {user?.name?.charAt(0) || "U"}
              </AvatarFallback>
            </Avatar>
          </div>
        </header>

        {/* Page content */}
        <main className="flex-1 p-4 lg:p-8 overflow-auto">
          {children}
        </main>
      </div>
    </div>
  );
}
