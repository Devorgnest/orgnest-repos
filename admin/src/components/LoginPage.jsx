import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import './LoginPage.css'; // Optional: for styling

const LoginPage = ({ setToken, setUserName }) => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const navigate = useNavigate();

  const handleLogin = async () => {
    try {
      const response = await fetch('http://127.0.0.1:5000/api/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password })
      });

      const data = await response.json();

      if (response.ok) {
        sessionStorage.setItem('token', data.token);
        sessionStorage.setItem('username', data.name); // persist name
        setToken(data.access_token);
        setUserName(data.name);
        navigate('/admin-review');
      } else {
        alert(data.error || 'Login failed');
      }
    } catch (error) {
      console.error('Login error:', error);
      alert('Login failed. Please try again.');
    }
  };

  return (
    <div className="login-container">
      <h2>Admin Login</h2>
      <input
        type="text"
        placeholder="Username"
        value={username}
        onChange={e => setUsername(e.target.value)}
        className="login-input"
      />
      <input
        type="password"
        placeholder="Password"
        value={password}
        onChange={e => setPassword(e.target.value)}
        className="login-input"
      />
      <button onClick={handleLogin} className="login-button">Login</button>
    </div>
  );
};

export default LoginPage;
