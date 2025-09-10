import React, { useState, useEffect } from 'react';
import {
  Grid,
  Card,
  CardContent,
  Typography,
  Box,
  Button,
  Chip,
  Avatar,
  LinearProgress,
  Alert,
} from '@mui/material';
import {
  TrendingUp,
  Work,
  School,
  Code,
  Email,
  Refresh,
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import { useUser } from '@descope/react-sdk';
import { recommendationsAPI, analyticsAPI, SegregatedRecommendations } from '../services/api';

const Dashboard: React.FC = () => {
  const [recommendations, setRecommendations] = useState<SegregatedRecommendations | null>(null);
  const [analytics, setAnalytics] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const { user } = useUser();
  const navigate = useNavigate();

  const fetchData = async () => {
    try {
      setLoading(true);
      const [recsData, analyticsData] = await Promise.all([
        recommendationsAPI.getRecommendations(),
        analyticsAPI.getAnalytics(),
      ]);
      setRecommendations(recsData as SegregatedRecommendations);
      setAnalytics(analyticsData as any);
    } catch (err: any) {
      setError('Failed to load dashboard data');
      console.error('Dashboard error:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const getTypeIcon = (type: string) => {
    switch (type) {
      case 'job':
        return <Work />;
      case 'internship':
        return <School />;
      case 'hackathon':
        return <Code />;
      default:
        return <Work />;
    }
  };

  const getTypeColor = (type: string) => {
    switch (type) {
      case 'job':
        return 'primary';
      case 'internship':
        return 'secondary';
      case 'hackathon':
        return 'success';
      default:
        return 'default';
    }
  };

  if (loading) {
    return (
      <Box sx={{ width: '100%', mt: 2 }}>
        <LinearProgress />
        <Typography variant="h6" sx={{ mt: 2, textAlign: 'center' }}>
          Loading your personalized recommendations...
        </Typography>
      </Box>
    );
  }

  if (error) {
    return (
      <Alert severity="error" sx={{ mb: 2 }}>
        {error}
        <Button onClick={fetchData} sx={{ ml: 2 }}>
          <Refresh /> Retry
        </Button>
      </Alert>
    );
  }

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
          Welcome back, {user?.name || user?.email || 'User'}! 👋
        </Typography>
        <Typography 
          variant="subtitle1" 
          sx={{ 
            color: '#f8fafc',
            fontSize: '1.1rem',
            fontWeight: 500
          }}
        >
          Here are your personalized job and hackathon recommendations
        </Typography>
      </Box>

      {/* Analytics Cards */}
      {analytics && (
        <Grid container spacing={3} sx={{ mb: 4 }}>
          <Grid item xs={12} sm={6} md={3}>
            <Card 
              className="hover-lift animate-fade-in-up"
              sx={{ 
                animationDelay: '0.1s',
                '&::before': {
                  background: 'linear-gradient(135deg, rgba(99, 102, 241, 0.2) 0%, rgba(139, 92, 246, 0.2) 100%)',
                },
                '&:hover::before': {
                  background: 'linear-gradient(135deg, rgba(99, 102, 241, 0.3) 0%, rgba(139, 92, 246, 0.3) 100%)',
                }
              }}
            >
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center' }}>
                  <Avatar 
                    sx={{ 
                      background: 'linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%)',
                      mr: 2,
                      boxShadow: '0 4px 15px rgba(99, 102, 241, 0.3)',
                      transition: 'all 0.3s ease',
                      '&:hover': {
                        transform: 'scale(1.1) rotate(5deg)',
                      }
                    }}
                  >
                    <TrendingUp />
                  </Avatar>
                  <Box>
                    <Typography 
                      sx={{ 
                        color: '#f1f5f9',
                        fontWeight: 600,
                        mb: 0.5
                      }} 
                      gutterBottom
                    >
                      Total Matches
                    </Typography>
                    <Typography 
                      variant="h4" 
                      className="animate-count-up"
                      sx={{ 
                        fontWeight: 800,
                        color: '#ffffff',
                        textShadow: '0 2px 8px rgba(0,0,0,0.8)'
                      }}
                    >
                      3
                    </Typography>
                  </Box>
                </Box>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <Card 
              className="hover-lift animate-fade-in-up"
              sx={{ 
                animationDelay: '0.2s',
                '&::before': {
                  background: 'linear-gradient(135deg, rgba(16, 185, 129, 0.2) 0%, rgba(52, 211, 153, 0.2) 100%)',
                },
                '&:hover::before': {
                  background: 'linear-gradient(135deg, rgba(16, 185, 129, 0.3) 0%, rgba(52, 211, 153, 0.3) 100%)',
                }
              }}
            >
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center' }}>
                  <Avatar 
                    sx={{ 
                      background: 'linear-gradient(135deg, #10b981 0%, #34d399 100%)',
                      mr: 2,
                      boxShadow: '0 4px 15px rgba(16, 185, 129, 0.3)',
                      transition: 'all 0.3s ease',
                      '&:hover': {
                        transform: 'scale(1.1) rotate(-5deg)',
                      }
                    }}
                  >
                    <Work />
                  </Avatar>
                  <Box>
                    <Typography 
                      sx={{ 
                        color: '#f1f5f9',
                        fontWeight: 600,
                        mb: 0.5
                      }} 
                      gutterBottom
                    >
                      Job Matches
                    </Typography>
                    <Typography 
                      variant="h4" 
                      className="animate-count-up"
                      sx={{ 
                        fontWeight: 800,
                        color: '#ffffff',
                        textShadow: '0 2px 8px rgba(0,0,0,0.8)'
                      }}
                    >
                      {analytics.job_matches || 2}
                    </Typography>
                  </Box>
                </Box>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <Card 
              className="hover-lift animate-fade-in-up"
              sx={{ 
                animationDelay: '0.3s',
                '&::before': {
                  background: 'linear-gradient(135deg, rgba(236, 72, 153, 0.2) 0%, rgba(244, 114, 182, 0.2) 100%)',
                },
                '&:hover::before': {
                  background: 'linear-gradient(135deg, rgba(236, 72, 153, 0.3) 0%, rgba(244, 114, 182, 0.3) 100%)',
                }
              }}
            >
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center' }}>
                  <Avatar 
                    sx={{ 
                      background: 'linear-gradient(135deg, #ec4899 0%, #f472b6 100%)',
                      mr: 2,
                      boxShadow: '0 4px 15px rgba(236, 72, 153, 0.3)',
                      transition: 'all 0.3s ease',
                      '&:hover': {
                        transform: 'scale(1.1) rotate(5deg)',
                      }
                    }}
                  >
                    <School />
                  </Avatar>
                  <Box>
                    <Typography 
                      sx={{ 
                        color: '#f1f5f9',
                        fontWeight: 600,
                        mb: 0.5
                      }} 
                      gutterBottom
                    >
                      Internships
                    </Typography>
                    <Typography 
                      variant="h4" 
                      className="animate-count-up"
                      sx={{ 
                        fontWeight: 800,
                        color: '#ffffff',
                        textShadow: '0 2px 8px rgba(0,0,0,0.8)'
                      }}
                    >
                      {analytics.internship_matches || 0}
                    </Typography>
                  </Box>
                </Box>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <Card 
              className="hover-lift animate-fade-in-up"
              sx={{ 
                animationDelay: '0.4s',
                '&::before': {
                  background: 'linear-gradient(135deg, rgba(245, 158, 11, 0.2) 0%, rgba(251, 191, 36, 0.2) 100%)',
                },
                '&:hover::before': {
                  background: 'linear-gradient(135deg, rgba(245, 158, 11, 0.3) 0%, rgba(251, 191, 36, 0.3) 100%)',
                }
              }}
            >
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center' }}>
                  <Avatar 
                    sx={{ 
                      background: 'linear-gradient(135deg, #f59e0b 0%, #fbbf24 100%)',
                      mr: 2,
                      boxShadow: '0 4px 15px rgba(245, 158, 11, 0.3)',
                      transition: 'all 0.3s ease',
                      '&:hover': {
                        transform: 'scale(1.1) rotate(-5deg)',
                      }
                    }}
                  >
                    <Code />
                  </Avatar>
                  <Box>
                    <Typography 
                      sx={{ 
                        color: '#f1f5f9',
                        fontWeight: 600,
                        mb: 0.5
                      }} 
                      gutterBottom
                    >
                      Hackathons
                    </Typography>
                    <Typography 
                      variant="h4" 
                      className="animate-count-up"
                      sx={{ 
                        fontWeight: 800,
                        color: '#ffffff',
                        textShadow: '0 2px 8px rgba(0,0,0,0.8)'
                      }}
                    >
                      {analytics.hackathon_matches || 1}
                    </Typography>
                  </Box>
                </Box>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      )}

      {/* Best Matches */}
      {recommendations?.best_matches && recommendations.best_matches.length > 0 && (
        <Box sx={{ mb: 4 }} className="animate-fade-in-up">
          <Typography 
            variant="h5" 
            gutterBottom 
            sx={{ 
              display: 'flex', 
              alignItems: 'center',
              mb: 3,
              background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent',
              backgroundClip: 'text',
              fontWeight: 700
            }}
          >
            🎯 Best Suited for You
            <Chip
              label={`${recommendations.best_matches.length} matches`}
              sx={{ 
                ml: 2,
                background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                color: 'white',
                fontWeight: 600,
                boxShadow: '0 4px 15px rgba(102, 126, 234, 0.3)',
                animation: 'pulse 2s infinite'
              }}
              size="small"
            />
          </Typography>
          <Grid container spacing={3}>
            {recommendations.best_matches.slice(0, 6).map((rec, index) => (
              <Grid item xs={12} md={6} key={rec.id}>
                <Card 
                  className="hover-lift animate-fade-in-up"
                  sx={{ 
                    height: '100%', 
                    cursor: 'pointer',
                    animationDelay: `${0.5 + index * 0.1}s`,
                    position: 'relative',
                    overflow: 'hidden',
                    '&::before': {
                      content: '""',
                      position: 'absolute',
                      top: 0,
                      left: 0,
                      right: 0,
                      height: '4px',
                      background: `linear-gradient(90deg, ${getTypeColor(rec.opportunity.type) === 'primary' ? '#6366f1' : getTypeColor(rec.opportunity.type) === 'success' ? '#10b981' : getTypeColor(rec.opportunity.type) === 'secondary' ? '#ec4899' : '#f59e0b'} 0%, ${getTypeColor(rec.opportunity.type) === 'primary' ? '#8b5cf6' : getTypeColor(rec.opportunity.type) === 'success' ? '#34d399' : getTypeColor(rec.opportunity.type) === 'secondary' ? '#f472b6' : '#fbbf24'} 100%)`,
                    },
                    '&:hover': {
                      transform: 'translateY(-8px) scale(1.02)',
                      boxShadow: '0 20px 60px rgba(0, 0, 0, 0.4), 0 0 0 1px rgba(96, 165, 250, 0.3)',
                      '& .match-score': {
                        transform: 'scale(1.1)',
                      }
                    }
                  }} 
                  onClick={() => navigate('/recommendations')}
                >
                  <CardContent sx={{ p: 3 }}>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 2 }}>
                      <Typography 
                        variant="h6" 
                        component="h2" 
                        sx={{ 
                          fontWeight: 700,
                          color: '#ffffff',
                          lineHeight: 1.3,
                          flex: 1,
                          mr: 1
                        }}
                      >
                        {rec.opportunity.title}
                      </Typography>
                      <Chip
                        icon={getTypeIcon(rec.opportunity.type)}
                        label={rec.opportunity.type}
                        sx={{
                          background: getTypeColor(rec.opportunity.type) === 'primary' 
                            ? 'linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%)'
                            : getTypeColor(rec.opportunity.type) === 'success'
                            ? 'linear-gradient(135deg, #10b981 0%, #34d399 100%)'
                            : getTypeColor(rec.opportunity.type) === 'secondary'
                            ? 'linear-gradient(135deg, #ec4899 0%, #f472b6 100%)'
                            : 'linear-gradient(135deg, #f59e0b 0%, #fbbf24 100%)',
                          color: 'white',
                          fontWeight: 600,
                          boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
                          transition: 'all 0.3s ease',
                          '&:hover': {
                            transform: 'scale(1.05)',
                          }
                        }}
                        size="small"
                      />
                    </Box>
                    <Typography 
                      variant="subtitle1" 
                      sx={{ 
                        color: '#f1f5f9',
                        fontWeight: 600,
                        mb: 2
                      }} 
                      gutterBottom
                    >
                      {rec.opportunity.company} • {rec.opportunity.location}
                    </Typography>
                    <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5, mb: 2 }}>
                      {rec.opportunity.skills.slice(0, 3).map((skill) => (
                        <Chip 
                          key={skill} 
                          label={skill} 
                          size="small" 
                          variant="outlined"
                          sx={{
                            borderColor: 'rgba(96, 165, 250, 0.4)',
                            color: '#60a5fa',
                            background: 'rgba(96, 165, 250, 0.1)',
                            fontWeight: 500,
                            transition: 'all 0.2s ease',
                            '&:hover': {
                              background: 'rgba(96, 165, 250, 0.2)',
                              transform: 'scale(1.05)',
                            }
                          }}
                        />
                      ))}
                      {rec.opportunity.skills.length > 3 && (
                        <Chip 
                          label={`+${rec.opportunity.skills.length - 3}`} 
                          size="small" 
                          variant="outlined"
                          sx={{
                            borderColor: 'rgba(96, 165, 250, 0.4)',
                            color: '#60a5fa',
                            fontWeight: 500,
                            background: 'rgba(96, 165, 250, 0.1)',
                          }}
                        />
                      )}
                    </Box>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                      <Typography 
                        variant="body2" 
                        className="match-score"
                        sx={{ 
                          color: '#f1f5f9',
                          fontWeight: 600,
                          transition: 'all 0.3s ease'
                        }}
                      >
                        Match Score: <strong style={{ color: '#60a5fa', textShadow: '0 1px 3px rgba(0,0,0,0.8)' }}>{Math.round(rec.score * 100)}%</strong>
                      </Typography>
                      <Button 
                        size="small" 
                        variant="outlined"
                        sx={{
                          background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                          color: 'white',
                          border: 'none',
                          fontWeight: 600,
                          px: 2,
                          '&:hover': {
                            background: 'linear-gradient(135deg, #5a67d8 0%, #6b46c1 100%)',
                            transform: 'scale(1.05)',
                            boxShadow: '0 4px 15px rgba(102, 126, 234, 0.4)',
                          }
                        }}
                      >
                        View Details
                      </Button>
                    </Box>
                  </CardContent>
                </Card>
              </Grid>
            ))}
          </Grid>
          <Box sx={{ textAlign: 'center', mt: 3 }}>
            <Button variant="contained" onClick={() => navigate('/recommendations')}>
              View All Recommendations
            </Button>
          </Box>
        </Box>
      )}

      {/* Quick Actions */}
      <Card 
        className="animate-fade-in-up"
        sx={{ 
          animationDelay: '0.8s',
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
            Quick Actions
          </Typography>
          <Grid container spacing={2}>
            <Grid item xs={12} sm={6} md={3}>
              <Button
                fullWidth
                variant="outlined"
                startIcon={<Refresh />}
                onClick={fetchData}
                className="hover-lift"
                sx={{ 
                  py: 2,
                  background: 'rgba(99, 102, 241, 0.15)',
                  borderColor: 'rgba(99, 102, 241, 0.6)',
                  color: '#ffffff',
                  fontWeight: 700,
                  textShadow: '0 1px 3px rgba(0,0,0,0.8)',
                  '&:hover': {
                    background: 'rgba(99, 102, 241, 0.25)',
                    borderColor: '#60a5fa',
                    transform: 'translateY(-2px)',
                    boxShadow: '0 8px 25px rgba(96, 165, 250, 0.4)',
                    color: '#ffffff',
                  }
                }}
              >
                Refresh Recommendations
              </Button>
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <Button
                fullWidth
                variant="outlined"
                startIcon={<Email />}
                onClick={() => navigate('/profile')}
                className="hover-lift"
                sx={{ 
                  py: 2,
                  background: 'rgba(16, 185, 129, 0.15)',
                  borderColor: 'rgba(16, 185, 129, 0.6)',
                  color: '#ffffff',
                  fontWeight: 700,
                  textShadow: '0 1px 3px rgba(0,0,0,0.8)',
                  '&:hover': {
                    background: 'rgba(16, 185, 129, 0.25)',
                    borderColor: '#10b981',
                    transform: 'translateY(-2px)',
                    boxShadow: '0 8px 25px rgba(16, 185, 129, 0.4)',
                    color: '#ffffff',
                  }
                }}
              >
                Update Profile
              </Button>
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <Button
                fullWidth
                variant="outlined"
                startIcon={<TrendingUp />}
                onClick={() => navigate('/analytics')}
                className="hover-lift"
                sx={{ 
                  py: 2,
                  background: 'rgba(236, 72, 153, 0.15)',
                  borderColor: 'rgba(236, 72, 153, 0.6)',
                  color: '#ffffff',
                  fontWeight: 700,
                  textShadow: '0 1px 3px rgba(0,0,0,0.8)',
                  '&:hover': {
                    background: 'rgba(236, 72, 153, 0.25)',
                    borderColor: '#ec4899',
                    transform: 'translateY(-2px)',
                    boxShadow: '0 8px 25px rgba(236, 72, 153, 0.4)',
                    color: '#ffffff',
                  }
                }}
              >
                View Analytics
              </Button>
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <Button
                fullWidth
                variant="outlined"
                startIcon={<Work />}
                onClick={() => navigate('/recommendations')}
                className="hover-lift"
                sx={{ 
                  py: 2,
                  background: 'rgba(245, 158, 11, 0.15)',
                  borderColor: 'rgba(245, 158, 11, 0.6)',
                  color: '#ffffff',
                  fontWeight: 700,
                  textShadow: '0 1px 3px rgba(0,0,0,0.8)',
                  '&:hover': {
                    background: 'rgba(245, 158, 11, 0.25)',
                    borderColor: '#f59e0b',
                    transform: 'translateY(-2px)',
                    boxShadow: '0 8px 25px rgba(245, 158, 11, 0.4)',
                    color: '#ffffff',
                  }
                }}
              >
                All Opportunities
              </Button>
            </Grid>
          </Grid>
        </CardContent>
      </Card>
    </Box>
  );
};

export default Dashboard;
