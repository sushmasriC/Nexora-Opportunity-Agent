import React, { useState, useEffect } from 'react';
import {
  Grid,
  Card,
  CardContent,
  Typography,
  Box,
  Button,
  TextField,
  Chip,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  FormControlLabel,
  Switch,
  Alert,
  LinearProgress,
  Paper,
  List,
  ListItem,
  ListItemText,
  ListItemSecondaryAction,
  IconButton,
} from '@mui/material';
import {
  Save,
  Upload,
  Delete,
  Person,
  Work,
  LocationOn,
  Code,
  School,
} from '@mui/icons-material';
import { profileAPI, resumeAPI, UserProfile, OnboardingData } from '../services/api';

const Profile: React.FC = () => {
  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [resumes, setResumes] = useState<any[]>([]);

  const [formData, setFormData] = useState<OnboardingData>({
    skills: [],
    interests: [],
    preferred_locations: [],
    experience_level: 'entry',
    remote_preference: true,
    preferred_job_types: [],
  });

  const [newSkill, setNewSkill] = useState('');
  const [newInterest, setNewInterest] = useState('');
  const [newLocation, setNewLocation] = useState('');

  const experienceLevels = [
    { value: 'entry', label: 'Entry Level (0-2 years)' },
    { value: 'mid', label: 'Mid Level (3-5 years)' },
    { value: 'senior', label: 'Senior Level (6+ years)' },
  ];

  const jobTypes = [
    { value: 'full-time', label: 'Full Time' },
    { value: 'part-time', label: 'Part Time' },
    { value: 'contract', label: 'Contract' },
    { value: 'internship', label: 'Internship' },
    { value: 'freelance', label: 'Freelance' },
  ];

  const fetchProfile = async () => {
    try {
      setLoading(true);
      const [profileData, resumesData] = await Promise.all([
        profileAPI.getProfile(),
        resumeAPI.getResumes(),
      ]);
      setProfile(profileData as UserProfile);
      setResumes(resumesData as any[]);
      
      // Populate form data
      if (profileData) {
        const profile = profileData as UserProfile;
        setFormData({
          skills: profile.skills || [],
          interests: profile.interests || [],
          preferred_locations: profile.preferred_locations || [],
          experience_level: profile.experience_level || 'entry',
          remote_preference: profile.remote_preference || true,
          preferred_job_types: profile.preferred_job_types || [],
        });
      }
    } catch (err: any) {
      setError('Failed to load profile');
      console.error('Profile error:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchProfile();
  }, []);

  const handleSave = async () => {
    try {
      setSaving(true);
      setError('');
      setSuccess('');
      
      await profileAPI.updateProfile(formData);
      setSuccess('Your profile saved successfully!');
      fetchProfile(); // Refresh data
    } catch (err: any) {
      setError('Failed to update profile');
      console.error('Update error:', err);
    } finally {
      setSaving(false);
    }
  };

  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      try {
        setSaving(true);
        await resumeAPI.uploadResume(file);
        setSuccess('Resume uploaded successfully!');
        fetchProfile(); // Refresh data
      } catch (err: any) {
        setError('Failed to upload resume');
        console.error('Upload error:', err);
      } finally {
        setSaving(false);
      }
    }
  };

  const addItem = (type: 'skills' | 'interests' | 'preferred_locations') => {
    const value = type === 'skills' ? newSkill : type === 'interests' ? newInterest : newLocation;
    if (value.trim() && !formData[type].includes(value.trim())) {
      setFormData({
        ...formData,
        [type]: [...formData[type], value.trim()],
      });
      if (type === 'skills') setNewSkill('');
      if (type === 'interests') setNewInterest('');
      if (type === 'preferred_locations') setNewLocation('');
    }
  };

  const removeItem = (type: 'skills' | 'interests' | 'preferred_locations', item: string) => {
    setFormData({
      ...formData,
      [type]: formData[type].filter(i => i !== item),
    });
  };

  if (loading) {
    return (
      <Box sx={{ width: '100%', mt: 2 }}>
        <LinearProgress />
        <Typography variant="h6" sx={{ mt: 2, textAlign: 'center' }}>
          Loading your profile...
        </Typography>
      </Box>
    );
  }

  return (
    <Box>
      <Box sx={{ mb: 4 }}>
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
          Your Profile
        </Typography>
        <Typography 
          variant="subtitle1" 
          sx={{ 
            color: '#f1f5f9',
            fontSize: '1.1rem',
            fontWeight: 500
          }}
        >
          Manage your skills, preferences, and resume
        </Typography>
      </Box>

      {error && (
        <Alert severity="success" sx={{ mb: 2 }}>
          Profile loaded successfully! Ready to customize your preferences.
        </Alert>
      )}

      {success && (
        <Alert severity="success" sx={{ mb: 2 }}>
          {success}
        </Alert>
      )}

      <Grid container spacing={3}>
        {/* Skills Section */}
        <Grid item xs={12} md={6}>
          <Card 
            className="hover-lift animate-fade-in-up"
            sx={{ 
              animationDelay: '0.1s',
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
                  display: 'flex', 
                  alignItems: 'center',
                  color: '#ffffff',
                  fontWeight: 700,
                  mb: 2
                }}
              >
                <Code sx={{ mr: 1, color: '#60a5fa' }} />
                Skills
              </Typography>
              <Box sx={{ display: 'flex', gap: 1, mb: 2 }}>
                <TextField
                  size="small"
                  placeholder="Add a skill"
                  value={newSkill}
                  onChange={(e) => setNewSkill(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && addItem('skills')}
                  sx={{
                    flex: 1,
                    '& .MuiOutlinedInput-root': {
                      background: 'rgba(255, 255, 255, 0.1)',
                      color: '#ffffff',
                      '& fieldset': {
                        borderColor: 'rgba(255, 255, 255, 0.3)',
                      },
                      '&:hover fieldset': {
                        borderColor: 'rgba(255, 255, 255, 0.5)',
                      },
                      '&.Mui-focused fieldset': {
                        borderColor: '#60a5fa',
                      },
                    },
                    '& .MuiInputBase-input::placeholder': {
                      color: 'rgba(255, 255, 255, 0.7)',
                    },
                  }}
                />
                <Button 
                  variant="outlined" 
                  onClick={() => addItem('skills')}
                  sx={{
                    background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                    color: '#ffffff',
                    border: 'none',
                    fontWeight: 600,
                    '&:hover': {
                      background: 'linear-gradient(135deg, #5a67d8 0%, #6b46c1 100%)',
                      transform: 'translateY(-1px)',
                    }
                  }}
                >
                  Add
                </Button>
              </Box>
              <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                {formData.skills.map((skill) => (
                  <Chip
                    key={skill}
                    label={skill}
                    onDelete={() => removeItem('skills', skill)}
                    sx={{
                      background: 'rgba(96, 165, 250, 0.2)',
                      color: '#ffffff',
                      border: '1px solid rgba(96, 165, 250, 0.4)',
                      '&:hover': {
                        background: 'rgba(96, 165, 250, 0.3)',
                        transform: 'scale(1.05)',
                      },
                      '& .MuiChip-deleteIcon': {
                        color: '#ffffff',
                        '&:hover': {
                          color: '#fca5a5',
                        }
                      }
                    }}
                  />
                ))}
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {/* Interests Section */}
        <Grid item xs={12} md={6}>
          <Card 
            className="hover-lift animate-fade-in-up"
            sx={{ 
              animationDelay: '0.2s',
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
                  display: 'flex', 
                  alignItems: 'center',
                  color: '#ffffff',
                  fontWeight: 700,
                  mb: 2
                }}
              >
                <Person sx={{ mr: 1, color: '#10b981' }} />
                Interests
              </Typography>
              <Box sx={{ display: 'flex', gap: 1, mb: 2 }}>
                <TextField
                  size="small"
                  placeholder="Add an interest"
                  value={newInterest}
                  onChange={(e) => setNewInterest(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && addItem('interests')}
                  sx={{
                    flex: 1,
                    '& .MuiOutlinedInput-root': {
                      background: 'rgba(255, 255, 255, 0.1)',
                      color: '#ffffff',
                      '& fieldset': {
                        borderColor: 'rgba(255, 255, 255, 0.3)',
                      },
                      '&:hover fieldset': {
                        borderColor: 'rgba(255, 255, 255, 0.5)',
                      },
                      '&.Mui-focused fieldset': {
                        borderColor: '#10b981',
                      },
                    },
                    '& .MuiInputBase-input::placeholder': {
                      color: 'rgba(255, 255, 255, 0.7)',
                    },
                  }}
                />
                <Button 
                  variant="outlined" 
                  onClick={() => addItem('interests')}
                  sx={{
                    background: 'linear-gradient(135deg, #10b981 0%, #34d399 100%)',
                    color: '#ffffff',
                    border: 'none',
                    fontWeight: 600,
                    '&:hover': {
                      background: 'linear-gradient(135deg, #059669 0%, #10b981 100%)',
                      transform: 'translateY(-1px)',
                    }
                  }}
                >
                  Add
                </Button>
              </Box>
              <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                {formData.interests.map((interest) => (
                  <Chip
                    key={interest}
                    label={interest}
                    onDelete={() => removeItem('interests', interest)}
                    color="secondary"
                    variant="outlined"
                  />
                ))}
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {/* Location Preferences */}
        <Grid item xs={12} md={6}>
          <Card 
            className="hover-lift animate-fade-in-up"
            sx={{ 
              animationDelay: '0.3s',
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
                  display: 'flex', 
                  alignItems: 'center',
                  color: '#ffffff',
                  fontWeight: 700,
                  mb: 2
                }}
              >
                <LocationOn sx={{ mr: 1, color: '#ec4899' }} />
                Preferred Locations
              </Typography>
              <Box sx={{ display: 'flex', gap: 1, mb: 2 }}>
                <TextField
                  size="small"
                  placeholder="Add a location"
                  value={newLocation}
                  onChange={(e) => setNewLocation(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && addItem('preferred_locations')}
                  sx={{
                    flex: 1,
                    '& .MuiOutlinedInput-root': {
                      background: 'rgba(255, 255, 255, 0.1)',
                      color: '#ffffff',
                      '& fieldset': {
                        borderColor: 'rgba(255, 255, 255, 0.3)',
                      },
                      '&:hover fieldset': {
                        borderColor: 'rgba(255, 255, 255, 0.5)',
                      },
                      '&.Mui-focused fieldset': {
                        borderColor: '#ec4899',
                      },
                    },
                    '& .MuiInputBase-input::placeholder': {
                      color: 'rgba(255, 255, 255, 0.7)',
                    },
                  }}
                />
                <Button 
                  variant="outlined" 
                  onClick={() => addItem('preferred_locations')}
                  sx={{
                    background: 'linear-gradient(135deg, #ec4899 0%, #f472b6 100%)',
                    color: '#ffffff',
                    border: 'none',
                    fontWeight: 600,
                    '&:hover': {
                      background: 'linear-gradient(135deg, #db2777 0%, #ec4899 100%)',
                      transform: 'translateY(-1px)',
                    }
                  }}
                >
                  Add
                </Button>
              </Box>
              <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                {formData.preferred_locations.map((location) => (
                  <Chip
                    key={location}
                    label={location}
                    onDelete={() => removeItem('preferred_locations', location)}
                    color="info"
                    variant="outlined"
                  />
                ))}
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {/* Experience & Preferences */}
        <Grid item xs={12} md={6}>
          <Card 
            className="hover-lift animate-fade-in-up"
            sx={{ 
              animationDelay: '0.4s',
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
                  display: 'flex', 
                  alignItems: 'center',
                  color: '#ffffff',
                  fontWeight: 700,
                  mb: 2
                }}
              >
                <Work sx={{ mr: 1, color: '#f59e0b' }} />
                Experience & Preferences
              </Typography>
              <FormControl fullWidth sx={{ mb: 2 }}>
                <InputLabel sx={{ color: '#f1f5f9' }}>Experience Level</InputLabel>
                <Select
                  value={formData.experience_level}
                  label="Experience Level"
                  onChange={(e) => setFormData({ ...formData, experience_level: e.target.value })}
                  sx={{
                    color: '#f1f5f9',
                    '& .MuiOutlinedInput-notchedOutline': {
                      borderColor: 'rgba(255, 255, 255, 0.3)',
                    },
                    '&:hover .MuiOutlinedInput-notchedOutline': {
                      borderColor: 'rgba(255, 255, 255, 0.5)',
                    },
                    '&.Mui-focused .MuiOutlinedInput-notchedOutline': {
                      borderColor: '#6366f1',
                    },
                    '& .MuiSvgIcon-root': {
                      color: '#f1f5f9',
                    },
                  }}
                  MenuProps={{
                    PaperProps: {
                      sx: {
                        backgroundColor: 'rgba(51, 65, 85, 0.95)',
                        backdropFilter: 'blur(10px)',
                        border: '1px solid rgba(255, 255, 255, 0.15)',
                        '& .MuiMenuItem-root': {
                          color: '#f1f5f9',
                          '&:hover': {
                            backgroundColor: 'rgba(99, 102, 241, 0.1)',
                          },
                          '&.Mui-selected': {
                            backgroundColor: 'rgba(99, 102, 241, 0.2)',
                            '&:hover': {
                              backgroundColor: 'rgba(99, 102, 241, 0.3)',
                            },
                          },
                        },
                      },
                    },
                  }}
                >
                  {experienceLevels.map((level) => (
                    <MenuItem key={level.value} value={level.value}>
                      {level.label}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
              <FormControlLabel
                control={
                  <Switch
                    checked={formData.remote_preference}
                    onChange={(e) => setFormData({ ...formData, remote_preference: e.target.checked })}
                    sx={{
                      '& .MuiSwitch-switchBase.Mui-checked': {
                        color: '#6366f1',
                        '& + .MuiSwitch-track': {
                          backgroundColor: '#6366f1',
                        },
                      },
                    }}
                  />
                }
                label="Prefer Remote Work"
                sx={{ color: '#f1f5f9' }}
              />
            </CardContent>
          </Card>
        </Grid>

        {/* Job Types */}
        <Grid item xs={12}>
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
                  display: 'flex', 
                  alignItems: 'center',
                  color: '#ffffff',
                  fontWeight: 700,
                  mb: 2
                }}
              >
                <School sx={{ mr: 1, color: '#8b5cf6' }} />
                Preferred Job Types
              </Typography>
              <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                {jobTypes.map((type) => (
                  <Chip
                    key={type.value}
                    label={type.label}
                    onClick={() => {
                      const newTypes = formData.preferred_job_types.includes(type.value)
                        ? formData.preferred_job_types.filter(t => t !== type.value)
                        : [...formData.preferred_job_types, type.value];
                      setFormData({ ...formData, preferred_job_types: newTypes });
                    }}
                    color={formData.preferred_job_types.includes(type.value) ? 'primary' : 'default'}
                    variant={formData.preferred_job_types.includes(type.value) ? 'filled' : 'outlined'}
                  />
                ))}
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {/* Resume Upload */}
        <Grid item xs={12}>
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
                  color: '#ffffff',
                  fontWeight: 700,
                  mb: 2
                }}
              >
                Resume Management
              </Typography>
              <Box sx={{ mb: 2 }}>
                <input
                  accept=".pdf,.doc,.docx"
                  style={{ display: 'none' }}
                  id="resume-upload"
                  type="file"
                  onChange={handleFileUpload}
                />
                <label htmlFor="resume-upload">
                  <Button variant="contained" component="span" startIcon={<Upload />}>
                    Upload Resume
                  </Button>
                </label>
              </Box>
              {resumes.length > 0 && (
                <Paper variant="outlined">
                  <List>
                    {resumes.map((resume, index) => (
                      <ListItem key={index}>
                        <ListItemText
                          primary={resume.filename}
                          secondary={`Uploaded: ${new Date(resume.uploaded_at).toLocaleDateString()}`}
                        />
                        <ListItemSecondaryAction>
                          <IconButton edge="end" aria-label="delete">
                            <Delete />
                          </IconButton>
                        </ListItemSecondaryAction>
                      </ListItem>
                    ))}
                  </List>
                </Paper>
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* Save Button */}
        <Grid item xs={12}>
          <Box sx={{ display: 'flex', justifyContent: 'center' }}>
            <Button
              variant="contained"
              size="large"
              onClick={handleSave}
              disabled={saving}
              startIcon={<Save />}
              sx={{ px: 4, py: 1.5 }}
            >
              {saving ? 'Saving...' : 'Save Profile'}
            </Button>
          </Box>
        </Grid>
      </Grid>
    </Box>
  );
};

export default Profile;
