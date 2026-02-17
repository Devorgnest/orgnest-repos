import React, { useState } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import AdminReview from './components/Admin/AdminReview';
import LoginPage from './components/LoginPage';
import RequireAuth from './components/RequireAuth';
import Header from './components/Layout/Header';
import Footer from './components/Layout/Footer';

const App = () => {
  const [token, setToken] = useState(sessionStorage.getItem('token') || null);
  const [userName, setUserName] = useState(sessionStorage.getItem('username') || '');

  return (
    <Router>
      <div className="app-layout">
        <Header setToken={setToken} setUserName={setUserName} />

        <main className="main-content">
          <Routes>
            <Route
              path="/login"
              element={<LoginPage setToken={setToken} setUserName={setUserName} />}
            />
            <Route
              path="/admin-review"
              element={
                <RequireAuth>
                  <AdminReview />
                </RequireAuth>
              }
            />
            <Route
              path="*"
              element={
                token ? <Navigate to="/admin-review" replace /> : <Navigate to="/login" replace />
              }
            />
          </Routes>
        </main>

        <Footer />
      </div>
    </Router>
  );
};

export default App;
