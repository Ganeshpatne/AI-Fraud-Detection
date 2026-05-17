import React, { useState, useEffect } from 'react';
import { BrowserRouter, Routes, Route, Navigate, useLocation } from 'react-router-dom';
import Sidebar from './components/Sidebar.jsx';
import Dashboard from './pages/Dashboard.jsx';
import Transactions from './pages/Transactions.jsx';
import LiveAlerts from './pages/LiveAlerts.jsx';
import FraudSimulation from './pages/FraudSimulation.jsx';
import Reports from './pages/Reports.jsx';
import DatasetUpload from './pages/DatasetUpload.jsx';
import Login from './pages/Login.jsx';
import { getToken, getAuthUser, clearToken } from './api.js';
import ChatBot from './components/ChatBot.jsx';

function AppContent({ user, onLogin, onLogout, isDark, onToggleTheme }) {
  const location = useLocation();
  const isLoginPage = location.pathname === '/login';

  if (isLoginPage) {
    return user ? <Navigate to="/" replace /> : <Login onLogin={onLogin} />;
  }

  if (!user) return <Navigate to="/login" replace />;

  return (
    <div className="app-layout">
      <Sidebar user={user} onLogout={onLogout} isDark={isDark} onToggleTheme={onToggleTheme} />
      <main className="main-content">
        <Routes>
          <Route path="/" element={<DatasetUpload />} />
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/transactions" element={<Transactions />} />
          <Route path="/alerts" element={<LiveAlerts />} />
          <Route path="/simulation" element={<FraudSimulation />} />
          <Route path="/reports" element={<Reports />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </main>
      <ChatBot />
    </div>
  );
}

export default function App() {
  const [user, setUser] = useState(null);
  const [isDark, setIsDark] = useState(() => {
    const saved = localStorage.getItem('theme');
    return saved ? saved === 'dark' : true; // default dark
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
        <Route path="/login" element={
          user ? <Navigate to="/" replace /> : <Login onLogin={handleLogin} />
        } />
        <Route path="/*" element={
          <AppContent
            user={user}
            onLogin={handleLogin}
            onLogout={handleLogout}
            isDark={isDark}
            onToggleTheme={handleToggleTheme}
          />
        } />
      </Routes>
    </BrowserRouter>
  );
}
