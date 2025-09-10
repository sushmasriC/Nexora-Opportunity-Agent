import React from 'react';
import { Container, Paper, Typography, Box } from '@mui/material';
import { Descope } from '@descope/react-sdk';
import DescopeTest from '../components/DescopeTest';

const DescopeTestPage: React.FC = () => {
  const onSuccess = (e: any) => {
    console.log('Descope Success:', e);
  };

  const onError = (e: any) => {
    console.log('Descope Error:', e);
  };

  return (
    <Container component="main" maxWidth="md">
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
              🧪 Descope Test Page
            </Typography>
            <Typography variant="h5" color="text.secondary">
              Testing Descope Integration
            </Typography>
          </Box>

          <DescopeTest />

          <Box sx={{ mt: 4 }}>
            <Typography variant="h6" sx={{ mb: 2 }}>
              Descope Component Test:
            </Typography>
            <Descope
              flowId="sign-up-or-in"
              onSuccess={onSuccess}
              onError={onError}
            />
          </Box>
        </Paper>
      </Box>
    </Container>
  );
};

export default DescopeTestPage;
