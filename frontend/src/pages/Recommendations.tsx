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
  Tabs,
  Tab,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  IconButton,
} from '@mui/material';
import {
  Work,
  School,
  Code,
  Visibility,
  Send,
  Close,
  TrendingUp,
} from '@mui/icons-material';
import { recommendationsAPI, Recommendation } from '../services/api';

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

function TabPanel(props: TabPanelProps) {
  const { children, value, index, ...other } = props;

  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`simple-tabpanel-${index}`}
      aria-labelledby={`simple-tab-${index}`}
      {...other}
    >
      {value === index && <Box sx={{ p: 3 }}>{children}</Box>}
    </div>
  );
}

const Recommendations: React.FC = () => {
  const [recommendations, setRecommendations] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [tabValue, setTabValue] = useState(0);
  const [selectedRec, setSelectedRec] = useState<Recommendation | null>(null);
  const [dialogOpen, setDialogOpen] = useState(false);

  const fetchRecommendations = async () => {
    try {
      setLoading(true);
      const data = await recommendationsAPI.getRecommendations();
      setRecommendations(data);
    } catch (err: any) {
      setError('Failed to load recommendations');
      console.error('Recommendations error:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchRecommendations();
  }, []);

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue);
  };

  const handleViewDetails = async (rec: Recommendation) => {
    setSelectedRec(rec);
    setDialogOpen(true);
    if (!rec.viewed) {
      try {
        await recommendationsAPI.markAsViewed(rec.id);
        // Optionally refresh recommendations to update the viewed status
        // fetchRecommendations();
      } catch (error) {
        console.error('Failed to mark as viewed:', error);
        // Don't prevent the dialog from opening if marking as viewed fails
      }
    }
  };

  const handleApply = async (rec: Recommendation) => {
    try {
      await recommendationsAPI.markAsApplied(rec.id);
      setDialogOpen(false);
      fetchRecommendations(); // Refresh to update status
    } catch (err) {
      console.error('Failed to mark as applied:', err);
    }
  };

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

  const getScoreColor = (score: number) => {
    if (score >= 0.8) return 'success';
    if (score >= 0.6) return 'warning';
    return 'error';
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
        <Button onClick={fetchRecommendations} sx={{ ml: 2 }}>
          Retry
        </Button>
      </Alert>
    );
  }

  const allRecommendations = [
    ...(recommendations?.best_matches || []),
    ...(recommendations?.other_suggestions || []),
  ];

  const jobRecommendations = allRecommendations.filter(rec => rec.opportunity.type === 'job');
  const internshipRecommendations = allRecommendations.filter(rec => rec.opportunity.type === 'internship');
  const hackathonRecommendations = allRecommendations.filter(rec => rec.opportunity.type === 'hackathon');

  const RecommendationCard: React.FC<{ rec: Recommendation }> = ({ rec }) => (
    <Card sx={{ height: '100%', cursor: 'pointer' }} onClick={() => handleViewDetails(rec)}>
      <CardContent>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 2 }}>
          <Typography variant="h6" component="h2" sx={{ fontWeight: 'bold' }}>
            {rec.opportunity.title}
          </Typography>
          <Box sx={{ display: 'flex', gap: 1 }}>
            <Chip
              icon={getTypeIcon(rec.opportunity.type)}
              label={rec.opportunity.type}
              color={getTypeColor(rec.opportunity.type) as any}
              size="small"
            />
            <Chip
              label={`${Math.round(rec.score * 100)}%`}
              color={getScoreColor(rec.score) as any}
              size="small"
              variant="outlined"
            />
          </Box>
        </Box>
        <Typography variant="subtitle1" color="text.secondary" gutterBottom>
          {rec.opportunity.company} • {rec.opportunity.location}
        </Typography>
        <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5, mb: 2 }}>
          {rec.opportunity.skills.slice(0, 4).map((skill) => (
            <Chip key={skill} label={skill} size="small" variant="outlined" />
          ))}
          {rec.opportunity.skills.length > 4 && (
            <Chip label={`+${rec.opportunity.skills.length - 4}`} size="small" variant="outlined" />
          )}
        </Box>
        <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
          {rec.reasoning.substring(0, 100)}...
        </Typography>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <Box sx={{ display: 'flex', gap: 1 }}>
            {rec.viewed && (
              <Chip icon={<Visibility />} label="Viewed" size="small" color="info" />
            )}
            {rec.applied && (
              <Chip icon={<Send />} label="Applied" size="small" color="success" />
            )}
          </Box>
          <Button size="small" variant="outlined">
            View Details
          </Button>
        </Box>
      </CardContent>
    </Card>
  );

  return (
    <Box>
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          Your Recommendations
        </Typography>
        <Typography variant="subtitle1" color="text.secondary">
          AI-powered matches based on your profile and preferences
        </Typography>
      </Box>

      <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 3 }}>
        <Tabs value={tabValue} onChange={handleTabChange} aria-label="recommendation tabs">
          <Tab label={`All (${allRecommendations.length})`} />
          <Tab label={`Jobs (${jobRecommendations.length})`} />
          <Tab label={`Internships (${internshipRecommendations.length})`} />
          <Tab label={`Hackathons (${hackathonRecommendations.length})`} />
        </Tabs>
      </Box>

      <TabPanel value={tabValue} index={0}>
        <Grid container spacing={3}>
          {allRecommendations.map((rec) => (
            <Grid item xs={12} md={6} lg={4} key={rec.id}>
              <RecommendationCard rec={rec} />
            </Grid>
          ))}
        </Grid>
      </TabPanel>

      <TabPanel value={tabValue} index={1}>
        <Grid container spacing={3}>
          {jobRecommendations.map((rec) => (
            <Grid item xs={12} md={6} lg={4} key={rec.id}>
              <RecommendationCard rec={rec} />
            </Grid>
          ))}
        </Grid>
      </TabPanel>

      <TabPanel value={tabValue} index={2}>
        <Grid container spacing={3}>
          {internshipRecommendations.map((rec) => (
            <Grid item xs={12} md={6} lg={4} key={rec.id}>
              <RecommendationCard rec={rec} />
            </Grid>
          ))}
        </Grid>
      </TabPanel>

      <TabPanel value={tabValue} index={3}>
        <Grid container spacing={3}>
          {hackathonRecommendations.map((rec) => (
            <Grid item xs={12} md={6} lg={4} key={rec.id}>
              <RecommendationCard rec={rec} />
            </Grid>
          ))}
        </Grid>
      </TabPanel>

      {/* Detail Dialog */}
      <Dialog open={dialogOpen} onClose={() => setDialogOpen(false)} maxWidth="md" fullWidth>
        <DialogTitle>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <Typography variant="h6">
              {selectedRec?.opportunity.title}
            </Typography>
            <IconButton onClick={() => setDialogOpen(false)}>
              <Close />
            </IconButton>
          </Box>
        </DialogTitle>
        <DialogContent>
          {selectedRec && (
            <Box>
              <Typography variant="h6" gutterBottom>
                {selectedRec.opportunity.company} • {selectedRec.opportunity.location}
              </Typography>
              <Box sx={{ display: 'flex', gap: 1, mb: 2 }}>
                <Chip
                  icon={getTypeIcon(selectedRec.opportunity.type)}
                  label={selectedRec.opportunity.type}
                  color={getTypeColor(selectedRec.opportunity.type) as any}
                />
                <Chip
                  label={`${Math.round(selectedRec.score * 100)}% Match`}
                  color={getScoreColor(selectedRec.score) as any}
                  icon={<TrendingUp />}
                />
              </Box>
              <Typography variant="body1" paragraph>
                {selectedRec.opportunity.description}
              </Typography>
              <Typography variant="h6" gutterBottom>
                Required Skills:
              </Typography>
              <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1, mb: 2 }}>
                {selectedRec.opportunity.skills.map((skill) => (
                  <Chip key={skill} label={skill} variant="outlined" />
                ))}
              </Box>
              <Typography variant="h6" gutterBottom>
                Why This Matches You:
              </Typography>
              <Typography variant="body1" paragraph>
                {selectedRec.reasoning}
              </Typography>
              {selectedRec.opportunity.url && (
                <Button
                  variant="contained"
                  href={selectedRec.opportunity.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  sx={{ mr: 2 }}
                >
                  View Original Posting
                </Button>
              )}
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDialogOpen(false)}>
            Close
          </Button>
          {selectedRec && !selectedRec.applied && (
            <Button
              variant="contained"
              onClick={() => handleApply(selectedRec)}
              startIcon={<Send />}
            >
              Mark as Applied
            </Button>
          )}
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default Recommendations;
