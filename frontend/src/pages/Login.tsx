import React from 'react';
import { useNavigate } from 'react-router-dom';
import { useDescope, useSession, useUser, SignUpOrInFlow } from '@descope/react-sdk';
import { Container, Paper, Typography, Box, Button } from '@mui/material';

const Login: React.FC = () => {
  const navigate = useNavigate();
  const { logout } = useDescope();
  const { isAuthenticated } = useSession();
  const { user } = useUser();

  const onSuccess = (e: any) => {
    console.log('Login successful:', e.detail.user);
    navigate('/profile');
  };

  const onError = (e: any) => {
    console.error('Login error:', e.detail.error);
  };

  // If user is authenticated, show welcome message
  if (isAuthenticated) {
    return (
      <Container component="main" maxWidth="sm">
        <Box
          sx={{
            marginTop: 8,
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            minHeight: '100vh',
          }}
        >
          <Paper 
            elevation={3} 
            sx={{ 
              padding: 4, 
              width: '100%', 
              textAlign: 'center',
              background: 'rgba(51, 65, 85, 0.95)',
              backdropFilter: 'blur(10px)',
              border: '1px solid rgba(255, 255, 255, 0.15)',
              borderRadius: 3,
            }}
          >
            <Typography 
              variant="h3" 
              component="h1" 
              sx={{ 
                fontWeight: 'bold', 
                mb: 2,
                background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                WebkitBackgroundClip: 'text',
                WebkitTextFillColor: 'transparent',
                backgroundClip: 'text',
              }}
            >
              🚀 Nexora AI
            </Typography>
            <Typography 
              variant="h5" 
              sx={{ 
                mb: 3,
                color: '#f1f5f9',
                fontWeight: 500
              }}
            >
              Welcome {user?.name || user?.email || 'User'}!
            </Typography>
            <Button 
              variant="contained" 
              onClick={() => navigate('/')}
              sx={{ 
                mr: 2,
                background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                '&:hover': {
                  background: 'linear-gradient(135deg, #5a67d8 0%, #6b46c1 100%)',
                }
              }}
            >
              Go to Dashboard
            </Button>
            <Button 
              variant="outlined" 
              onClick={() => logout()}
              sx={{
                borderColor: 'rgba(255, 255, 255, 0.3)',
                color: '#ffffff',
                '&:hover': {
                  borderColor: 'rgba(255, 255, 255, 0.5)',
                  background: 'rgba(255, 255, 255, 0.1)',
                }
              }}
            >
              Logout
            </Button>
          </Paper>
        </Box>
      </Container>
    );
  }

  // If not authenticated, show the Descope login widget
  return (
    <Container component="main" maxWidth="sm">
      <Box
        sx={{
          marginTop: 8,
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          minHeight: '100vh',
        }}
      >
        <Paper 
          elevation={3} 
          sx={{ 
            padding: 4, 
            width: '100%',
            background: 'rgba(51, 65, 85, 0.95)',
            backdropFilter: 'blur(10px)',
            border: '1px solid rgba(255, 255, 255, 0.15)',
            borderRadius: 3,
          }}
        >
          <Box sx={{ textAlign: 'center', mb: 3 }}>
            <Typography 
              variant="h3" 
              component="h1" 
              sx={{ 
                fontWeight: 'bold', 
                mb: 1,
                background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                WebkitBackgroundClip: 'text',
                WebkitTextFillColor: 'transparent',
                backgroundClip: 'text',
              }}
            >
              🚀 Nexora AI
            </Typography>
            <Typography 
              variant="h5" 
              sx={{ 
                color: '#f1f5f9',
                fontWeight: 500
              }}
            >
              Sign in to your account
            </Typography>
          </Box>

          {/* Descope SignUpOrInFlow component */}
          <SignUpOrInFlow
            onSuccess={onSuccess}
            onError={onError}
          />
        </Paper>
      </Box>
    </Container>
  );
};

export default Login;