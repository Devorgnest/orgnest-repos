// components/RequireAuth.jsx
import React from 'react';
import { Navigate } from 'react-router-dom';

const RequireAuth = ({ children }) => {
  const token = sessionStorage.getItem('token');
  return token ? children : <Navigate to="/login" replace />;
};

export default RequireAuth;
