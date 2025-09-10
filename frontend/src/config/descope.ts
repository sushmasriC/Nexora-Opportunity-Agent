// Descope configuration
export const DESCOPE_CONFIG = {
  projectId: process.env.REACT_APP_DESCOPE_PROJECT_ID || 'P32PGSu8wPzyY4nRF5fwc4rze4vX',
  flowId: process.env.REACT_APP_DESCOPE_FLOW_ID || 'sign-up-or-in',
  clientId: process.env.REACT_APP_DESCOPE_CLIENT_ID || 'UDMyUEdTdTh3UHp5WTRuUkY1ZndjNHJ6ZTR2WDpLMzJQSHJDY1NTWnpRTXpPYVVjM3R6dWd0OE9t',
  clientSecret: process.env.REACT_APP_DESCOPE_CLIENT_SECRET || 'K32PHrCcSSZzQMzOaUc3tzugt8OmV0Oc9N2AlpZuFXF40EJp7qqOlEoo9JoS6mYcGw3FhLq',
  baseUrl: 'https://api.descope.com',
};

// Flow IDs - using your configured flow ID
export const FLOW_IDS = {
  signUp: 'sign-up-or-in',
  signIn: 'sign-up-or-in',
  signOut: 'sign-out',
};
