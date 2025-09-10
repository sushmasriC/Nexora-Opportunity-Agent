import React, { useEffect } from 'react';
import { useSession, useUser } from '@descope/react-sdk';

const DescopeTest: React.FC = () => {
  const { isAuthenticated, isSessionLoading, sessionToken } = useSession();
  const { user, isUserLoading } = useUser();

  useEffect(() => {
    console.log('Descope Test - Session:', {
      isAuthenticated,
      isSessionLoading,
      sessionToken: sessionToken ? 'Present' : 'Not present'
    });
    
    console.log('Descope Test - User:', {
      user,
      isUserLoading
    });
  }, [isAuthenticated, isSessionLoading, sessionToken, user, isUserLoading]);

  return (
    <div style={{ padding: '20px', border: '1px solid #ccc', margin: '20px' }}>
      <h3>Descope Test Component</h3>
      <p><strong>Session Loading:</strong> {isSessionLoading ? 'Yes' : 'No'}</p>
      <p><strong>User Loading:</strong> {isUserLoading ? 'Yes' : 'No'}</p>
      <p><strong>Authenticated:</strong> {isAuthenticated ? 'Yes' : 'No'}</p>
      <p><strong>Session Token:</strong> {sessionToken ? 'Present' : 'Not present'}</p>
      <p><strong>User:</strong> {user ? JSON.stringify(user, null, 2) : 'No user'}</p>
    </div>
  );
};

export default DescopeTest;
