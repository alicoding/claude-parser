/**
 * @fileoverview Type definitions for streaming transport layer
 * @module @claude-parser/stream
 * 
 * ENGINEERING PRINCIPLES:
 * - Transport agnostic interfaces (SOLID - Interface Segregation)
 * - Clear separation of concerns (DDD)
 * - Type-first development
 */

// ============================================================================
// CORE MESSAGE TYPES
// ============================================================================

/**
 * Real Claude message structure from WebSocket/SSE
 * This matches the exact format from claude-code
 */
export interface StreamMessage {
  parentUuid: string
  isSidechain: boolean
  userType: string
  cwd: string
  sessionId: string
  version: string
  gitBranch: string
  type: 'user' | 'assistant' | 'system' | 'tool_use' | 'tool_result'
  timestamp: string
  message: {
    id: string
    type: string
    role: string
    model?: string
    content: Array<{
      type: string
      id?: string
      name?: string
      input?: Record<string, unknown>
      text?: string
      [key: string]: unknown
    }>
    stop_reason: string | null
    stop_sequence: string | null
    usage?: {
      input_tokens: number
      cache_creation_input_tokens?: number
      cache_read_input_tokens?: number
      output_tokens: number
      service_tier?: string
    }
  }
  requestId: string
  uuid: string
}

// ============================================================================
// TRANSPORT CONFIGURATION
// ============================================================================

/**
 * Transport types supported by the SDK
 */
export type TransportType = 'sse' | 'websocket' | 'socket.io'

/**
 * Configuration for transport layer
 */
export interface TransportConfig {
  /** Transport type to use (default: 'sse') */
  transport?: TransportType
  
  /** Reconnection interval in milliseconds (default: 3000) */
  reconnectInterval?: number
  
  /** Maximum reconnection attempts (default: Infinity) */
  maxReconnectAttempts?: number
  
  /** Custom headers for HTTP-based transports */
  headers?: Record<string, string>
  
  /** Query parameters to append to URL */
  params?: Record<string, string>
  
  /** Enable debug logging */
  debug?: boolean
}

// ============================================================================
// CONNECTION STATES
// ============================================================================

/**
 * Connection states for transport
 */
export type ConnectionState = 
  | 'disconnected'
  | 'connecting'
  | 'connected'
  | 'reconnecting'
  | 'error'

// ============================================================================
// TRANSPORT EVENTS
// ============================================================================

/**
 * Event handlers for transport layer
 */
export interface TransportEvents {
  onMessage: (message: StreamMessage) => void
  onError: (error: Error) => void
  onReconnect: () => void
  onStateChange: (state: ConnectionState) => void
}

// ============================================================================
// TRANSPORT INTERFACE
// ============================================================================

/**
 * Core transport interface - all transports must implement this
 * SOLID: Interface Segregation Principle
 */
export interface MessageStreamTransport {
  /** Transport configuration */
  readonly config: TransportConfig
  
  /** Current connection state */
  readonly state: ConnectionState
  
  /** Connect to the stream */
  connect(): void
  
  /** Disconnect from the stream */
  disconnect(): void
  
  /** Check if currently connected */
  isConnected(): boolean
  
  /** Register message handler */
  onMessage(handler: (message: StreamMessage) => void): void
  
  /** Register error handler */
  onError(handler: (error: Error) => void): void
  
  /** Register reconnection handler */
  onReconnect(handler: () => void): void
  
  /** Register state change handler */
  onStateChange(handler: (state: ConnectionState) => void): void
}

// ============================================================================
// FACTORY TYPES
// ============================================================================

/**
 * Transport factory function signature
 */
export type TransportFactory = (
  url: string,
  config?: TransportConfig
) => MessageStreamTransport

// ============================================================================
// ERROR TYPES
// ============================================================================

/**
 * Custom error for transport failures
 */
export class TransportError extends Error {
  constructor(
    message: string,
    public readonly code: string,
    public readonly transport: TransportType,
    public readonly originalError?: Error
  ) {
    super(message)
    this.name = 'TransportError'
  }
}

// ============================================================================
// UTILITY TYPES
// ============================================================================

/**
 * Message handler function signature
 */
export type MessageHandler = (message: StreamMessage) => void

/**
 * Error handler function signature
 */
export type ErrorHandler = (error: Error) => void

/**
 * State change handler function signature
 */
export type StateChangeHandler = (state: ConnectionState) => void

/**
 * Reconnect handler function signature
 */
export type ReconnectHandler = () => void