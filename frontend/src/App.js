import "@/App.css";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import axios from "axios";
import Login from "@/pages/Login";
import Dashboard from "@/pages/Dashboard";
import Leads from "@/pages/Leads";
import Pipeline from "@/pages/Pipeline";
import Reports from "@/pages/Reports";
import Admin from "@/pages/Admin";
import Oportunidades from "@/pages/Oportunidades";
import LicitacionesDrones from "@/pages/LicitacionesDrones";
import Layout from "@/components/Layout";
import { Toaster } from "@/components/ui/sonner";
import { ThemeProvider } from "@/context/ThemeContext";

// Configure axios defaults
axios.defaults.withCredentials = true;

// Default dev user (no auth required)
const devUser = {
  user_id: "dev_user",
  email: "dev@systemrapidsolutions.com",
  name: "Developer",
  role: "admin",
  picture: null
};

// App Router
function AppRouter() {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route
        path="/dashboard"
        element={
          <Layout user={devUser}>
            <Dashboard user={devUser} />
          </Layout>
        }
      />
      <Route
        path="/leads"
        element={
          <Layout user={devUser}>
            <Leads user={devUser} />
          </Layout>
        }
      />
      <Route
        path="/pipeline"
        element={
          <Layout user={devUser}>
            <Pipeline user={devUser} />
          </Layout>
        }
      />
      <Route
        path="/reports"
        element={
          <Layout user={devUser}>
            <Reports user={devUser} />
          </Layout>
        }
      />
      <Route
        path="/oportunidades"
        element={
          <Layout user={devUser}>
            <Oportunidades user={devUser} />
          </Layout>
        }
      />
      <Route
        path="/licitaciones-drones"
        element={
          <Layout user={devUser}>
            <LicitacionesDrones user={devUser} />
          </Layout>
        }
      />
      <Route
        path="/admin"
        element={
          <Layout user={devUser}>
            <Admin user={devUser} />
          </Layout>
        }
      />
      <Route path="/" element={<Navigate to="/dashboard" replace />} />
      <Route path="*" element={<Navigate to="/dashboard" replace />} />
    </Routes>
  );
}

function App() {
  return (
    <ThemeProvider>
      <div className="App">
        <BrowserRouter>
          <AppRouter />
          <Toaster position="top-right" />
        </BrowserRouter>
      </div>
    </ThemeProvider>
  );
}

export default App;
