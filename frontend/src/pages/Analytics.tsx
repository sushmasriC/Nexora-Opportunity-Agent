import React, { useState, useEffect } from 'react';
import {
  Grid,
  Card,
  CardContent,
  Typography,
  Box,
  LinearProgress,
  Alert,
  Chip,
  CircularProgress,
} from '@mui/material';
import {
  Email,
  Visibility,
  Send,
  Star,
  Assessment,
} from '@mui/icons-material';
import { analyticsAPI } from '../services/api';

// Circular Progress Component
const CircularProgressWithLabel: React.FC<{
  value: number;
  size?: number;
  color?: string;
  label?: string;
  subtitle?: string;
}> = ({ value, size = 120, color = '#6366f1', label, subtitle }) => {
  const [displayValue, setDisplayValue] = useState(0);
  
  useEffect(() => {
    const timer = setTimeout(() => {
      setDisplayValue(value);
    }, 500);
    return () => clearTimeout(timer);
  }, [value]);

  return (
    <Box sx={{ position: 'relative', display: 'inline-flex', alignItems: 'center', justifyContent: 'center' }}>
      <CircularProgress
        variant="determinate"
        value={displayValue}
        size={size}
        thickness={4}
        sx={{
          color: color,
          '& .MuiCircularProgress-circle': {
            strokeLinecap: 'round',
          },
        }}
      />
      <Box
        sx={{
          top: 0,
          left: 0,
          bottom: 0,
          right: 0,
          position: 'absolute',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          flexDirection: 'column',
        }}
      >
        <Typography variant="h4" component="div" sx={{ fontWeight: 700, color: '#ffffff' }}>
          {`${Math.round(displayValue)}%`}
        </Typography>
        {label && (
          <Typography variant="body2" sx={{ color: '#cbd5e1', fontWeight: 500 }}>
            {label}
          </Typography>
        )}
        {subtitle && (
          <Typography variant="caption" sx={{ color: '#94a3b8', fontSize: '0.75rem' }}>
            {subtitle}
          </Typography>
        )}
      </Box>
    </Box>
  );
};

const Analytics: React.FC = () => {
  const [analytics, setAnalytics] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const fetchAnalytics = async () => {
    try {
      setLoading(true);
      const data = await analyticsAPI.getAnalytics();
      setAnalytics(data);
    } catch (err: any) {
      setError('Failed to load analytics');
      console.error('Analytics error:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAnalytics();
  }, []);

  if (loading) {
    return (
      <Box sx={{ width: '100%', mt: 2 }}>
        <LinearProgress />
        <Typography variant="h6" sx={{ mt: 2, textAlign: 'center' }}>
          Loading your analytics...
        </Typography>
      </Box>
    );
  }

  if (error) {
    return (
      <Alert severity="error" sx={{ mb: 2 }}>
        {error}
      </Alert>
    );
  }

  const StatCard: React.FC<{
    title: string;
    value: number | string;
    icon: React.ReactNode;
    color: string;
    subtitle?: string;
    delay?: number;
  }> = ({ title, value, icon, color, subtitle, delay = 0 }) => (
    <Card 
      className="hover-lift animate-fade-in-up"
      sx={{ 
        animationDelay: `${delay}s`,
        background: 'rgba(51, 65, 85, 0.95)',
        backdropFilter: 'blur(10px)',
        border: '1px solid rgba(255, 255, 255, 0.15)',
        position: 'relative',
        overflow: 'hidden',
        '&::before': {
          content: '""',
          position: 'absolute',
          top: 0,
          left: 0,
          right: 0,
          height: '4px',
          background: color,
        },
        '&:hover': {
          transform: 'translateY(-4px) scale(1.02)',
          boxShadow: '0 12px 40px rgba(0,0,0,0.7)',
          background: 'rgba(51, 65, 85, 1)',
        }
      }}
    >
      <CardContent sx={{ p: 3 }}>
        <Box sx={{ display: 'flex', alignItems: 'center' }}>
          <Box
            sx={{
              p: 2.5,
              borderRadius: 3,
              background: color,
              color: 'white',
              mr: 2,
              boxShadow: `0 4px 15px ${color}40`,
              transition: 'all 0.3s ease',
              '&:hover': {
                transform: 'scale(1.1) rotate(5deg)',
                boxShadow: `0 6px 20px ${color}60`,
              }
            }}
          >
            {icon}
          </Box>
          <Box>
            <Typography 
              sx={{ 
                color: '#f1f5f9',
                fontWeight: 600,
                mb: 0.5
              }} 
              gutterBottom
            >
              {title}
            </Typography>
            <Typography 
              variant="h4" 
              component="div"
              className="animate-count-up"
              sx={{ 
                fontWeight: 800,
                color: '#ffffff',
                textShadow: '0 2px 8px rgba(0,0,0,0.8)'
              }}
            >
              {value}
            </Typography>
            {subtitle && (
              <Typography 
                variant="body2" 
                sx={{ 
                  color: '#cbd5e1',
                  fontWeight: 500
                }}
              >
                {subtitle}
              </Typography>
            )}
          </Box>
        </Box>
      </CardContent>
    </Card>
  );

  return (
    <Box>
      <Box sx={{ mb: 4 }} className="animate-fade-in-up">
        <Typography 
          variant="h4" 
          component="h1" 
          gutterBottom
          sx={{
            background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent',
            backgroundClip: 'text',
            fontWeight: 700,
            mb: 2
          }}
        >
          Your Analytics
        </Typography>
        <Typography 
          variant="subtitle1" 
          sx={{ 
            color: '#f1f5f9',
            fontSize: '1.1rem',
            fontWeight: 500
          }}
        >
          Insights into your job search and recommendations
        </Typography>
      </Box>


      <Grid container spacing={3}>
        {/* Engagement Stats */}
        <Grid item xs={12} md={6}>
          <Card 
            className="hover-lift animate-fade-in-up"
            sx={{ 
              animationDelay: '0.5s',
              background: 'rgba(51, 65, 85, 0.95)',
              backdropFilter: 'blur(10px)',
              border: '1px solid rgba(255, 255, 255, 0.15)',
              '&:hover': {
                transform: 'translateY(-4px)',
                boxShadow: '0 12px 40px rgba(0,0,0,0.7)',
                background: 'rgba(51, 65, 85, 1)',
              }
            }}
          >
            <CardContent sx={{ p: 3 }}>
              <Typography 
                variant="h6" 
                gutterBottom
                sx={{
                  background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                  WebkitBackgroundClip: 'text',
                  WebkitTextFillColor: 'transparent',
                  backgroundClip: 'text',
                  fontWeight: 700,
                  mb: 3
                }}
              >
                Engagement Statistics
              </Typography>
              <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 3 }}>
                  <CircularProgressWithLabel
                    value={25}
                    size={80}
                    color="#3b82f6"
                    label="Viewed"
                  />
                  <Box>
                    <Typography variant="h6" sx={{ fontWeight: 600, color: '#ffffff' }}>
                      Viewed Recommendations
                    </Typography>
                    <Typography variant="body2" sx={{ color: '#cbd5e1' }}>
                      1 out of 3
                    </Typography>
                  </Box>
                </Box>
                
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 3 }}>
                  <CircularProgressWithLabel
                    value={0}
                    size={80}
                    color="#10b981"
                    label="Applied"
                  />
                  <Box>
                    <Typography variant="h6" sx={{ fontWeight: 600, color: '#ffffff' }}>
                      Applied to Opportunities
                    </Typography>
                    <Typography variant="body2" sx={{ color: '#cbd5e1' }}>
                      {analytics?.applied_recommendations || 0} applications
                    </Typography>
                  </Box>
                </Box>

                <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, p: 2, background: 'rgba(99, 102, 241, 0.05)', borderRadius: 2 }}>
                  <Box sx={{ p: 1.5, background: 'linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%)', borderRadius: 2, color: 'white' }}>
                    <Email />
                  </Box>
                  <Box>
                    <Typography variant="h6" sx={{ fontWeight: 600, color: '#ffffff' }}>
                      Email Notifications
                    </Typography>
                    <Typography variant="body2" sx={{ color: '#cbd5e1' }}>
                      {analytics?.emails_sent || 0} sent
                    </Typography>
                  </Box>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {/* Top Skills */}
        <Grid item xs={12} md={6}>
          <Card 
            className="hover-lift animate-fade-in-up"
            sx={{ 
              animationDelay: '0.6s',
              background: 'rgba(51, 65, 85, 0.95)',
              backdropFilter: 'blur(10px)',
              border: '1px solid rgba(255, 255, 255, 0.15)',
              '&:hover': {
                transform: 'translateY(-4px)',
                boxShadow: '0 12px 40px rgba(0,0,0,0.7)',
                background: 'rgba(51, 65, 85, 1)',
              }
            }}
          >
            <CardContent sx={{ p: 3 }}>
              <Typography 
                variant="h6" 
                gutterBottom
                sx={{
                  background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                  WebkitBackgroundClip: 'text',
                  WebkitTextFillColor: 'transparent',
                  backgroundClip: 'text',
                  fontWeight: 700,
                  mb: 3
                }}
              >
                Most Matched Skills
              </Typography>
              <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1.5 }}>
                {[
                  { name: 'Python' },
                  { name: 'AI' },
                  { name: 'ML' }
                ].map((skill: any, index: number) => (
                  <Chip
                    key={skill.name}
                    label={skill.name}
                    sx={{
                      background: index < 3 
                        ? 'linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%)'
                        : 'rgba(99, 102, 241, 0.1)',
                      color: index < 3 ? 'white' : '#6366f1',
                      border: index < 3 ? 'none' : '1px solid rgba(99, 102, 241, 0.3)',
                      fontWeight: 600,
                      boxShadow: index < 3 ? '0 4px 15px rgba(99, 102, 241, 0.3)' : 'none',
                      transition: 'all 0.3s ease',
                      '&:hover': {
                        transform: 'scale(1.05)',
                        boxShadow: index < 3 
                          ? '0 6px 20px rgba(99, 102, 241, 0.4)'
                          : '0 4px 15px rgba(99, 102, 241, 0.2)',
                      }
                    }}
                    icon={index < 3 ? <Star sx={{ color: 'white' }} /> : undefined}
                  />
                ))}
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {/* Match Quality */}
        <Grid item xs={12} md={6}>
          <Card 
            className="hover-lift animate-fade-in-up"
            sx={{ 
              animationDelay: '0.7s',
              background: 'rgba(51, 65, 85, 0.95)',
              backdropFilter: 'blur(10px)',
              border: '1px solid rgba(255, 255, 255, 0.15)',
              '&:hover': {
                transform: 'translateY(-4px)',
                boxShadow: '0 12px 40px rgba(0,0,0,0.7)',
                background: 'rgba(51, 65, 85, 1)',
              }
            }}
          >
            <CardContent sx={{ p: 3 }}>
              <Typography 
                variant="h6" 
                gutterBottom
                sx={{
                  background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                  WebkitBackgroundClip: 'text',
                  WebkitTextFillColor: 'transparent',
                  backgroundClip: 'text',
                  fontWeight: 700,
                  mb: 3
                }}
              >
                Match Quality Distribution
              </Typography>
              <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                <Box sx={{ 
                  display: 'flex', 
                  alignItems: 'center', 
                  justifyContent: 'space-between',
                  p: 2,
                  background: 'linear-gradient(135deg, rgba(16, 185, 129, 0.05) 0%, rgba(52, 211, 153, 0.05) 100%)',
                  borderRadius: 2,
                  border: '1px solid rgba(16, 185, 129, 0.2)'
                }}>
                  <Box>
                    <Typography variant="h6" sx={{ fontWeight: 600, color: '#ffffff' }}>
                      High Quality Matches (80%+)
                    </Typography>
                    <Typography variant="body2" sx={{ color: '#cbd5e1' }}>
                      {analytics?.high_quality_matches || 0} recommendations
                    </Typography>
                  </Box>
                  <Chip 
                    label="Excellent" 
                    sx={{
                      background: 'linear-gradient(135deg, #10b981 0%, #34d399 100%)',
                      color: 'white',
                      fontWeight: 600,
                      boxShadow: '0 2px 8px rgba(16, 185, 129, 0.3)'
                    }}
                    size="small" 
                  />
                </Box>
                
                <Box sx={{ 
                  display: 'flex', 
                  alignItems: 'center', 
                  justifyContent: 'space-between',
                  p: 2,
                  background: 'linear-gradient(135deg, rgba(245, 158, 11, 0.05) 0%, rgba(251, 191, 36, 0.05) 100%)',
                  borderRadius: 2,
                  border: '1px solid rgba(245, 158, 11, 0.2)'
                }}>
                  <Box>
                    <Typography variant="h6" sx={{ fontWeight: 600, color: '#ffffff' }}>
                      Good Matches (60-79%)
                    </Typography>
                    <Typography variant="body2" sx={{ color: '#cbd5e1' }}>
                      {analytics?.good_matches || 0} recommendations
                    </Typography>
                  </Box>
                  <Chip 
                    label="Good" 
                    sx={{
                      background: 'linear-gradient(135deg, #f59e0b 0%, #fbbf24 100%)',
                      color: 'white',
                      fontWeight: 600,
                      boxShadow: '0 2px 8px rgba(245, 158, 11, 0.3)'
                    }}
                    size="small" 
                  />
                </Box>
                
                <Box sx={{ 
                  display: 'flex', 
                  alignItems: 'center', 
                  justifyContent: 'space-between',
                  p: 2,
                  background: 'linear-gradient(135deg, rgba(59, 130, 246, 0.05) 0%, rgba(96, 165, 250, 0.05) 100%)',
                  borderRadius: 2,
                  border: '1px solid rgba(59, 130, 246, 0.2)'
                }}>
                  <Box>
                    <Typography variant="h6" sx={{ fontWeight: 600, color: '#ffffff' }}>
                      Fair Matches (40-59%)
                    </Typography>
                    <Typography variant="body2" sx={{ color: '#cbd5e1' }}>
                      {analytics?.fair_matches || 0} recommendations
                    </Typography>
                  </Box>
                  <Chip 
                    label="Fair" 
                    sx={{
                      background: 'linear-gradient(135deg, #3b82f6 0%, #60a5fa 100%)',
                      color: 'white',
                      fontWeight: 600,
                      boxShadow: '0 2px 8px rgba(59, 130, 246, 0.3)'
                    }}
                    size="small" 
                  />
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {/* Recent Activity */}
        <Grid item xs={12} md={6}>
          <Card 
            className="hover-lift animate-fade-in-up"
            sx={{ 
              animationDelay: '0.8s',
              background: 'rgba(51, 65, 85, 0.95)',
              backdropFilter: 'blur(10px)',
              border: '1px solid rgba(255, 255, 255, 0.15)',
              '&:hover': {
                transform: 'translateY(-4px)',
                boxShadow: '0 12px 40px rgba(0,0,0,0.7)',
                background: 'rgba(51, 65, 85, 1)',
              }
            }}
          >
            <CardContent sx={{ p: 3 }}>
              <Typography 
                variant="h6" 
                gutterBottom
                sx={{
                  background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                  WebkitBackgroundClip: 'text',
                  WebkitTextFillColor: 'transparent',
                  backgroundClip: 'text',
                  fontWeight: 700,
                  mb: 3
                }}
              >
                Recent Activity
              </Typography>
              {analytics?.recent_activity && analytics.recent_activity.length > 0 ? (
                <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                  {analytics.recent_activity.map((activity: any, index: number) => (
                    <Box 
                      key={index}
                      sx={{ 
                        display: 'flex', 
                        alignItems: 'center', 
                        gap: 2,
                        p: 2,
                        background: 'rgba(99, 102, 241, 0.05)',
                        borderRadius: 2,
                        border: '1px solid rgba(99, 102, 241, 0.1)',
                        transition: 'all 0.3s ease',
                        '&:hover': {
                          background: 'rgba(99, 102, 241, 0.1)',
                          transform: 'translateX(4px)',
                        }
                      }}
                    >
                      <Box sx={{ 
                        p: 1.5, 
                        borderRadius: 2,
                        background: activity.type === 'view' 
                          ? 'linear-gradient(135deg, #3b82f6 0%, #60a5fa 100%)'
                          : activity.type === 'apply'
                          ? 'linear-gradient(135deg, #10b981 0%, #34d399 100%)'
                          : 'linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%)',
                        color: 'white',
                        boxShadow: '0 2px 8px rgba(0,0,0,0.1)'
                      }}>
                        {activity.type === 'view' && <Visibility />}
                        {activity.type === 'apply' && <Send />}
                        {activity.type === 'recommendation' && <Star />}
                      </Box>
                      <Box>
                        <Typography variant="body1" sx={{ fontWeight: 600, color: '#ffffff' }}>
                          {activity.description}
                        </Typography>
                        <Typography variant="body2" sx={{ color: '#cbd5e1' }}>
                          {new Date(activity.timestamp).toLocaleDateString()}
                        </Typography>
                      </Box>
                    </Box>
                  ))}
                </Box>
              ) : (
                <Typography 
                  sx={{ 
                    color: '#94a3b8',
                    fontStyle: 'italic',
                    textAlign: 'center',
                    py: 2
                  }}
                >
                  No recent activity
                </Typography>
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* Profile Completeness */}
        <Grid item xs={12}>
          <Card 
            className="hover-lift animate-fade-in-up"
            sx={{ 
              animationDelay: '0.9s',
              background: 'rgba(51, 65, 85, 0.95)',
              backdropFilter: 'blur(10px)',
              border: '1px solid rgba(255, 255, 255, 0.15)',
              '&:hover': {
                transform: 'translateY(-4px)',
                boxShadow: '0 12px 40px rgba(0,0,0,0.7)',
                background: 'rgba(51, 65, 85, 1)',
              }
            }}
          >
            <CardContent sx={{ p: 3 }}>
              <Typography 
                variant="h6" 
                gutterBottom
                sx={{
                  background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                  WebkitBackgroundClip: 'text',
                  WebkitTextFillColor: 'transparent',
                  backgroundClip: 'text',
                  fontWeight: 700,
                  mb: 3
                }}
              >
                Profile Completeness
              </Typography>
              
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 4, mb: 4 }}>
                <CircularProgressWithLabel
                  value={100}
                  size={120}
                  color="linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%)"
                  label="Overall"
                  subtitle="Profile Complete"
                />
                <Box>
                  <Typography variant="h5" sx={{ fontWeight: 700, color: '#ffffff', mb: 1 }}>
                    Profile Status
                  </Typography>
                  <Typography variant="body1" sx={{ color: '#cbd5e1', mb: 2 }}>
                    Complete your profile to get better recommendations
                  </Typography>
                  <Box sx={{ 
                    display: 'flex', 
                    alignItems: 'center', 
                    gap: 1,
                    p: 2,
                    background: 'rgba(99, 102, 241, 0.05)',
                    borderRadius: 2,
                    border: '1px solid rgba(99, 102, 241, 0.1)'
                  }}>
                    <Assessment sx={{ color: '#6366f1' }} />
                    <Typography variant="body2" sx={{ color: '#ffffff', fontWeight: 500 }}>
                      100% Complete
                    </Typography>
                  </Box>
                </Box>
              </Box>

              <Grid container spacing={3}>
                <Grid item xs={12} sm={6} md={3}>
                  <Box sx={{ 
                    textAlign: 'center', 
                    p: 2,
                    background: 'linear-gradient(135deg, rgba(99, 102, 241, 0.05) 0%, rgba(139, 92, 246, 0.05) 100%)',
                    borderRadius: 2,
                    border: '1px solid rgba(99, 102, 241, 0.1)',
                    transition: 'all 0.3s ease',
                    '&:hover': {
                      transform: 'translateY(-2px)',
                      boxShadow: '0 8px 25px rgba(99, 102, 241, 0.1)',
                    }
                  }}>
                    <Typography 
                      variant="h4" 
                      className="animate-count-up"
                      sx={{ 
                        fontWeight: 700,
                        background: 'linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%)',
                        WebkitBackgroundClip: 'text',
                        WebkitTextFillColor: 'transparent',
                        backgroundClip: 'text',
                        mb: 1
                      }}
                    >
                      {analytics?.skills_count || 5}
                    </Typography>
                    <Typography variant="body2" sx={{ color: '#cbd5e1', fontWeight: 500 }}>
                      Skills
                    </Typography>
                  </Box>
                </Grid>
                <Grid item xs={12} sm={6} md={3}>
                  <Box sx={{ 
                    textAlign: 'center', 
                    p: 2,
                    background: 'linear-gradient(135deg, rgba(236, 72, 153, 0.05) 0%, rgba(244, 114, 182, 0.05) 100%)',
                    borderRadius: 2,
                    border: '1px solid rgba(236, 72, 153, 0.1)',
                    transition: 'all 0.3s ease',
                    '&:hover': {
                      transform: 'translateY(-2px)',
                      boxShadow: '0 8px 25px rgba(236, 72, 153, 0.1)',
                    }
                  }}>
                    <Typography 
                      variant="h4" 
                      className="animate-count-up"
                      sx={{ 
                        fontWeight: 700,
                        background: 'linear-gradient(135deg, #ec4899 0%, #f472b6 100%)',
                        WebkitBackgroundClip: 'text',
                        WebkitTextFillColor: 'transparent',
                        backgroundClip: 'text',
                        mb: 1
                      }}
                    >
                      {analytics?.interests_count || 3}
                    </Typography>
                    <Typography variant="body2" sx={{ color: '#cbd5e1', fontWeight: 500 }}>
                      Interests
                    </Typography>
                  </Box>
                </Grid>
                <Grid item xs={12} sm={6} md={3}>
                  <Box sx={{ 
                    textAlign: 'center', 
                    p: 2,
                    background: 'linear-gradient(135deg, rgba(59, 130, 246, 0.05) 0%, rgba(96, 165, 250, 0.05) 100%)',
                    borderRadius: 2,
                    border: '1px solid rgba(59, 130, 246, 0.1)',
                    transition: 'all 0.3s ease',
                    '&:hover': {
                      transform: 'translateY(-2px)',
                      boxShadow: '0 8px 25px rgba(59, 130, 246, 0.1)',
                    }
                  }}>
                    <Typography 
                      variant="h4" 
                      className="animate-count-up"
                      sx={{ 
                        fontWeight: 700,
                        background: 'linear-gradient(135deg, #3b82f6 0%, #60a5fa 100%)',
                        WebkitBackgroundClip: 'text',
                        WebkitTextFillColor: 'transparent',
                        backgroundClip: 'text',
                        mb: 1
                      }}
                    >
                      {analytics?.locations_count || "India"}
                    </Typography>
                    <Typography variant="body2" sx={{ color: '#cbd5e1', fontWeight: 500 }}>
                      Locations
                    </Typography>
                  </Box>
                </Grid>
                <Grid item xs={12} sm={6} md={3}>
                  <Box sx={{ 
                    textAlign: 'center', 
                    p: 2,
                    background: 'linear-gradient(135deg, rgba(16, 185, 129, 0.05) 0%, rgba(52, 211, 153, 0.05) 100%)',
                    borderRadius: 2,
                    border: '1px solid rgba(16, 185, 129, 0.1)',
                    transition: 'all 0.3s ease',
                    '&:hover': {
                      transform: 'translateY(-2px)',
                      boxShadow: '0 8px 25px rgba(16, 185, 129, 0.1)',
                    }
                  }}>
                    <Typography 
                      variant="h4" 
                      className="animate-count-up"
                      sx={{ 
                        fontWeight: 700,
                        background: 'linear-gradient(135deg, #10b981 0%, #34d399 100%)',
                        WebkitBackgroundClip: 'text',
                        WebkitTextFillColor: 'transparent',
                        backgroundClip: 'text',
                        mb: 1
                      }}
                    >
                      {analytics?.resumes_count || 1}
                    </Typography>
                    <Typography variant="body2" sx={{ color: '#cbd5e1', fontWeight: 500 }}>
                      Resumes
                    </Typography>
                  </Box>
                </Grid>
              </Grid>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
};

export default Analytics;
