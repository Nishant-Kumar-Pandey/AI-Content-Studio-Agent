import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';

const TrendingPanel = ({ onTopicSelect }) => {
  const [trends, setTrends] = useState([]);
  const [loading, setLoading] = useState(true);
  const { token, logout } = useAuth();

  const API_BASE = import.meta.env.VITE_API_URL || "http://localhost:8080";
  const BASE_CLEAN = API_BASE.endsWith('/') ? API_BASE.slice(0, -1) : API_BASE;

  useEffect(() => {
    const fetchTrends = async () => {
      try {
        const res = await fetch(`${BASE_CLEAN}/trending`, {
          headers: { 'Authorization': `Bearer ${token}` }
        });
        if (res.status === 401) {
          logout();
          return;
        }
        if (res.ok) {
          const data = await res.json();
          setTrends(data);
        }
      } catch (err) {
        console.error("Failed to fetch trends:", err);
      } finally {
        setLoading(false);
      }
    };
    fetchTrends();
  }, [token, logout, BASE_CLEAN]);

  if (loading) return <div className="loader">Analyzing trends...</div>;

  return (
    <div className="trending-panel glass-panel">
      <div className="talk-header">
        <div className="talk-title">🔥 Trending Topics</div>
      </div>
      
      <div className="trends-container">
        {trends.map((item, index) => (
          <div key={index} className="trend-card" onClick={() => onTopicSelect(item.topic)}>
            <div className="trend-growth">{item.growth}</div>
            <h3 className="trend-topic">{item.topic}</h3>
            <p className="trend-desc">{item.description}</p>
            <button className="use-trend-btn">Generate Content ✨</button>
          </div>
        ))}
      </div>
    </div>
  );
};

export default TrendingPanel;
