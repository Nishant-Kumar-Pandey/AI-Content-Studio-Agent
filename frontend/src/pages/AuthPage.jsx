import React, { useState } from 'react';
import { useAuth } from '../context/AuthContext';

const AuthPage = () => {
  const [isLogin, setIsLogin] = useState(true);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [fullName, setFullName] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  
  const { login: saveAuth } = useAuth();
  const API_BASE = import.meta.env.VITE_API_URL || "http://localhost:8080";
  const BASE_CLEAN = API_BASE.endsWith('/') ? API_BASE.slice(0, -1) : API_BASE;

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    const endpoint = isLogin ? '/auth/login' : '/auth/register';
    const payload = isLogin 
      ? { email, password } 
      : { email, password, full_name: fullName };

    try {
      const res = await fetch(`${BASE_CLEAN}${endpoint}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });

      if (res.status === 500) {
        const serverError = await res.json().catch(() => ({}));
        const errorDetail = serverError.traceback || serverError.detail || "No details provided";
        throw new Error(`Server Error (500): ${errorDetail}. Please ensure you have pushed latest changes and redeployed to Render.`);
      }

      const data = await res.json().catch(() => ({ detail: 'Authentication failed (could not parse response)' }));
      if (!res.ok) throw new Error(data.detail || 'Authentication failed');

      saveAuth(data.access_token, data.user);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleOAuth = (provider) => {
    const providerLower = provider.toLowerCase();
    
    // LinkedIn is not yet implemented in backend, show warning
    if (providerLower === 'linkedin') {
      alert("LinkedIn login is coming soon! Our backend is currently configured for Google and GitHub.");
      return;
    }

    if (['google', 'github'].includes(providerLower)) {
      // Ensure we use the correct backend URL
      window.location.href = `${BASE_CLEAN}/auth/${providerLower}/login`;
    } else {
      alert(`${provider} login coming soon! Requires Client ID setup.`);
    }
  };

  // SVGs for Logos
  const GoogleLogo = () => (
    <svg width="20" height="20" viewBox="0 0 24 24">
      <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
      <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
      <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l3.66-2.84z"/>
      <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
    </svg>
  );

  const GitHubLogo = () => (
    <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
      <path d="M12 .297c-6.63 0-12 5.373-12 12 0 5.303 3.438 9.8 8.205 11.385.6.113.82-.258.82-.577 0-.285-.01-1.04-.015-2.04-3.338.724-4.042-1.61-4.042-1.61C4.422 18.07 3.633 17.7 3.633 17.7c-1.087-.744.084-.729.084-.729 1.205.084 1.838 1.236 1.838 1.236 1.07 1.835 2.809 1.305 3.495.998.108-.776.417-1.305.76-1.605-2.665-.3-5.466-1.332-5.466-5.93 0-1.31.465-2.38 1.235-3.22-.135-.303-.54-1.523.105-3.176 0 0 1.005-.322 3.3 1.23.96-.267 1.98-.399 3-.405 1.02.006 2.04.138 3 .405 2.28-1.552 3.285-1.23 3.285-1.23.645 1.653.24 2.873.12 3.176.765.84 1.23 1.91 1.23 3.22 0 4.61-2.805 5.625-5.475 5.92.42.36.81 1.096.81 2.22 0 1.606-.015 2.896-.015 3.286 0 .315.21.69.825.57C20.565 22.092 24 17.592 24 12.297c0-6.627-5.373-12-12-12"/>
    </svg>
  );

  const LinkedInLogo = () => (
    <svg width="20" height="20" viewBox="0 0 24 24" fill="#0A66C2">
      <path d="M19 0h-14c-2.761 0-5 2.239-5 5v14c0 2.761 2.239 5 5 5h14c2.762 0 5-2.239 5-5v-14c0-2.761-2.238-5-5-5zm-11 19h-3v-11h3v11zm-1.5-12.268c-.966 0-1.75-.79-1.75-1.764s.784-1.764 1.75-1.764 1.75.79 1.75 1.764-.783 1.764-1.75 1.764zm13.5 12.268h-3v-5.604c0-3.368-4-3.113-4 0v5.604h-3v-11h3v1.765c1.396-2.586 7-2.777 7 2.476v6.759z"/>
    </svg>
  );

  return (
    <div className="auth-container">
      <div className="auth-card glass-panel">
        <h2>{isLogin ? 'Welcome Back' : 'Create Account'}</h2>
        <p className="auth-subtitle">
          {isLogin ? 'Sign in to access your creative studio' : 'Start your journey with AI Content Studio'}
        </p>

        <div className="auth-tabs">
          <button 
            className={`auth-tab ${isLogin ? 'active' : ''}`} 
            onClick={() => setIsLogin(true)}
          >
            Login
          </button>
          <button 
            className={`auth-tab ${!isLogin ? 'active' : ''}`} 
            onClick={() => setIsLogin(false)}
          >
            Register
          </button>
        </div>

        {error && <div className="error-message" style={{marginBottom: '1rem'}}>{error}</div>}

        <form className="auth-form" onSubmit={handleSubmit}>
          {!isLogin && (
            <input 
              type="text" 
              placeholder="Full Name" 
              required 
              value={fullName}
              onChange={(e) => setFullName(e.target.value)}
            />
          )}
          <input 
            type="email" 
            placeholder="Email Address" 
            required 
            value={email}
            onChange={(e) => setEmail(e.target.value)}
          />
          <input 
            type="password" 
            placeholder="Password" 
            required 
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />
          <button type="submit" className="auth-submit-btn" disabled={loading}>
            {loading ? 'Processing...' : (isLogin ? 'Sign In' : 'Sign Up')}
          </button>
        </form>

        <div className="divider">or continue with</div>

        <div className="oauth-buttons">
          <button className="oauth-btn" onClick={() => handleOAuth('Google')}>
            <GoogleLogo />
            <span>Google</span>
          </button>
          <button className="oauth-btn" onClick={() => handleOAuth('GitHub')}>
            <GitHubLogo />
            <span>GitHub</span>
          </button>
          <button className="oauth-btn" onClick={() => handleOAuth('LinkedIn')}>
            <LinkedInLogo />
            <span>LinkedIn</span>
          </button>
        </div>
      </div>
    </div>
  );
};

export default AuthPage;
