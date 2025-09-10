import React, { createContext, useContext, useState } from "react";
import { useDescope, useSession, useUser } from "@descope/react-sdk";

type AuthContextType = {
  user: any | null;
  loading: boolean;
  error: string | null;
  isAuthenticated: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
};

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) throw new Error("useAuth must be used within AuthProvider");
  return context;
};

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const descope = useDescope(); // Get the full descope object
  const { isAuthenticated, isSessionLoading } = useSession();
  const { user: descopeUser, isUserLoading } = useUser(); // Use Descope's useUser hook

  // Since we're using Descope's built-in flows, we don't need custom login/register methods
  const login = async (email: string, password: string) => {
    // This won't be used since SignInFlow handles authentication
    console.log('Login method called but SignInFlow handles authentication');
  };

  const register = async (email: string, password: string) => {
    // This won't be used since SignUpFlow handles authentication
    console.log('Register method called but SignUpFlow handles authentication');
  };

  const logout = async () => {
    try {
      await descope?.logout();
    } catch (err: any) {
      console.error('Logout error:', err);
    }
  };

  return (
    <AuthContext.Provider value={{ 
      user: descopeUser, // Use Descope's user directly
      loading: isSessionLoading || isUserLoading, 
      error: null, // Descope flows handle their own errors
      isAuthenticated,
      login, 
      register, 
      logout 
    }}>
      {children}
    </AuthContext.Provider>
  );
};