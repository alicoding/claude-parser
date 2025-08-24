/**
 * @fileoverview Transport factory for creating stream transports
 * @module @claude-parser/stream
 * 
 * ENGINEERING PRINCIPLES:
 * - Factory pattern for transport creation
 * - Type-safe transport selection
 * - 95/5: SSE by default (following industry standard)
 */

import type {
  MessageStreamTransport,
  TransportConfig,
  TransportType
} from './types'
import { SSETransport } from './sse-transport'

/**
 * Create a message stream transport
 * 
 * @example 95% use case - zero config, SSE by default
 * ```typescript
 * const transport = createTransport('/api/stream')
 * transport.connect()
 * ```
 * 
 * @example 5% use case - custom transport
 * ```typescript
 * const transport = createTransport('/api/stream', {
 *   transport: 'websocket',
 *   reconnectInterval: 5000
 * })
 * ```
 */
export function createTransport(
  url: string,
  config: TransportConfig = {}
): MessageStreamTransport {
  const transportType = config.transport ?? 'sse'
  
  switch (transportType) {
    case 'sse':
      return new SSETransport(url, config)
      
    case 'websocket':
      // TODO: Implement WebSocketTransport
      throw new Error('WebSocket transport not yet implemented')
      
    case 'socket.io':
      // TODO: Implement SocketIOTransport  
      throw new Error('Socket.io transport not yet implemented')
      
    default:
      // TypeScript exhaustiveness check
      const _exhaustive: never = transportType
      throw new Error(`Unsupported transport: ${transportType}`)
  }
}

/**
 * Export all transports for direct use (5% use case)
 */
export { SSETransport } from './sse-transport'

/**
 * Re-export types for convenience
 */
export type {
  MessageStreamTransport,
  TransportConfig,
  TransportType,
  StreamMessage,
  ConnectionState,
  TransportEvents,
  MessageHandler,
  ErrorHandler,
  StateChangeHandler,
  ReconnectHandler
} from './types'