import React, { useState, useEffect } from 'react';
import { BrowserRouter, Routes, Route, Navigate, useLocation, Outlet } from 'react-router-dom';
import Sidebar from './components/Sidebar.jsx';
import Dashboard from './pages/Dashboard.jsx';
import Transactions from './pages/Transactions.jsx';
import LiveAlerts from './pages/LiveAlerts.jsx';
import FraudSimulation from './pages/FraudSimulation.jsx';
import Reports from './pages/Reports.jsx';
import DatasetUpload from './pages/DatasetUpload.jsx';
import Login from './pages/Login.jsx';
import LandingPage from './pages/LandingPage.jsx';
import { getToken, getAuthUser, clearToken } from './api.js';
import ChatBot from './components/ChatBot.jsx';

/* ─── Protected App Shell ──────────────────────────────────── */
function AppShell({ user, onLogout, isDark, onToggleTheme }) {
  return (
    <div className="app-layout">
      <Sidebar user={user} onLogout={onLogout} isDark={isDark} onToggleTheme={onToggleTheme} />
      <main className="main-content">
        <Outlet />
      </main>
      <ChatBot />
    </div>
  );
}

/* ─── Protected Route Wrapper ──────────────────────────────── */
function ProtectedRoute({ user, children }) {
  if (!user) return <Navigate to="/login" replace />;
  return children;
}

export default function App() {
  const [user, setUser] = useState(null);
  const [isDark, setIsDark] = useState(() => {
    const saved = localStorage.getItem('theme');
    return saved ? saved === 'dark' : false;
  });

  useEffect(() => {
    const token = getToken();
    const authUser = getAuthUser();
    if (token && authUser) {
      setUser(authUser);
    }
  }, []);

  useEffect(() => {
    document.documentElement.setAttribute('data-theme', isDark ? 'dark' : 'light');
    localStorage.setItem('theme', isDark ? 'dark' : 'light');
  }, [isDark]);

  const handleLogin = (result) => {
    setUser({ id: result.user_id, username: result.username, role: result.role });
  };

  const handleLogout = () => {
    clearToken();
    setUser(null);
  };

  const handleToggleTheme = () => {
    setIsDark(prev => !prev);
  };

  return (
    <BrowserRouter>
      <Routes>
        {/* Public landing page */}
        <Route path="/" element={<LandingPage isDark={isDark} onToggleTheme={handleToggleTheme} />} />

        {/* Login page */}
        <Route path="/login" element={
          user ? <Navigate to="/app/dashboard" replace /> : <Login onLogin={handleLogin} />
        } />

        {/* Protected app shell */}
        <Route path="/app" element={
          <ProtectedRoute user={user}>
            <AppShell
              user={user}
              onLogout={handleLogout}
              isDark={isDark}
              onToggleTheme={handleToggleTheme}
            />
          </ProtectedRoute>
        }>
          <Route index element={<Navigate to="/app/upload" replace />} />
          <Route path="upload" element={<DatasetUpload />} />
          <Route path="dashboard" element={<Dashboard />} />
          <Route path="transactions" element={<Transactions />} />
          <Route path="alerts" element={<LiveAlerts />} />
          <Route path="simulation" element={<FraudSimulation />} />
          <Route path="reports" element={<Reports />} />
        </Route>

        {/* Fallback */}
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  );
}
