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

const SimpleRegister: React.FC = () => {
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
        }}
      >
        <Paper elevation={3} sx={{ padding: 4, width: '100%' }}>
          <Box sx={{ textAlign: 'center', mb: 3 }}>
            <Typography variant="h3" component="h1" sx={{ fontWeight: 'bold', mb: 1 }}>
              🚀 Nexora AI
            </Typography>
            <Typography variant="h5" color="text.secondary">
              Create your account
            </Typography>
          </Box>

          <SimpleAuth mode="register" onSuccess={onSuccess} />

          <Box sx={{ textAlign: 'center', mt: 2 }}>
            <Link component={RouterLink} to="/login" variant="body2">
              Already have an account? Sign In
            </Link>
          </Box>
        </Paper>
      </Box>
    </Container>
  );
};

export default SimpleRegister;
