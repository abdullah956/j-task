import { useState, useEffect, useRef, useCallback } from 'react';

const useWebSocket = () => {
  // Generate random session ID on first load
  const [sessionId] = useState(() => {
    return `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  });

  const [messages, setMessages] = useState([]);
  const [isConnected, setIsConnected] = useState(false);
  const [isStreaming, setIsStreaming] = useState(false);
  const wsRef = useRef(null);
  const reconnectTimeoutRef = useRef(null);

  // Connect to WebSocket
  const connect = useCallback(() => {
    try {
      const ws = new WebSocket(`ws://localhost:8000/ws/${sessionId}`);

      ws.onopen = () => {
        console.log('WebSocket connected');
        setIsConnected(true);
      };

      ws.onmessage = (event) => {
        const data = event.data;

        // Check for end-of-stream sentinel
        if (data === '__END__') {
          setIsStreaming(false);
          // Mark the last message as no longer streaming
          setMessages((prevMessages) => {
            if (prevMessages.length === 0) return prevMessages;
            const lastMessage = prevMessages[prevMessages.length - 1];
            if (lastMessage && lastMessage.role === 'ai' && lastMessage.streaming) {
              return [
                ...prevMessages.slice(0, -1),
                {
                  ...lastMessage,
                  streaming: false,
                },
              ];
            }
            return prevMessages;
          });
          return;
        }

        // Append token to last AI message or create new one
        setMessages((prevMessages) => {
          const lastMessage = prevMessages[prevMessages.length - 1];

          if (lastMessage && lastMessage.role === 'ai' && lastMessage.streaming) {
            // Append to existing streaming message
            return [
              ...prevMessages.slice(0, -1),
              {
                ...lastMessage,
                content: lastMessage.content + data,
              },
            ];
          } else {
            // Create new AI message
            return [
              ...prevMessages,
              {
                role: 'ai',
                content: data,
                streaming: true,
                timestamp: new Date(),
              },
            ];
          }
        });
      };

      ws.onerror = (error) => {
        console.error('WebSocket error:', error);
      };

      ws.onclose = () => {
        console.log('WebSocket disconnected');
        setIsConnected(false);

        // Attempt to reconnect after 3 seconds
        reconnectTimeoutRef.current = setTimeout(() => {
          console.log('Attempting to reconnect...');
          connect();
        }, 3000);
      };

      wsRef.current = ws;
    } catch (error) {
      console.error('Failed to connect:', error);
      setIsConnected(false);
    }
  }, [sessionId]);

  // Send message via WebSocket
  const sendMessage = useCallback((text) => {
    if (!wsRef.current || wsRef.current.readyState !== WebSocket.OPEN) {
      console.error('WebSocket not connected');
      return;
    }

    // Add user message to messages
    setMessages((prev) => [
      ...prev,
      {
        role: 'user',
        content: text,
        timestamp: new Date(),
      },
    ]);

    // Send message to server
    const message = JSON.stringify({ message: text });
    wsRef.current.send(message);

    // Set streaming state
    setIsStreaming(true);
  }, []);

  // Initialize WebSocket connection
  useEffect(() => {
    connect();

    // Cleanup on unmount
    return () => {
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
      }
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, [connect]);

  return {
    sendMessage,
    messages,
    isConnected,
    isStreaming,
    sessionId,
  };
};

export default useWebSocket;
