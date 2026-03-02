import { useState, useEffect, useRef } from 'react';
import useWebSocket from '../hooks/useWebSocket';

const ChatWidget = () => {
  const { sendMessage, messages, isConnected, isStreaming } = useWebSocket();
  const [inputValue, setInputValue] = useState('');
  const messagesEndRef = useRef(null);

  // Auto-scroll to bottom on new messages
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSubmit = (e) => {
    e.preventDefault();

    if (!inputValue.trim() || !isConnected || isStreaming) {
      return;
    }

    sendMessage(inputValue);
    setInputValue('');
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  return (
    <div style={styles.container}>
      {/* Header */}
      <div style={styles.header}>
        <div style={styles.headerContent}>
          <h2 style={styles.headerTitle}>ShopNest Support</h2>
          <div style={styles.statusIndicator}>
            <div
              style={{
                ...styles.statusDot,
                backgroundColor: isConnected ? '#10b981' : '#ef4444',
              }}
            />
            <span style={styles.statusText}>
              {isConnected ? 'Connected' : 'Connecting...'}
            </span>
          </div>
        </div>
      </div>

      {/* Messages Area */}
      <div style={styles.messagesContainer}>
        {messages.length === 0 && (
          <div style={styles.welcomeMessage}>
            <div style={styles.welcomeIcon}>💬</div>
            <h3 style={styles.welcomeTitle}>Welcome to ShopNest Support!</h3>
            <p style={styles.welcomeText}>
              Hi! I'm ShopNest's AI support assistant. Ask me about your orders or our policies!
            </p>
          </div>
        )}

        {messages.map((message, index) => (
          <div
            key={index}
            style={{
              ...styles.messageWrapper,
              justifyContent: message.role === 'user' ? 'flex-end' : 'flex-start',
            }}
          >
            <div
              style={{
                ...styles.messageBubble,
                ...(message.role === 'user' ? styles.userBubble : styles.aiBubble),
              }}
            >
              <div style={styles.messageContent}>{message.content}</div>
              {message.role === 'ai' && message.streaming && (
                <span style={styles.cursor}>▊</span>
              )}
            </div>
          </div>
        ))}

        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <div style={styles.inputContainer}>
        <form onSubmit={handleSubmit} style={styles.inputForm}>
          <input
            type="text"
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder={
              !isConnected
                ? 'Connecting to support...'
                : isStreaming
                ? 'Waiting for response...'
                : 'Type your message...'
            }
            disabled={!isConnected || isStreaming}
            style={styles.input}
          />
          <button
            type="submit"
            disabled={!inputValue.trim() || !isConnected || isStreaming}
            style={{
              ...styles.sendButton,
              ...((!inputValue.trim() || !isConnected || isStreaming) &&
                styles.sendButtonDisabled),
            }}
          >
            <svg
              style={styles.sendIcon}
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8"
              />
            </svg>
          </button>
        </form>
      </div>
    </div>
  );
};

const styles = {
  container: {
    width: '100%',
    maxWidth: '800px',
    height: '600px',
    backgroundColor: '#ffffff',
    borderRadius: '16px',
    boxShadow: '0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)',
    display: 'flex',
    flexDirection: 'column',
    overflow: 'hidden',
  },

  header: {
    backgroundColor: '#0d9488',
    color: 'white',
    padding: '20px 24px',
    borderBottom: '1px solid rgba(255, 255, 255, 0.1)',
  },

  headerContent: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
  },

  headerTitle: {
    margin: 0,
    fontSize: '20px',
    fontWeight: '600',
  },

  statusIndicator: {
    display: 'flex',
    alignItems: 'center',
    gap: '8px',
  },

  statusDot: {
    width: '8px',
    height: '8px',
    borderRadius: '50%',
    animation: 'pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite',
  },

  statusText: {
    fontSize: '14px',
    opacity: 0.9,
  },

  messagesContainer: {
    flex: 1,
    overflowY: 'auto',
    padding: '24px',
    backgroundColor: '#f9fafb',
  },

  welcomeMessage: {
    textAlign: 'center',
    padding: '60px 20px',
    color: '#6b7280',
  },

  welcomeIcon: {
    fontSize: '48px',
    marginBottom: '16px',
  },

  welcomeTitle: {
    margin: '0 0 12px 0',
    fontSize: '24px',
    fontWeight: '600',
    color: '#0d9488',
  },

  welcomeText: {
    margin: 0,
    fontSize: '16px',
    lineHeight: '1.6',
  },

  messageWrapper: {
    display: 'flex',
    marginBottom: '16px',
  },

  messageBubble: {
    maxWidth: '75%',
    padding: '12px 16px',
    borderRadius: '12px',
    fontSize: '15px',
    lineHeight: '1.5',
    position: 'relative',
  },

  userBubble: {
    backgroundColor: '#0d9488',
    color: 'white',
    borderBottomRightRadius: '4px',
  },

  aiBubble: {
    backgroundColor: 'white',
    color: '#1f2937',
    borderBottomLeftRadius: '4px',
    boxShadow: '0 1px 2px 0 rgba(0, 0, 0, 0.05)',
  },

  messageContent: {
    whiteSpace: 'pre-wrap',
    wordBreak: 'break-word',
  },

  cursor: {
    marginLeft: '2px',
    animation: 'blink 1s infinite',
    color: '#0d9488',
  },

  inputContainer: {
    padding: '20px 24px',
    backgroundColor: 'white',
    borderTop: '1px solid #e5e7eb',
  },

  inputForm: {
    display: 'flex',
    gap: '12px',
  },

  input: {
    flex: 1,
    padding: '12px 16px',
    fontSize: '15px',
    border: '1px solid #d1d5db',
    borderRadius: '8px',
    outline: 'none',
    transition: 'border-color 0.2s',
  },

  sendButton: {
    padding: '12px 20px',
    backgroundColor: '#0d9488',
    color: 'white',
    border: 'none',
    borderRadius: '8px',
    cursor: 'pointer',
    transition: 'background-color 0.2s',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
  },

  sendButtonDisabled: {
    backgroundColor: '#9ca3af',
    cursor: 'not-allowed',
  },

  sendIcon: {
    width: '20px',
    height: '20px',
  },
};

// Add CSS animations
const styleSheet = document.createElement('style');
styleSheet.textContent = `
  @keyframes blink {
    0%, 50% { opacity: 1; }
    51%, 100% { opacity: 0; }
  }

  @keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.5; }
  }

  input:focus {
    border-color: #0d9488 !important;
    box-shadow: 0 0 0 3px rgba(13, 148, 136, 0.1) !important;
  }

  button:hover:not(:disabled) {
    background-color: #0f766e !important;
  }
`;
document.head.appendChild(styleSheet);

export default ChatWidget;
