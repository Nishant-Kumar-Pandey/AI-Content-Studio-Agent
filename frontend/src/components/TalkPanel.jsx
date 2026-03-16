import React, { useState, useEffect, useRef } from 'react';
import ChatMessage from './ChatMessage';
import VoiceInput from './VoiceInput';
import { useAuth } from '../context/AuthContext';

const TalkPanel = ({ onGenerate }) => {
  const { token, logout } = useAuth();
  const [sessionId, setSessionId] = useState(`session_${Date.now()}`);
  const [messages, setMessages] = useState([
    { text: "Hello! I'm your AI Creative Strategist. What topic should we brainstorm today?", isAi: true }
  ]);
  const [history, setHistory] = useState([]);
  const [showHistory, setShowHistory] = useState(false);
  const [input, setInput] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const chatEndRef = useRef(null);

  // Robustly handle trailing slash
  const API_BASE = import.meta.env.VITE_API_URL || "http://localhost:8080";
  const BASE_CLEAN = API_BASE.endsWith('/') ? API_BASE.slice(0, -1) : API_BASE;
  const TALK_URL = `${BASE_CLEAN}/talk`;

  const scrollToBottom = () => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Load history list
  const fetchHistoryList = async () => {
    try {
      const res = await fetch(`${BASE_CLEAN}/sessions`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (res.status === 401) { logout(); return; }
      if (res.ok) {
        const data = await res.json();
        setHistory(data);
      }
    } catch (err) {
      console.error("Failed to fetch history:", err);
    }
  };

  useEffect(() => {
    fetchHistoryList();
  }, []);

  const startNewChat = () => {
    setSessionId(`session_${Date.now()}`);
    setMessages([{ text: "New session started! What's our next big idea?", isAi: true }]);
    setShowHistory(false);
  };

  const loadSession = async (sid) => {
    try {
      setIsTyping(true);
      const res = await fetch(`${BASE_CLEAN}/sessions/${sid}/messages`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (res.status === 401) { logout(); return; }
      if (res.ok) {
        const data = await res.json();
        if (data.length > 0) {
          setMessages(data.map(m => ({ text: m.content, isAi: m.is_ai })));
        }
        setSessionId(sid);
        setShowHistory(false);
      }
    } catch (err) {
      console.error("Failed to load session:", err);
    } finally {
      setIsTyping(false);
    }
  };

  const handleSend = async (text) => {
    const messageText = text || input;
    if (!messageText.trim()) return;

    const newMessages = [...messages, { text: messageText, isAi: false }];
    setMessages(newMessages);
    setInput('');
    setIsTyping(true);

    try {
      const response = await fetch(TALK_URL, {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({ message: messageText, session_id: sessionId }),
      });

      if (response.status === 401) { logout(); return; }

      if (response.status === 429) {
        setMessages([...newMessages, { 
          text: "🚨 API Quota Reached! Please try again tomorrow.", 
          isAi: true 
        }]);
        return;
      }

      if (!response.ok) throw new Error('Talk failed');

      const data = await response.json();
      setMessages([...newMessages, { text: data.reply, isAi: true }]);
      fetchHistoryList(); // Refresh list after reply
    } catch (err) {
      console.error(err);
      setMessages([...newMessages, { text: "Sorry, I hit a snag. Try again?", isAi: true }]);
    } finally {
      setIsTyping(false);
    }
  };

  return (
    <div className="talk-panel glass-panel">
      <div className="talk-header">
        <div className="talk-title">Creative Strategist</div>
        <div className="talk-actions">
          <button className="icon-btn" title="New Chat" onClick={startNewChat}>+</button>
          <button className="icon-btn" title="History" onClick={() => { setShowHistory(!showHistory); fetchHistoryList(); }}>🕒</button>
        </div>
      </div>

      <div className="chat-history">
        {messages.map((m, i) => (
          <ChatMessage key={i} message={m.text} isAi={m.isAi} />
        ))}
        {isTyping && <div className="typing-indicator">Strategist is thinking...</div>}
        <div ref={chatEndRef} />
      </div>

      {showHistory && (
        <div className="history-overlay">
          <div className="history-header">
            <span>Recent Chats</span>
            <button className="icon-btn" style={{border:'none'}} onClick={() => setShowHistory(false)}>✕</button>
          </div>
          <div className="history-list">
            {history.map((session) => (
              <div 
                key={session.id} 
                className={`history-item ${sessionId === session.id ? 'active' : ''}`}
                onClick={() => loadSession(session.id)}
              >
                <div className="session-title">{session.title}</div>
                <div className="session-date">{new Date(session.created_at).toLocaleDateString()}</div>
              </div>
            ))}
            {history.length === 0 && <div style={{padding: '1rem', color: 'var(--text-muted)'}}>No history yet</div>}
          </div>
        </div>
      )}

      <div className="chat-input-area">
        <VoiceInput onTranscript={(text) => handleSend(text)} />
        <input
          type="text"
          className="chat-input"
          placeholder="Type your message..."
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && handleSend()}
        />
        <button className="send-btn" onClick={() => handleSend()}>
          <span>Send</span>
        </button>
      </div>
      
      <button className="generate-now-btn" onClick={() => onGenerate(messages[messages.length-1]?.text)}>
        Generate Content from this Idea ✨
      </button>
    </div>
  );
};

export default TalkPanel;
