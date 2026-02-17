import React from 'react';
import './Header.css';
import { useNavigate } from 'react-router-dom';

const Header = ({ setToken, setUserName }) => {
  const navigate = useNavigate();

  const handleLogout = () => {
    sessionStorage.removeItem('token1');
    sessionStorage.removeItem('username');
    setToken(null);
    setUserName('');
    navigate('/login');
  };

  return (
    <header className="primary-header">
      <div className="header-content">
        <img src='./Header.jpg' alt="Header" className="header-photo" />
        <button className="logout-button" onClick={handleLogout}>Logout</button>
      </div>
    </header>
  );
};

export default Header;
