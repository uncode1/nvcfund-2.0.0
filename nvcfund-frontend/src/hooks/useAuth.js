import React, { createContext, useContext, useState, useEffect } from 'react';
import apiService from '../services/api';

const AuthContext = createContext();

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  useEffect(() => {
    checkAuthStatus();
  }, []);

  const checkAuthStatus = async () => {
    try {
      // Check if token exists in localStorage
      const token = localStorage.getItem('token');
      if (!token) {
        setUser(null);
        setIsAuthenticated(false);
        return;
      }

      const response = await apiService.getAuthStatus();
      // Backend returns {status: "success", data: {authenticated: true, user: {...}}}
      if (response.status === 'success' && response.data.authenticated) {
        setUser(response.data.user);
        setIsAuthenticated(true);
      } else {
        // Token is invalid, clear it
        localStorage.removeItem('token');
        setUser(null);
        setIsAuthenticated(false);
      }
    } catch (error) {
      console.error('Auth status check failed:', error);
      // Clear invalid token
      localStorage.removeItem('token');
      setUser(null);
      setIsAuthenticated(false);
    } finally {
      setLoading(false);
    }
  };

  const login = async (username, password) => {
    try {
      const response = await apiService.login(username, password);
      // Backend returns {status: "success", data: {...}} or {status: "error", error: {...}}
      if (response.status === 'success') {
        // Store JWT token in localStorage
        localStorage.setItem('token', response.data.token);
        
        // Fetch updated user profile to get current last_login time
        try {
          const profileResponse = await apiService.getProfile();
          if (profileResponse.status === 'success') {
            setUser(profileResponse.data.user);
          } else {
            // Fallback to login response user data
            setUser(response.data.user);
          }
        } catch (profileError) {
          console.warn('Failed to fetch updated profile, using login data:', profileError);
          setUser(response.data.user);
        }
        
        setIsAuthenticated(true);
        return { success: true, user: response.data.user };
      } else {
        return { success: false, error: response.error?.message || 'Login failed' };
      }
    } catch (error) {
      console.error('Login error:', error);
      // Handle axios error response
      const errorMessage = error.response?.data?.error?.message || 'Connection error. Please try again.';
      return { 
        success: false, 
        error: errorMessage
      };
    }
  };

  const logout = async () => {
    try {
      await apiService.logout();
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      // Clear JWT token from localStorage
      localStorage.removeItem('token');
      setUser(null);
      setIsAuthenticated(false);
    }
  };

  const register = async (userData) => {
    try {
      const response = await apiService.register(userData);
      if (response.status === 'success') {
        return { success: true, message: response.message || 'Registration successful! Please log in.' };
      } else {
        return { success: false, error: response.error?.message || 'Registration failed' };
      }
    } catch (error) {
      console.error('Registration error:', error);
      return { 
        success: false, 
        error: error.response?.data?.error?.message || 'Registration failed. Please try again.' 
      };
    }
  };

  const updateProfile = async (data) => {
    try {
      const response = await apiService.updateProfile(data);
      if (response.status === 'success') {
        setUser({ ...user, ...data });
        return { success: true, message: response.message || 'Profile updated successfully' };
      } else {
        return { success: false, error: response.error?.message || 'Profile update failed' };
      }
    } catch (error) {
      console.error('Profile update error:', error);
      return { 
        success: false, 
        error: error.response?.data?.error?.message || 'Profile update failed. Please try again.' 
      };
    }
  };

  // User role and permission checking
  const hasRole = (role) => {
    return user?.role === role;
  };

  const hasAnyRole = (roles) => {
    return roles.includes(user?.role);
  };

  const isAdmin = () => {
    return hasAnyRole(['ADMIN', 'SUPER_ADMIN']);
  };

  const isBankingStaff = () => {
    return hasAnyRole(['BANKING_OFFICER', 'RELATIONSHIP_MANAGER', 'BRANCH_MANAGER']);
  };

  const isCompliance = () => {
    return hasAnyRole(['COMPLIANCE_OFFICER', 'RISK_MANAGER']);
  };

  const isTreasury = () => {
    return hasAnyRole(['TREASURY_OFFICER', 'SOVEREIGN_BANKER']);
  };

  // Utility methods
  const getUserDisplayName = () => {
    if (!user) return 'Guest';
    return user.first_name || user.username;
  };

  const getUserRoleDisplay = () => {
    if (!user) return '';
    const roleMap = {
      'USER': 'Client',
      'BUSINESS_USER': 'Business Client',
      'VIP_USER': 'VIP Client',
      'BANKING_OFFICER': 'Banking Officer',
      'RELATIONSHIP_MANAGER': 'Relationship Manager',
      'BRANCH_MANAGER': 'Branch Manager',
      'COMPLIANCE_OFFICER': 'Compliance Officer',
      'RISK_MANAGER': 'Risk Manager',
      'TREASURY_OFFICER': 'Treasury Officer',
      'SOVEREIGN_BANKER': 'Sovereign Banker',
      'ADMIN': 'Administrator',
      'SUPER_ADMIN': 'Super Administrator'
    };
    return roleMap[user.role] || user.role;
  };

  const value = {
    user,
    loading,
    isAuthenticated,
    login,
    logout,
    register,
    updateProfile,
    checkAuthStatus,
    hasRole,
    hasAnyRole,
    isAdmin,
    isBankingStaff,
    isCompliance,
    isTreasury,
    getUserDisplayName,
    getUserRoleDisplay,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};