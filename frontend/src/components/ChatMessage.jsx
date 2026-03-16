import React from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

const ChatMessage = ({ message, isAi }) => {
  return (
    <div className={`chat-message-wrapper ${isAi ? 'ai' : 'user'}`}>
      <div className={`chat-bubble ${isAi ? 'ai' : 'user'}`}>
        <div className="chat-content">
          {isAi ? (
            <ReactMarkdown remarkPlugins={[remarkGfm]}>
              {message}
            </ReactMarkdown>
          ) : (
            message
          )}
        </div>
      </div>
    </div>
  );
};

export default ChatMessage;
