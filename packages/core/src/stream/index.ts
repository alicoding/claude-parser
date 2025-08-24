/**
 * @fileoverview Stream module exports
 * @module @claude-parser/stream
 * 
 * Dead simple streaming for Claude Code messages
 * Following Anthropic/OpenAI/Vercel SSE pattern
 */

// Main factory function (95% use case)
export { createTransport } from './factory'

// Transport implementations (5% use case)
export { SSETransport } from './sse-transport'

// Types for TypeScript users
export type {
  // Core interfaces
  MessageStreamTransport,
  TransportConfig,
  StreamMessage,
  
  // Configuration
  TransportType,
  ConnectionState,
  
  // Event handlers
  TransportEvents,
  MessageHandler,
  ErrorHandler,
  StateChangeHandler,
  ReconnectHandler,
  
  // Factory type
  TransportFactory
} from './types'