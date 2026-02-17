// src/App.jsx
import React, { useState } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Header from './components/Header/Header';
import Footer from './components/Footer/Footer';
import PrimaryReviewerPage from './components/Internal/PrimaryReviewerPage';
import LoginPage from './components/LoginPage';
import RequireAuth from './components/RequireAuth';

function App() {
  const [token, setToken] = useState(sessionStorage.getItem('token1') || null);
  const [userName, setUserName] = useState(sessionStorage.getItem('username') || '');

  return (
    <Router>
      <Header setToken={setToken} setUserName={setUserName} />

      <Routes>
        <Route
          path="/login"
          element={<LoginPage setToken={setToken} setUserName={setUserName} />}
        />
        <Route
          path="/primary-review"
          element={
            <RequireAuth token={token}>
              <PrimaryReviewerPage />
            </RequireAuth>
          }
        />
        <Route
          path="*"
          element={
            token ? (
              <Navigate to="/primary-review" replace />
            ) : (
              <Navigate to="/login" replace />
            )
          }
        />
      </Routes>

      <Footer />
    </Router>
  );
}

export default App;

