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

      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || 'Authentication failed');

      saveAuth(data.access_token, data.user);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleOAuth = (provider) => {
    alert(`${provider} login coming soon! Requires Client ID setup.`);
  };

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
            <span className="oauth-icon">G</span> Google
          </button>
          <button className="oauth-btn" onClick={() => handleOAuth('GitHub')}>
            <span className="oauth-icon">GitHub</span> GitHub
          </button>
          <button className="oauth-btn" onClick={() => handleOAuth('LinkedIn')}>
            <span className="oauth-icon">in</span> LinkedIn
          </button>
        </div>
      </div>
    </div>
  );
};

export default AuthPage;
