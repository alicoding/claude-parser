/**
 * @fileoverview SSE Transport implementation
 * @module @claude-parser/stream
 * 
 * ENGINEERING PRINCIPLES:
 * - ZERO any types (God-mode TypeScript)
 * - 95/5: Dead simple for users, complexity hidden
 * - SOLID: Single responsibility - SSE transport only
 * - DRY: Reusable event handling logic
 */

import type {
  MessageStreamTransport,
  TransportConfig,
  StreamMessage,
  ConnectionState,
  MessageHandler,
  ErrorHandler,
  StateChangeHandler,
  ReconnectHandler
} from './types'

/**
 * Server-Sent Events transport implementation
 * Following Anthropic/OpenAI/Vercel pattern
 * 
 * @example 95% use case - zero config
 * ```typescript
 * const transport = new SSETransport('/api/stream')
 * transport.connect()
 * transport.onMessage(msg => console.log(msg))
 * ```
 */
export class SSETransport implements MessageStreamTransport {
  readonly config: TransportConfig
  private eventSource: EventSource | null = null
  private _state: ConnectionState = 'disconnected'
  private reconnectAttempts = 0
  private reconnectTimer: NodeJS.Timeout | null = null
  
  // Event handlers
  private messageHandlers: Set<MessageHandler> = new Set()
  private errorHandlers: Set<ErrorHandler> = new Set()
  private reconnectHandlers: Set<ReconnectHandler> = new Set()
  private stateChangeHandlers: Set<StateChangeHandler> = new Set()
  
  // Event listener references for cleanup
  private boundMessageHandler: ((event: MessageEvent) => void) | null = null
  private boundErrorHandler: ((event: Event) => void) | null = null
  private boundOpenHandler: ((event: Event) => void) | null = null

  constructor(
    private readonly url: string,
    config: TransportConfig = {}
  ) {
    // Default config with 95/5 principle - sensible defaults
    this.config = {
      transport: 'sse',
      reconnectInterval: 3000,
      maxReconnectAttempts: Infinity,
      debug: false,
      ...config
    }
  }

  /**
   * Get current connection state
   */
  get state(): ConnectionState {
    return this._state
  }

  /**
   * Connect to SSE endpoint
   */
  connect(): void {
    // Prevent multiple connections
    if (this.eventSource && this.eventSource.readyState !== EventSource.CLOSED) {
      if (this.config.debug) {
        console.log('[SSETransport] Already connected or connecting')
      }
      return
    }

    this.setState('connecting')

    try {
      // Build URL with query params if provided
      let connectUrl = this.url
      if (this.config.params) {
        const params = new URLSearchParams(this.config.params)
        connectUrl = `${this.url}?${params.toString()}`
      }

      // Create EventSource
      this.eventSource = new EventSource(connectUrl)

      // Create bound handlers for cleanup
      this.boundMessageHandler = this.handleMessage.bind(this)
      this.boundErrorHandler = this.handleError.bind(this)
      this.boundOpenHandler = this.handleOpen.bind(this)

      // Set up event listeners
      this.eventSource.addEventListener('message', this.boundMessageHandler)
      this.eventSource.addEventListener('error', this.boundErrorHandler)
      this.eventSource.addEventListener('open', this.boundOpenHandler)

    } catch (error) {
      const transportError = new TransportError(
        `Failed to create EventSource: ${error instanceof Error ? error.message : 'Unknown error'}`,
        'INIT_ERROR',
        'sse',
        error instanceof Error ? error : undefined
      )
      this.emitError(transportError)
      this.setState('error')
    }
  }

  /**
   * Disconnect from SSE endpoint
   */
  disconnect(): void {
    // Clear reconnect timer
    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer)
      this.reconnectTimer = null
    }

    // Close EventSource and cleanup
    if (this.eventSource) {
      // Remove event listeners using bound references
      if (this.boundMessageHandler) {
        this.eventSource.removeEventListener('message', this.boundMessageHandler)
      }
      if (this.boundErrorHandler) {
        this.eventSource.removeEventListener('error', this.boundErrorHandler)
      }
      if (this.boundOpenHandler) {
        this.eventSource.removeEventListener('open', this.boundOpenHandler)
      }

      this.eventSource.close()
      this.eventSource = null
    }

    // Reset state
    this.reconnectAttempts = 0
    this.boundMessageHandler = null
    this.boundErrorHandler = null
    this.boundOpenHandler = null
    this.setState('disconnected')
  }

  /**
   * Check if currently connected
   */
  isConnected(): boolean {
    return this.eventSource !== null && 
           this.eventSource.readyState === EventSource.OPEN &&
           this._state === 'connected'
  }

  /**
   * Register message handler
   */
  onMessage(handler: MessageHandler): void {
    this.messageHandlers.add(handler)
  }

  /**
   * Register error handler
   */
  onError(handler: ErrorHandler): void {
    this.errorHandlers.add(handler)
  }

  /**
   * Register reconnection handler
   */
  onReconnect(handler: ReconnectHandler): void {
    this.reconnectHandlers.add(handler)
  }

  /**
   * Register state change handler
   */
  onStateChange(handler: StateChangeHandler): void {
    this.stateChangeHandlers.add(handler)
  }

  /**
   * Handle incoming SSE message
   */
  private handleMessage(event: MessageEvent): void {
    // Ignore empty messages
    if (!event.data || event.data.trim() === '') {
      return
    }

    try {
      // Parse JSON message
      const message: StreamMessage = JSON.parse(event.data)
      
      // Emit to all message handlers
      this.messageHandlers.forEach(handler => handler(message))
      
    } catch (error) {
      // Emit parse error
      const parseError = new TransportError(
        `Failed to parse message: ${error instanceof Error ? error.message : 'Invalid JSON'}`,
        'PARSE_ERROR',
        'sse',
        error instanceof Error ? error : undefined
      )
      this.emitError(parseError)
    }
  }

  /**
   * Handle SSE errors
   */
  private handleError(event: Event): void {
    // Check if this is a connection loss that needs reconnection
    if (this.eventSource && this.eventSource.readyState === EventSource.CLOSED) {
      const error = new TransportError(
        'Connection failed',
        'CONNECTION_ERROR',
        'sse'
      )
      this.emitError(error)
      
      // Attempt reconnection if configured
      this.attemptReconnect()
    }
  }

  /**
   * Handle successful connection
   */
  private handleOpen(event: Event): void {
    this.reconnectAttempts = 0
    this.setState('connected')
    
    if (this.config.debug) {
      console.log('[SSETransport] Connected successfully')
    }
  }

  /**
   * Attempt to reconnect after connection loss
   */
  private attemptReconnect(): void {
    // Check if we should reconnect
    if (this.config.maxReconnectAttempts !== undefined &&
        this.reconnectAttempts >= this.config.maxReconnectAttempts) {
      if (this.config.debug) {
        console.log('[SSETransport] Max reconnect attempts reached')
      }
      this.setState('error')
      return
    }

    this.setState('reconnecting')
    this.reconnectAttempts++

    // Clear existing timer
    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer)
    }

    // Schedule reconnection
    this.reconnectTimer = setTimeout(() => {
      if (this.config.debug) {
        console.log(`[SSETransport] Reconnecting (attempt ${this.reconnectAttempts})`)
      }
      
      // Emit reconnection event
      this.reconnectHandlers.forEach(handler => handler())
      
      // Reconnect
      this.connect()
    }, this.config.reconnectInterval ?? 3000)
  }

  /**
   * Update connection state and notify handlers
   */
  private setState(state: ConnectionState): void {
    if (this._state !== state) {
      this._state = state
      this.stateChangeHandlers.forEach(handler => handler(state))
    }
  }

  /**
   * Emit error to all handlers
   */
  private emitError(error: Error): void {
    this.errorHandlers.forEach(handler => handler(error))
  }
}

/**
 * Custom TransportError implementation
 * (Moved from types.ts to avoid circular dependency)
 */
class TransportError extends Error {
  constructor(
    message: string,
    public readonly code: string,
    public readonly transport: 'sse' | 'websocket' | 'socket.io',
    public readonly originalError?: Error
  ) {
    super(message)
    this.name = 'TransportError'
  }
}