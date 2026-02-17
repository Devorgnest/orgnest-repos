import React from 'react';
import { Navigate } from 'react-router-dom';

const RequireAuth = ({ children, token }) => {
  if (!token || token === 'null') {
    return <Navigate to="/login" replace />;
  }
  return children;
};

export default RequireAuth;
