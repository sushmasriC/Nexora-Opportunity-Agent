import React, { useState } from 'react';
import {
  AppBar,
  Toolbar,
  Typography,
  IconButton,
  Drawer,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Box,
  Avatar,
  Menu,
  MenuItem,
  Divider,
} from '@mui/material';
import {
  Menu as MenuIcon,
  Dashboard as DashboardIcon,
  Person as PersonIcon,
  Recommend as RecommendIcon,
  Analytics as AnalyticsIcon,
  Logout as LogoutIcon,
  AccountCircle as AccountCircleIcon,
} from '@mui/icons-material';
import { useNavigate, useLocation } from 'react-router-dom';
import { useDescope, useUser } from '@descope/react-sdk';

interface LayoutProps {
  children: React.ReactNode;
}

const drawerWidth = 240;

const Layout: React.FC<LayoutProps> = ({ children }) => {
  const [mobileOpen, setMobileOpen] = useState(false);
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
  const { logout } = useDescope();
  const { user } = useUser();
  const navigate = useNavigate();
  const location = useLocation();

  const handleDrawerToggle = () => {
    setMobileOpen(!mobileOpen);
  };

  const handleProfileMenuOpen = (event: React.MouseEvent<HTMLElement>) => {
    setAnchorEl(event.currentTarget);
  };

  const handleProfileMenuClose = () => {
    setAnchorEl(null);
  };

  const handleLogout = async () => {
    handleProfileMenuClose();
    try {
      await logout();
      navigate('/login');
    } catch (error) {
      console.error('Logout error:', error);
      navigate('/login');
    }
  };

  const menuItems = [
    { text: 'Profile', icon: <PersonIcon />, path: '/profile' },
    { text: 'Dashboard', icon: <DashboardIcon />, path: '/dashboard' },
    { text: 'Recommendations', icon: <RecommendIcon />, path: '/recommendations' },
    { text: 'Analytics', icon: <AnalyticsIcon />, path: '/analytics' },
  ];

  const drawer = (
    <div>
      <Toolbar sx={{ 
        background: 'linear-gradient(135deg, #1e293b 0%, #334155 100%)',
        color: 'white',
        position: 'relative',
        overflow: 'hidden',
        borderBottom: '1px solid rgba(96, 165, 250, 0.2)',
        boxShadow: '0 2px 10px rgba(0, 0, 0, 0.2)'
      }}>
        <Box sx={{ 
          position: 'absolute',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          background: 'url("data:image/svg+xml,%3Csvg width="60" height="60" viewBox="0 0 60 60" xmlns="http://www.w3.org/2000/svg"%3E%3Cg fill="none" fill-rule="evenodd"%3E%3Cg fill="%2360a5fa" fill-opacity="0.15"%3E%3Ccircle cx="30" cy="30" r="2"/%3E%3C/g%3E%3C/g%3E%3C/svg%3E")',
          opacity: 0.4
        }} />
        <Typography 
          variant="h6" 
          noWrap 
          component="div" 
          sx={{ 
            fontWeight: 800,
            fontSize: '1.5rem',
            zIndex: 1,
            position: 'relative',
            background: 'linear-gradient(45deg, #ffffff 0%, #60a5fa 100%)',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent',
            backgroundClip: 'text',
            textShadow: '0 0 20px rgba(96, 165, 250, 0.3)'
          }}
        >
          🚀 Nexora AI
        </Typography>
      </Toolbar>
      <Divider sx={{ borderColor: 'rgba(96, 165, 250, 0.2)' }} />
      <List sx={{ px: 1, py: 2 }}>
        {menuItems.map((item, index) => (
          <ListItem
            key={item.text}
            onClick={() => {
              navigate(item.path);
              setMobileOpen(false);
            }}
            selected={location.pathname === item.path}
            sx={{
              cursor: 'pointer',
              mb: 0.5,
              borderRadius: 2,
              transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
              animation: `slideInLeft 0.6s ease-out ${index * 0.1}s both`,
              '&:hover': {
                background: 'rgba(96, 165, 250, 0.1)',
                transform: 'translateX(8px)',
                borderLeft: '3px solid #60a5fa',
                '& .MuiListItemIcon-root': {
                  color: '#60a5fa',
                  transform: 'scale(1.1)',
                },
                '& .MuiListItemText-primary': {
                  color: '#ffffff',
                  fontWeight: 600,
                },
              },
              '&.Mui-selected': {
                background: 'linear-gradient(135deg, #1e40af 0%, #3b82f6 100%)',
                color: 'white',
                boxShadow: '0 4px 15px rgba(59, 130, 246, 0.4)',
                borderLeft: '3px solid #60a5fa',
                '& .MuiListItemIcon-root': {
                  color: 'white',
                  transform: 'scale(1.1)',
                },
                '& .MuiListItemText-primary': {
                  color: 'white',
                  fontWeight: 600,
                },
                '&:hover': {
                  background: 'linear-gradient(135deg, #1d4ed8 0%, #2563eb 100%)',
                  transform: 'translateX(8px) scale(1.02)',
                },
              },
            }}
          >
            <ListItemIcon sx={{ 
              color: 'rgba(203, 213, 225, 0.8)',
              transition: 'all 0.3s ease',
              minWidth: 40
            }}>
              {item.icon}
            </ListItemIcon>
            <ListItemText 
              primary={item.text} 
              sx={{
                '& .MuiListItemText-primary': {
                  color: 'rgba(241, 245, 249, 0.9)',
                  fontWeight: 500,
                  transition: 'all 0.3s ease',
                }
              }}
            />
          </ListItem>
        ))}
      </List>
    </div>
  );

  return (
    <Box sx={{ display: 'flex' }}>
      <AppBar
        position="fixed"
        sx={{
          width: { sm: `calc(100% - ${drawerWidth}px)` },
          ml: { sm: `${drawerWidth}px` },
          background: 'rgba(15, 23, 42, 0.95)',
          backdropFilter: 'blur(20px)',
          boxShadow: '0 4px 20px rgba(0,0,0,0.3)',
          borderBottom: '1px solid rgba(96, 165, 250, 0.2)',
        }}
      >
        <Toolbar sx={{ py: 1 }}>
          <IconButton
            color="inherit"
            aria-label="open drawer"
            edge="start"
            onClick={handleDrawerToggle}
            sx={{ 
              mr: 2, 
              display: { sm: 'none' },
              color: '#f1f5f9',
              '&:hover': {
                background: 'rgba(96, 165, 250, 0.1)',
                transform: 'scale(1.1)',
              },
              transition: 'all 0.3s ease'
            }}
          >
            <MenuIcon />
          </IconButton>
          <Typography 
            variant="h6" 
            noWrap 
            component="div" 
            sx={{ 
              flexGrow: 1,
              color: '#f1f5f9',
              fontWeight: 600,
              background: 'linear-gradient(135deg, #60a5fa 0%, #3b82f6 100%)',
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent',
              backgroundClip: 'text',
              textShadow: '0 0 20px rgba(96, 165, 250, 0.3)'
            }}
          >
            AI-Powered Opportunity Finder
          </Typography>
          <IconButton
            size="large"
            edge="end"
            aria-label="account of current user"
            aria-controls="primary-search-account-menu"
            aria-haspopup="true"
            onClick={handleProfileMenuOpen}
            sx={{
              color: '#f1f5f9',
              '&:hover': {
                background: 'rgba(96, 165, 250, 0.1)',
                transform: 'scale(1.1)',
              },
              transition: 'all 0.3s ease'
            }}
          >
            <Avatar sx={{ 
              width: 36, 
              height: 36,
              background: 'linear-gradient(135deg, #3b82f6 0%, #60a5fa 100%)',
              fontWeight: 600,
              fontSize: '1rem',
              boxShadow: '0 4px 15px rgba(59, 130, 246, 0.3)',
              transition: 'all 0.3s ease',
              '&:hover': {
                transform: 'scale(1.1)',
                boxShadow: '0 6px 20px rgba(59, 130, 246, 0.4)',
              }
            }}>
              {user?.name?.charAt(0).toUpperCase() || user?.email?.charAt(0).toUpperCase() || 'U'}
            </Avatar>
          </IconButton>
        </Toolbar>
      </AppBar>
      <Menu
        anchorEl={anchorEl}
        open={Boolean(anchorEl)}
        onClose={handleProfileMenuClose}
        onClick={handleProfileMenuClose}
        PaperProps={{
          elevation: 0,
          sx: {
            overflow: 'visible',
            filter: 'drop-shadow(0px 4px 20px rgba(0,0,0,0.5))',
            mt: 1.5,
            background: 'rgba(15, 23, 42, 0.95)',
            backdropFilter: 'blur(20px)',
            border: '1px solid rgba(96, 165, 250, 0.2)',
            borderRadius: 2,
            '& .MuiAvatar-root': {
              width: 32,
              height: 32,
              ml: -0.5,
              mr: 1,
            },
          },
        }}
        transformOrigin={{ horizontal: 'right', vertical: 'top' }}
        anchorOrigin={{ horizontal: 'right', vertical: 'bottom' }}
      >
        <MenuItem 
          onClick={() => navigate('/profile')}
          sx={{
            color: '#f1f5f9',
            '&:hover': {
              background: 'rgba(96, 165, 250, 0.1)',
            },
            '& .MuiListItemIcon-root': {
              color: '#cbd5e1',
            },
          }}
        >
          <ListItemIcon>
            <AccountCircleIcon fontSize="small" />
          </ListItemIcon>
          Profile
        </MenuItem>
        <Divider sx={{ borderColor: 'rgba(96, 165, 250, 0.2)' }} />
        <MenuItem 
          onClick={handleLogout}
          sx={{
            color: '#f1f5f9',
            '&:hover': {
              background: 'rgba(239, 68, 68, 0.1)',
            },
            '& .MuiListItemIcon-root': {
              color: '#cbd5e1',
            },
          }}
        >
          <ListItemIcon>
            <LogoutIcon fontSize="small" />
          </ListItemIcon>
          Logout
        </MenuItem>
      </Menu>
      <Box
        component="nav"
        sx={{ width: { sm: drawerWidth }, flexShrink: { sm: 0 } }}
        aria-label="mailbox folders"
      >
        <Drawer
          variant="temporary"
          open={mobileOpen}
          onClose={handleDrawerToggle}
          ModalProps={{
            keepMounted: true,
          }}
          sx={{
            display: { xs: 'block', sm: 'none' },
            '& .MuiDrawer-paper': { boxSizing: 'border-box', width: drawerWidth },
          }}
        >
          {drawer}
        </Drawer>
        <Drawer
          variant="permanent"
          sx={{
            display: { xs: 'none', sm: 'block' },
            '& .MuiDrawer-paper': { boxSizing: 'border-box', width: drawerWidth },
          }}
          open
        >
          {drawer}
        </Drawer>
      </Box>
      <Box
        component="main"
        sx={{
          flexGrow: 1,
          p: 3,
          width: { sm: `calc(100% - ${drawerWidth}px)` },
          minHeight: '100vh',
          position: 'relative',
        }}
      >
        <Toolbar />
        <Box 
          className="animate-fade-in"
          sx={{
            animation: 'fadeInUp 0.8s ease-out',
            '& > *': {
              animation: 'fadeInUp 0.8s ease-out',
            }
          }}
        >
          {children}
        </Box>
      </Box>
    </Box>
  );
};

export default Layout;
