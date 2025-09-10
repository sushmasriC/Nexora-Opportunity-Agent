import React from 'react';
import {
  Container,
  Paper,
  Typography,
  Box,
  Link,
} from '@mui/material';
import { useNavigate, Link as RouterLink } from 'react-router-dom';
import SimpleAuth from '../components/SimpleAuth';

const SimpleLogin: React.FC = () => {
  const navigate = useNavigate();

  const onSuccess = () => {
    navigate('/profile');
  };

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

          <SimpleAuth mode="login" onSuccess={onSuccess} />

          <Box sx={{ textAlign: 'center', mt: 2 }}>
            <Link 
              component={RouterLink} 
              to="/register" 
              variant="body2"
              sx={{
                color: '#60a5fa',
                textDecoration: 'none',
                '&:hover': {
                  color: '#93c5fd',
                  textDecoration: 'underline',
                }
              }}
            >
              Don't have an account? Sign Up
            </Link>
          </Box>
        </Paper>
      </Box>
    </Container>
  );
};

export default SimpleLogin;
