/**
 * @fileoverview Transport abstraction layer tests
 * 
 * ENGINEERING PRINCIPLES:
 * - TDD: Tests written before implementation
 * - Transport agnostic design
 * - 95/5: Simple defaults, powerful options
 */

import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import type { 
  MessageStreamTransport,
  TransportConfig,
  StreamMessage,
  TransportEvents
} from '../types'
import { createTransport } from '../factory'
import { SSETransport } from '../sse-transport'

// Real Claude message from the bug report
const REAL_CLAUDE_MESSAGE = {
  parentUuid: "2340e0e7-dbe8-4f7c-9255-1117873d179c",
  isSidechain: false,
  userType: "external",
  cwd: "/Volumes/AliDev/ai-projects/memory",
  sessionId: "6f190dcd-baa8-4cd1-bba9-34ba93bc881b",
  version: "1.0.72",
  gitBranch: "",
  type: "assistant",
  timestamp: "2025-08-11T02:18:28.945Z",
  message: {
    id: "msg_01PVrYziTVTcR3npG17j4ncd",
    type: "message",
    role: "assistant",
    model: "claude-sonnet-4-20250514",
    content: [{
      type: "tool_use",
      id: "toolu_015aFZfsN5r2MxzzKUqJtWfC",
      name: "TodoWrite",
      input: { todos: [] }
    }],
    stop_reason: null,
    stop_sequence: null,
    usage: {
      input_tokens: 3,
      cache_creation_input_tokens: 32299,
      cache_read_input_tokens: 0,
      output_tokens: 226
    }
  },
  requestId: "req_011CS16dDvySBA4fqNFoEFrf",
  uuid: "6d4b27ba-31cd-45b7-a2fd-af43305a0aae"
}

describe('Transport Abstraction Layer', () => {
  describe('Factory Pattern', () => {
    it('creates SSE transport by default (following Anthropic)', () => {
      const transport = createTransport('/api/stream')
      expect(transport).toBeInstanceOf(SSETransport)
    })
    
    it('creates SSE transport when explicitly specified', () => {
      const transport = createTransport('/api/stream', { transport: 'sse' })
      expect(transport).toBeInstanceOf(SSETransport)
    })
    
    it('throws error for unsupported transport (fail fast)', () => {
      expect(() => 
        createTransport('/api/stream', { transport: 'unknown' as any })
      ).toThrow('Unsupported transport: unknown')
    })
    
    it('passes configuration to transport', () => {
      const config = {
        transport: 'sse' as const,
        reconnectInterval: 5000,
        maxReconnectAttempts: 10
      }
      const transport = createTransport('/api/stream', config)
      expect(transport.config).toMatchObject(config)
    })
  })
  
  describe('SSE Transport', () => {
    let transport: SSETransport
    let mockEventSource: any
    
    beforeEach(() => {
      // Mock EventSource
      mockEventSource = {
        addEventListener: vi.fn(),
        removeEventListener: vi.fn(),
        close: vi.fn(),
        readyState: 1, // OPEN
        url: '/api/stream'
      }
      
      global.EventSource = vi.fn(() => mockEventSource) as any
      transport = new SSETransport('/api/stream')
    })
    
    afterEach(() => {
      transport.disconnect()
      vi.clearAllMocks()
    })
    
    describe('Connection Management', () => {
      it('creates EventSource on connect', () => {
        transport.connect()
        expect(global.EventSource).toHaveBeenCalledWith('/api/stream')
      })
      
      it('sets up event listeners on connect', () => {
        transport.connect()
        expect(mockEventSource.addEventListener).toHaveBeenCalledWith('message', expect.any(Function))
        expect(mockEventSource.addEventListener).toHaveBeenCalledWith('error', expect.any(Function))
        expect(mockEventSource.addEventListener).toHaveBeenCalledWith('open', expect.any(Function))
      })
      
      it('closes EventSource on disconnect', () => {
        transport.connect()
        transport.disconnect()
        expect(mockEventSource.close).toHaveBeenCalled()
      })
      
      it('removes event listeners on disconnect', () => {
        transport.connect()
        const messageHandler = mockEventSource.addEventListener.mock.calls[0][1]
        transport.disconnect()
        expect(mockEventSource.removeEventListener).toHaveBeenCalledWith('message', messageHandler)
      })
      
      it('prevents multiple simultaneous connections', () => {
        transport.connect()
        transport.connect() // Should not create another EventSource
        expect(global.EventSource).toHaveBeenCalledTimes(1)
      })
    })
    
    describe('Message Handling', () => {
      it('parses and validates incoming messages', (done) => {
        const messageHandler = vi.fn((msg: StreamMessage) => {
          expect(msg).toEqual(REAL_CLAUDE_MESSAGE)
          done()
        })
        
        transport.onMessage(messageHandler)
        transport.connect()
        
        // Simulate SSE message
        const messageListener = mockEventSource.addEventListener.mock.calls[0][1]
        messageListener({ data: JSON.stringify(REAL_CLAUDE_MESSAGE) })
      })
      
      it('handles malformed JSON gracefully', () => {
        const errorHandler = vi.fn()
        
        transport.onError(errorHandler)
        transport.connect()
        
        const messageListener = mockEventSource.addEventListener.mock.calls[0][1]
        messageListener({ data: 'not valid json' })
        
        expect(errorHandler).toHaveBeenCalledWith(
          expect.objectContaining({
            message: expect.stringContaining('Failed to parse message')
          })
        )
      })
      
      it('ignores empty messages', () => {
        const messageHandler = vi.fn()
        transport.onMessage(messageHandler)
        transport.connect()
        
        const messageListener = mockEventSource.addEventListener.mock.calls[0][1]
        messageListener({ data: '' })
        
        expect(messageHandler).not.toHaveBeenCalled()
      })
    })
    
    describe('Reconnection Logic', () => {
      it('automatically reconnects on connection loss', (done) => {
        const reconnectHandler = vi.fn(() => {
          expect(reconnectHandler).toHaveBeenCalled()
          done()
        })
        
        transport.onReconnect(reconnectHandler)
        transport.connect()
        
        // Simulate connection error
        mockEventSource.readyState = 2 // CLOSED
        const errorListener = mockEventSource.addEventListener.mock.calls[1][1]
        errorListener(new Event('error'))
        
        // Fast-forward reconnect timer
        setTimeout(() => {
          expect(global.EventSource).toHaveBeenCalledTimes(2)
        }, 100)
      })
      
      it('respects maxReconnectAttempts', () => {
        transport = new SSETransport('/api/stream', { 
          maxReconnectAttempts: 2,
          reconnectInterval: 10 
        })
        transport.connect()
        
        // Simulate multiple connection failures
        for (let i = 0; i < 3; i++) {
          mockEventSource.readyState = 2
          const errorListener = mockEventSource.addEventListener.mock.calls[1][1]
          errorListener(new Event('error'))
        }
        
        // Should stop trying after 2 attempts
        setTimeout(() => {
          expect(global.EventSource).toHaveBeenCalledTimes(2)
        }, 100)
      })
      
      it('emits connection state changes', () => {
        const stateHandler = vi.fn()
        transport.onStateChange(stateHandler)
        transport.connect()
        
        expect(stateHandler).toHaveBeenCalledWith('connecting')
        
        const openListener = mockEventSource.addEventListener.mock.calls[2][1]
        openListener(new Event('open'))
        
        expect(stateHandler).toHaveBeenCalledWith('connected')
      })
    })
    
    describe('Error Handling', () => {
      it('emits network errors', (done) => {
        const errorHandler = vi.fn((error: Error) => {
          expect(error.message).toContain('Connection failed')
          done()
        })
        
        transport.onError(errorHandler)
        transport.connect()
        
        const errorListener = mockEventSource.addEventListener.mock.calls[1][1]
        errorListener(new Event('error'))
      })
      
      it('handles EventSource creation failure', () => {
        global.EventSource = vi.fn(() => {
          throw new Error('EventSource not supported')
        }) as any
        
        const errorHandler = vi.fn()
        transport.onError(errorHandler)
        transport.connect()
        
        expect(errorHandler).toHaveBeenCalledWith(
          expect.objectContaining({
            message: expect.stringContaining('EventSource not supported')
          })
        )
      })
    })
  })
  
  describe('Transport Interface Contract', () => {
    it('all transports must implement MessageStreamTransport interface', () => {
      const transport = createTransport('/api/stream')
      
      // Check all required methods exist
      expect(typeof transport.connect).toBe('function')
      expect(typeof transport.disconnect).toBe('function')
      expect(typeof transport.onMessage).toBe('function')
      expect(typeof transport.onError).toBe('function')
      expect(typeof transport.onReconnect).toBe('function')
      expect(typeof transport.onStateChange).toBe('function')
      expect(typeof transport.isConnected).toBe('function')
    })
    
    it('validates transport configuration', () => {
      const validConfig: TransportConfig = {
        transport: 'sse',
        reconnectInterval: 3000,
        maxReconnectAttempts: 5,
        headers: { 'Authorization': 'Bearer token' }
      }
      
      expect(() => createTransport('/api/stream', validConfig)).not.toThrow()
    })
  })
})

describe('Message Validation', () => {
  let mockEventSource: any
  
  beforeEach(() => {
    // Mock EventSource for these tests
    mockEventSource = {
      addEventListener: vi.fn(),
      removeEventListener: vi.fn(),
      close: vi.fn(),
      readyState: 1,
      url: '/api/stream'
    }
    
    global.EventSource = vi.fn(() => mockEventSource) as any
  })
  
  it('validates real Claude message structure', () => {
    const transport = new SSETransport('/api/stream')
    const messageHandler = vi.fn()
    
    transport.onMessage(messageHandler)
    transport.connect()
    
    // Get the actual message listener
    const messageListener = mockEventSource.addEventListener.mock.calls[0][1]
    
    // Send valid message
    messageListener({ data: JSON.stringify(REAL_CLAUDE_MESSAGE) })
    
    expect(messageHandler).toHaveBeenCalledWith(
      expect.objectContaining({
        type: 'assistant',
        message: expect.objectContaining({
          role: 'assistant',
          content: expect.any(Array)
        })
      })
    )
  })
  
  it('handles tool_use messages correctly', () => {
    const transport = new SSETransport('/api/stream')
    const messageHandler = vi.fn()
    
    transport.onMessage(messageHandler)
    transport.connect()
    
    const messageListener = mockEventSource.addEventListener.mock.calls[0][1]
    
    messageListener({ data: JSON.stringify(REAL_CLAUDE_MESSAGE) })
    
    const receivedMessage = messageHandler.mock.calls[0][0]
    expect(receivedMessage.message.content[0].type).toBe('tool_use')
    expect(receivedMessage.message.content[0].name).toBe('TodoWrite')
  })
})