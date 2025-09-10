import axios from 'axios';
import { getSessionToken } from '@descope/react-sdk';

const API_BASE_URL = 'http://localhost:8000';

// Create axios instance
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Helper function to make authenticated requests
const makeAuthenticatedRequest = async (config: any) => {
  try {
    const sessionToken = await getSessionToken();
    console.log('Session token retrieved:', sessionToken ? 'Yes' : 'No');
    if (sessionToken) {
      config.headers = {
        ...config.headers,
        Authorization: `Bearer ${sessionToken}`,
      };
      console.log('Authorization header set');
    } else {
      console.warn('No session token available for authenticated request');
    }
  } catch (error) {
    console.error('Error getting Descope session token:', error);
  }
  return api(config);
};

// Types
export interface User {
  id: string;
  email: string;
  username: string;
  created_at: string;
}

export interface UserProfile {
  user_id: string;
  skills: string[];
  interests: string[];
  preferred_locations: string[];
  experience_level: string;
  remote_preference: boolean;
  preferred_job_types: string[];
  resume_path?: string;
}

export interface Opportunity {
  id: string;
  title: string;
  company: string;
  location: string;
  type: 'job' | 'internship' | 'hackathon';
  source: string;
  skills: string[];
  description: string;
  url?: string;
  salary?: string;
  deadline?: string;
}

export interface Recommendation {
  id: string;
  opportunity_id: string;
  user_id: string;
  score: number;
  reasoning: string;
  created_at: string;
  viewed: boolean;
  applied: boolean;
  opportunity: Opportunity;
}

export interface SegregatedRecommendations {
  best_matches: Recommendation[];
  other_suggestions: Recommendation[];
}

export interface OnboardingData {
  skills: string[];
  interests: string[];
  preferred_locations: string[];
  experience_level: string;
  remote_preference: boolean;
  preferred_job_types: string[];
}

// API functions
export const authAPI = {
  register: async (email: string, password: string, username: string) => {
    const response = await api.post('/auth/register', { email, password, username });
    return response.data;
  },

  login: async (email: string, password: string) => {
    const response = await api.post('/auth/login', { email, password });
    return response.data;
  },

  getCurrentUser: async () => {
    const response = await makeAuthenticatedRequest({
      method: 'get',
      url: '/users/me'
    });
    return response.data;
  },
};

export const profileAPI = {
  getProfile: async () => {
    const response = await makeAuthenticatedRequest({
      method: 'get',
      url: '/users/me/profile'
    });
    return response.data;
  },

  updateProfile: async (profile: Partial<UserProfile>) => {
    const response = await makeAuthenticatedRequest({
      method: 'put',
      url: '/users/me/profile',
      data: profile
    });
    return response.data;
  },

  completeOnboarding: async (data: OnboardingData) => {
    const response = await makeAuthenticatedRequest({
      method: 'post',
      url: '/users/onboarding',
      data: data
    });
    return response.data;
  },
};

export const recommendationsAPI = {
  getRecommendations: async () => {
    const response = await makeAuthenticatedRequest({
      method: 'get',
      url: '/users/me/recommendations'
    });
    return response.data;
  },

  markAsViewed: async (recommendationId: string) => {
    try {
      const response = await makeAuthenticatedRequest({
        method: 'post',
        url: `/users/me/recommendations/${recommendationId}/view`
      });
      return response.data;
    } catch (error) {
      console.error('Error marking recommendation as viewed:', error);
      // Don't throw the error, just log it to prevent UI crashes
      const errorMessage = error instanceof Error ? error.message : 'Unknown error';
      return { success: false, error: errorMessage };
    }
  },

  markAsApplied: async (recommendationId: string) => {
    try {
      const response = await makeAuthenticatedRequest({
        method: 'post',
        url: `/users/me/recommendations/${recommendationId}/apply`
      });
      return response.data;
    } catch (error) {
      console.error('Error marking recommendation as applied:', error);
      // Don't throw the error, just log it to prevent UI crashes
      const errorMessage = error instanceof Error ? error.message : 'Unknown error';
      return { success: false, error: errorMessage };
    }
  },
};

export const opportunitiesAPI = {
  getOpportunities: async (type?: string, limit?: number) => {
    const params = new URLSearchParams();
    if (type) params.append('type', type);
    if (limit) params.append('limit', limit.toString());
    
    const response = await api.get(`/opportunities?${params.toString()}`);
    return response.data;
  },
};

export const analyticsAPI = {
  getAnalytics: async () => {
    const response = await makeAuthenticatedRequest({
      method: 'get',
      url: '/users/me/analytics'
    });
    return response.data;
  },
};

export const resumeAPI = {
  uploadResume: async (file: File) => {
    const formData = new FormData();
    formData.append('file', file);
    
    const response = await makeAuthenticatedRequest({
      method: 'post',
      url: '/users/me/resume/upload',
      data: formData,
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  getResumes: async () => {
    const response = await makeAuthenticatedRequest({
      method: 'get',
      url: '/users/me/resumes'
    });
    return response.data;
  },
};

export default api;
