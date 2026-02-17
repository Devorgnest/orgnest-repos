import React from 'react';
import { useNavigate } from 'react-router-dom';
import './Header.css';

const Header = ({ setToken, setUserName }) => {
  const navigate = useNavigate();

  const handleLogout = () => {
    sessionStorage.removeItem('token');
    sessionStorage.removeItem('username');
    setToken(null);
    setUserName('');
    navigate('/login');
  };

  return (
    <header className="admin-header">
      <div className="admin-header-content">
        <img src="./Header.jpg" alt="Header" className="header-photo" />
        <button className="logout-button" onClick={handleLogout}>Logout</button>
      </div>
    </header>
  );
};

export default Header;
