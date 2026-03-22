import React, { createContext, useContext, useState, useEffect } from 'react';

const AuthContext = createContext();

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Check for existing token on mount
    const token = sessionStorage.getItem('token');
    if (token) {
      setIsLoggedIn(true);
      // You could decode the token here to get user info
    }
    setLoading(false);
  }, []);

  const login = (token, userData = null) => {
    sessionStorage.setItem('token', token);
    setIsLoggedIn(true);
    setUser(userData);
  };

  const logout = () => {
    sessionStorage.removeItem('token');
    setIsLoggedIn(false);
    setUser(null);
  };

  const getToken = () => {
    return sessionStorage.getItem('token');
  };

  const value = {
    isLoggedIn,
    user,
    loading,
    login,
    logout,
    getToken,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};

export default AuthContext;
