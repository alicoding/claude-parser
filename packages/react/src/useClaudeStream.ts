/**
 * @fileoverview React hook for streaming Claude messages
 * @module @claude-parser/react
 * 
 * ENGINEERING PRINCIPLES:
 * - Dead simple API (95/5 principle)
 * - Automatic cleanup on unmount
 * - Type-safe with full autocomplete
 * - Zero configuration required
 */

import { useEffect, useRef, useState, useCallback } from 'react'
import { 
  createTransport,
  groupToolOperations,
  type StreamMessage,
  type TransportConfig,
  type MessageStreamTransport,
  type ToolOperation
} from '@claude-parser/core'

/**
 * Hook state and return value
 */
export interface UseClaudeStreamState {
  /** All messages received */
  messages: StreamMessage[]
  
  /** Grouped tool operations */
  toolOperations: ToolOperation[]
  
  /** Connection status */
  isConnected: boolean
  
  /** Loading state (connecting) */
  isLoading: boolean
  
  /** Error state */
  error: string | null
  
  /** Reconnection attempt count */
  reconnectCount: number
  
  /** Manual reconnect function */
  reconnect: () => void
  
  /** Manual disconnect function */
  disconnect: () => void
  
  /** Clear all messages */
  clear: () => void
}

/**
 * Hook options
 */
export interface UseClaudeStreamOptions extends TransportConfig {
  /** Auto-connect on mount (default: true) */
  autoConnect?: boolean
  
  /** Maximum messages to keep (default: 1000) */
  maxMessages?: number
  
  /** Message filter function */
  messageFilter?: (message: StreamMessage) => boolean
  
  /** Callback for new messages */
  onMessage?: (message: StreamMessage) => void
  
  /** Callback for connection state changes */
  onConnectionChange?: (connected: boolean) => void
  
  /** Callback for errors */
  onError?: (error: Error) => void
}

/**
 * React hook for streaming Claude messages
 * 
 * @example 95% use case - zero config
 * ```typescript
 * function ChatView() {
 *   const { messages, toolOperations, isConnected } = useClaudeStream('/api/stream')
 *   
 *   return (
 *     <div>
 *       {messages.map(msg => <Message key={msg.uuid} {...msg} />)}
 *     </div>
 *   )
 * }
 * ```
 * 
 * @example 5% use case - with options
 * ```typescript
 * const { messages, reconnect } = useClaudeStream('/api/stream', {
 *   maxMessages: 500,
 *   reconnectInterval: 5000,
 *   onMessage: (msg) => console.log('New message:', msg)
 * })
 * ```
 */
export function useClaudeStream(
  url: string,
  options: UseClaudeStreamOptions = {}
): UseClaudeStreamState {
  // Default options
  const {
    autoConnect = true,
    maxMessages = 1000,
    messageFilter,
    onMessage,
    onConnectionChange,
    onError,
    ...transportConfig
  } = options
  
  // State
  const [messages, setMessages] = useState<StreamMessage[]>([])
  const [toolOperations, setToolOperations] = useState<ToolOperation[]>([])
  const [isConnected, setIsConnected] = useState(false)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [reconnectCount, setReconnectCount] = useState(0)
  
  // Refs for stable references
  const transportRef = useRef<MessageStreamTransport | null>(null)
  const messagesRef = useRef<StreamMessage[]>([])
  
  // Update tool operations when messages change
  useEffect(() => {
    const operations = groupToolOperations(messages)
    setToolOperations(operations)
  }, [messages])
  
  // Handle incoming messages
  const handleMessage = useCallback((message: StreamMessage) => {
    // Apply filter if provided
    if (messageFilter && !messageFilter(message)) {
      return
    }
    
    // Update messages
    setMessages(prev => {
      const newMessages = [...prev, message]
      
      // Limit message count
      if (newMessages.length > maxMessages) {
        newMessages.splice(0, newMessages.length - maxMessages)
      }
      
      messagesRef.current = newMessages
      return newMessages
    })
    
    // Call user callback
    onMessage?.(message)
  }, [messageFilter, maxMessages, onMessage])
  
  // Handle connection state changes
  const handleConnectionChange = useCallback((connected: boolean) => {
    setIsConnected(connected)
    setIsLoading(false)
    
    if (connected) {
      setError(null)
    }
    
    onConnectionChange?.(connected)
  }, [onConnectionChange])
  
  // Handle errors
  const handleError = useCallback((err: Error) => {
    setError(err.message)
    setIsLoading(false)
    onError?.(err)
  }, [onError])
  
  // Handle reconnection
  const handleReconnect = useCallback(() => {
    setReconnectCount(prev => prev + 1)
  }, [])
  
  // Create and connect transport
  const connect = useCallback(() => {
    // Clean up existing transport
    if (transportRef.current) {
      transportRef.current.disconnect()
    }
    
    setIsLoading(true)
    setError(null)
    
    try {
      // Create transport
      const transport = createTransport(url, transportConfig)
      
      // Set up event handlers
      transport.onMessage(handleMessage)
      transport.onError(handleError)
      transport.onReconnect(handleReconnect)
      transport.onStateChange(state => {
        handleConnectionChange(state === 'connected')
        if (state === 'connecting') {
          setIsLoading(true)
        }
      })
      
      // Connect
      transport.connect()
      
      // Store reference
      transportRef.current = transport
      
    } catch (err) {
      handleError(err instanceof Error ? err : new Error(String(err)))
    }
  }, [url, transportConfig, handleMessage, handleError, handleReconnect, handleConnectionChange])
  
  // Disconnect transport
  const disconnect = useCallback(() => {
    if (transportRef.current) {
      transportRef.current.disconnect()
      transportRef.current = null
      setIsConnected(false)
      setIsLoading(false)
    }
  }, [])
  
  // Manual reconnect
  const reconnect = useCallback(() => {
    disconnect()
    connect()
  }, [disconnect, connect])
  
  // Clear messages
  const clear = useCallback(() => {
    setMessages([])
    setToolOperations([])
    messagesRef.current = []
  }, [])
  
  // Auto-connect on mount
  useEffect(() => {
    if (autoConnect) {
      connect()
    }
    
    // Cleanup on unmount
    return () => {
      disconnect()
    }
  }, []) // Only run on mount/unmount
  
  // Return hook state
  return {
    messages,
    toolOperations,
    isConnected,
    isLoading,
    error,
    reconnectCount,
    reconnect,
    disconnect,
    clear
  }
}

/**
 * Hook for filtering messages by type
 */
export function useFilteredMessages(
  messages: StreamMessage[],
  type: StreamMessage['type'] | StreamMessage['type'][]
): StreamMessage[] {
  const types = Array.isArray(type) ? type : [type]
  
  return messages.filter(msg => types.includes(msg.type))
}

/**
 * Hook for getting only the latest N messages
 */
export function useLatestMessages(
  messages: StreamMessage[],
  count: number
): StreamMessage[] {
  return messages.slice(-count)
}

/**
 * Hook for getting messages in a specific session
 */
export function useSessionMessages(
  messages: StreamMessage[],
  sessionId: string
): StreamMessage[] {
  return messages.filter(msg => msg.sessionId === sessionId)
}