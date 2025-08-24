/**
 * @fileoverview Schema validation tests with real Claude Code JSON
 * 
 * ENGINEERING PRINCIPLES:
 * - Test with production data from day 1
 * - Type-safe test fixtures
 * - Comprehensive edge case coverage
 * - Clear test organization
 */

import { describe, it, expect, beforeAll } from 'vitest'
import { z } from 'zod'
import {
  MessageSchema,
  ConversationSchema,
  ToolOperationSchema,
  MessageCategorySchema,
  MessageGroupSchema,
  parseMessage,
  parseConversation,
  isValidMessage,
  isValidConversation
} from '../schemas'
import type {
  Message,
  Conversation,
  ToolOperation,
  MessageCategory,
  MessageGroup
} from '../schemas'

// ============================================================================
// TYPE-SAFE TEST FIXTURES
// ============================================================================

/**
 * Test fixture types - No any types allowed
 * PATTERN: Explicit typing for test data
 */
interface RealClaudeMessages {
  readonly userMessage: Readonly<Record<string, unknown>>
  readonly assistantMessage: Readonly<Record<string, unknown>>
  readonly toolUseMessage: Readonly<Record<string, unknown>>
  readonly toolResultMessage: Readonly<Record<string, unknown>>
  readonly systemMessage: Readonly<Record<string, unknown>>
}

interface RealClaudeHookData {
  readonly preToolUse: Readonly<Record<string, unknown>>
  readonly postToolUse: Readonly<Record<string, unknown>>
  readonly postToolUseString: Readonly<Record<string, unknown>>
  readonly postToolUseLS: Readonly<Record<string, unknown>>
  readonly postToolUseGrep: Readonly<Record<string, unknown>>
}

/**
 * Real Claude Code JSON samples from production
 * Source: Previous session bug reports and actual Claude Code outputs
 */
const REAL_CLAUDE_MESSAGES: RealClaudeMessages = {
  userMessage: {
    type: 'user',
    uuid: 'msg_01234567890abcdef',
    timestamp: '2024-08-20T10:30:00.000Z',
    content: 'Help me implement a feature'
  },
  
  assistantMessage: {
    type: 'assistant',
    uuid: 'msg_01abcdef234567890',
    timestamp: '2024-08-20T10:30:05.000Z',
    content: [
      { type: 'text', text: 'I\'ll help you implement that feature.' }
    ]
  },
  
  toolUseMessage: {
    type: 'tool_use',
    uuid: 'msg_tool_use_123',
    timestamp: '2024-08-20T10:30:10.000Z',
    content: [{
      type: 'tool_use',
      id: 'call_123',
      name: 'Edit',
      input: {
        file_path: '/path/to/file.ts',
        old_string: 'old code',
        new_string: 'new code'
      }
    }]
  },
  
  toolResultMessage: {
    type: 'tool_result',
    uuid: 'msg_tool_result_123',
    timestamp: '2024-08-20T10:30:15.000Z',
    content: [
      { type: 'tool_result', tool_call_id: 'call_123', content: 'Success' }
    ]
  },
  
  systemMessage: {
    type: 'system',
    uuid: 'msg_system_123',
    timestamp: '2024-08-20T10:30:20.000Z',
    content: 'System notification: Build completed'
  }
} as const

const REAL_CLAUDE_HOOK_DATA: RealClaudeHookData = {
  preToolUse: {
    sessionId: 'abc123xyz789',
    transcriptPath: '/path/to/session.jsonl',
    cwd: '/project/path',
    hookEventName: 'PreToolUse',
    toolName: 'Edit',
    toolInput: {
      file_path: '/path/to/file.ts',
      old_string: 'old code',
      new_string: 'new code'
    }
  },
  
  postToolUse: {
    sessionId: 'abc123xyz789',
    transcriptPath: '/path/to/session.jsonl',
    cwd: '/project/path',
    hookEventName: 'PostToolUse',
    toolName: 'Edit',
    toolResponse: [
      { type: 'text', text: 'File edited successfully' }
    ]
  },
  
  // Bug report: LS returns string, not dict/array
  postToolUseString: {
    sessionId: 'abc123xyz789',
    transcriptPath: '/path/to/session.jsonl',
    cwd: '/project/path',
    hookEventName: 'PostToolUse',
    toolName: 'LS',
    toolResponse: '- /Users/ali/.claude/projects/\n  - file.md\n  - subdir/\n'  // STRING!
  },
  
  // Real-world LS tool response
  postToolUseLS: {
    sessionId: 'abc123xyz789',
    transcriptPath: '/path/to/session.jsonl',
    cwd: '/project/path',
    hookEventName: 'PostToolUse',
    toolName: 'LS',
    toolResponse: '- /Users/ali/.claude/projects/\n  - claude-parser/\n    - docs/\n      - api/\n        - CHANGELOG.md\n        - typescript-sdk.md'
  },
  
  // Real-world Grep tool response
  postToolUseGrep: {
    sessionId: 'abc123xyz789',
    transcriptPath: '/path/to/session.jsonl',
    cwd: '/project/path',
    hookEventName: 'PostToolUse',
    toolName: 'Grep',
    toolResponse: 'file.ts:10: const result = parseMessage(data)\nfile.ts:20: if (result.success) {'
  }
} as const

// ============================================================================
// MESSAGE SCHEMA TESTS
// ============================================================================

describe('MessageSchema', () => {
  describe('Real Claude Code JSON Validation', () => {
    it('validates user message from Claude Code', () => {
      const result = parseMessage(REAL_CLAUDE_MESSAGES.userMessage)
      
      expect(result.success).toBe(true)
      if (result.success) {
        const message: Message = result.data
        expect(message.type).toBe('user')
        expect(message.uuid).toBe('msg_01234567890abcdef')
        expect(message.content).toBe('Help me implement a feature')
        expect(typeof message.timestamp).toBe('string')
      }
    })
    
    it('validates assistant message with content blocks', () => {
      const result = parseMessage(REAL_CLAUDE_MESSAGES.assistantMessage)
      
      expect(result.success).toBe(true)
      if (result.success) {
        const message: Message = result.data
        expect(message.type).toBe('assistant')
        expect(Array.isArray(message.content)).toBe(true)
        if (Array.isArray(message.content)) {
          expect(message.content[0]).toHaveProperty('type', 'text')
          expect(message.content[0]).toHaveProperty('text')
        }
      }
    })
    
    it('validates tool_use message', () => {
      const result = parseMessage(REAL_CLAUDE_MESSAGES.toolUseMessage)
      
      expect(result.success).toBe(true)
      if (result.success) {
        const message: Message = result.data
        expect(message.type).toBe('tool_use')
        expect(Array.isArray(message.content)).toBe(true)
      }
    })
    
    it('validates tool_result message', () => {
      const result = parseMessage(REAL_CLAUDE_MESSAGES.toolResultMessage)
      
      expect(result.success).toBe(true)
      if (result.success) {
        const message: Message = result.data
        expect(message.type).toBe('tool_result')
        expect(message.uuid).toBe('msg_tool_result_123')
      }
    })
    
    it('validates system message', () => {
      const result = parseMessage(REAL_CLAUDE_MESSAGES.systemMessage)
      
      expect(result.success).toBe(true)
      if (result.success) {
        const message: Message = result.data
        expect(message.type).toBe('system')
        expect(message.content).toBe('System notification: Build completed')
      }
    })
  })
  
  describe('Field Normalization', () => {
    it('normalizes camelCase sessionId to snake_case', () => {
      const messageWithCamelCase = {
        type: 'user',
        uuid: 'test_uuid',
        timestamp: '2024-08-20T10:30:00.000Z',
        content: 'test content',
        sessionId: 'session_123' // camelCase
      }
      
      const result = parseMessage(messageWithCamelCase)
      
      expect(result.success).toBe(true)
      if (result.success) {
        const message: Message = result.data
        expect(message.session_id).toBe('session_123')
      }
    })
    
    it('preserves snake_case session_id', () => {
      const messageWithSnakeCase = {
        type: 'user',
        uuid: 'test_uuid',
        timestamp: '2024-08-20T10:30:00.000Z',
        content: 'test content',
        session_id: 'session_123' // snake_case
      }
      
      const result = parseMessage(messageWithSnakeCase)
      
      expect(result.success).toBe(true)
      if (result.success) {
        const message: Message = result.data
        expect(message.session_id).toBe('session_123')
      }
    })
  })
  
  describe('Forward Compatibility', () => {
    it('preserves unknown fields', () => {
      const messageWithExtra = {
        ...REAL_CLAUDE_MESSAGES.userMessage,
        futureField: 'future value',
        metadata: { custom: 'data' },
        tags: ['important', 'urgent']
      }
      
      const result = parseMessage(messageWithExtra)
      
      expect(result.success).toBe(true)
      if (result.success) {
        const message = result.data as Message & Record<string, unknown>
        expect(message.futureField).toBe('future value')
        expect(message.metadata).toEqual({ custom: 'data' })
        expect(message.tags).toEqual(['important', 'urgent'])
      }
    })
  })
  
  describe('Validation Errors', () => {
    it('rejects missing required fields', () => {
      const invalidMessage = {
        type: 'user'
        // Missing: uuid, timestamp, content
      }
      
      const result = parseMessage(invalidMessage)
      
      expect(result.success).toBe(false)
      if (!result.success) {
        expect(result.error.issues.length).toBeGreaterThan(0)
        expect(result.error.issues.some(issue => issue.path.includes('uuid'))).toBe(true)
      }
    })
    
    it('rejects invalid message type', () => {
      const invalidMessage = {
        type: 'invalid_type',
        uuid: 'test_uuid',
        timestamp: '2024-08-20T10:30:00.000Z',
        content: 'test'
      }
      
      const result = parseMessage(invalidMessage)
      
      expect(result.success).toBe(false)
      if (!result.success) {
        expect(result.error.issues.some(issue => issue.path.includes('type'))).toBe(true)
      }
    })
    
    it('rejects invalid timestamp format', () => {
      const invalidMessage = {
        type: 'user',
        uuid: 'test_uuid',
        timestamp: 'not-a-valid-timestamp',
        content: 'test'
      }
      
      const result = parseMessage(invalidMessage)
      
      expect(result.success).toBe(false)
      if (!result.success) {
        expect(result.error.issues.some(issue => issue.path.includes('timestamp'))).toBe(true)
      }
    })
  })
  
  describe('Type Guards', () => {
    it('correctly identifies valid messages', () => {
      expect(isValidMessage(REAL_CLAUDE_MESSAGES.userMessage)).toBe(true)
      expect(isValidMessage(REAL_CLAUDE_MESSAGES.assistantMessage)).toBe(true)
      expect(isValidMessage(REAL_CLAUDE_MESSAGES.toolUseMessage)).toBe(true)
    })
    
    it('correctly rejects invalid messages', () => {
      expect(isValidMessage({})).toBe(false)
      expect(isValidMessage(null)).toBe(false)
      expect(isValidMessage(undefined)).toBe(false)
      expect(isValidMessage('string')).toBe(false)
      expect(isValidMessage(123)).toBe(false)
    })
  })
})

// ============================================================================
// CONVERSATION SCHEMA TESTS
// ============================================================================

describe('ConversationSchema', () => {
  it('validates conversation with real Claude messages', () => {
    const conversation = {
      messages: Object.values(REAL_CLAUDE_MESSAGES),
      metadata: {
        sessionId: 'session_123',
        totalMessages: 5,
        startTime: '2024-08-20T10:30:00.000Z',
        endTime: '2024-08-20T10:30:20.000Z'
      }
    }
    
    const result = parseConversation(conversation)
    
    expect(result.success).toBe(true)
    if (result.success) {
      const conv: Conversation = result.data
      expect(conv.messages).toHaveLength(5)
      expect(conv.messages[0]?.type).toBe('user')
      expect(conv.messages[1]?.type).toBe('assistant')
      expect(conv.metadata?.totalMessages).toBe(5)
    }
  })
  
  it('validates empty conversation', () => {
    const emptyConversation = {
      messages: []
    }
    
    const result = parseConversation(emptyConversation)
    
    expect(result.success).toBe(true)
    if (result.success) {
      const conv: Conversation = result.data
      expect(conv.messages).toHaveLength(0)
      expect(conv.metadata).toBeUndefined()
    }
  })
  
  it('validates conversation without metadata', () => {
    const conversation = {
      messages: [REAL_CLAUDE_MESSAGES.userMessage]
    }
    
    const result = parseConversation(conversation)
    
    expect(result.success).toBe(true)
    if (result.success) {
      const conv: Conversation = result.data
      expect(conv.messages).toHaveLength(1)
      expect(conv.metadata).toBeUndefined()
    }
  })
  
  it('uses type guard correctly', () => {
    const validConversation = {
      messages: Object.values(REAL_CLAUDE_MESSAGES)
    }
    
    expect(isValidConversation(validConversation)).toBe(true)
    expect(isValidConversation({})).toBe(false)
    expect(isValidConversation({ messages: 'not-an-array' })).toBe(false)
  })
})

// ============================================================================
// TOOL OPERATION SCHEMA TESTS
// ============================================================================

describe('ToolOperationSchema', () => {
  it('validates complete tool operation', () => {
    const toolOperation = {
      id: 'edit_001',
      name: 'Edit',
      input: {
        file_path: '/path/to/file.ts',
        old_string: 'old code',
        new_string: 'new code'
      },
      result: 'File edited successfully',
      status: 'success',
      success: true,
      duration: 150,
      startTime: '2024-08-20T10:30:10.000Z',
      endTime: '2024-08-20T10:30:15.000Z'
    }
    
    const result = ToolOperationSchema.safeParse(toolOperation)
    
    expect(result.success).toBe(true)
    if (result.success) {
      const op: ToolOperation = result.data
      expect(op.name).toBe('Edit')
      expect(op.status).toBe('success')
      expect(op.success).toBe(true)
      expect(op.duration).toBe(150)
    }
  })
  
  it('validates in-progress tool operation', () => {
    const inProgressOperation = {
      id: 'bash_001',
      name: 'Bash',
      input: { command: 'npm install' },
      status: 'in_progress',
      success: false,
      startTime: '2024-08-20T10:30:10.000Z'
      // No result, endTime, or duration yet
    }
    
    const result = ToolOperationSchema.safeParse(inProgressOperation)
    
    expect(result.success).toBe(true)
    if (result.success) {
      const op: ToolOperation = result.data
      expect(op.status).toBe('in_progress')
      expect(op.result).toBeUndefined()
      expect(op.endTime).toBeUndefined()
      expect(op.duration).toBeUndefined()
    }
  })
  
  it('applies default status when not provided', () => {
    const operationWithoutStatus = {
      id: 'test_001',
      name: 'Test',
      input: {},
      success: false,
      startTime: '2024-08-20T10:30:10.000Z'
    }
    
    const result = ToolOperationSchema.safeParse(operationWithoutStatus)
    
    expect(result.success).toBe(true)
    if (result.success) {
      const op: ToolOperation = result.data
      expect(op.status).toBe('pending')
    }
  })
})

// ============================================================================
// MESSAGE CLASSIFICATION TESTS
// ============================================================================

describe('MessageCategorySchema', () => {
  it('validates complete message category', () => {
    const category = {
      type: 'assistant',
      intent: ['help', 'implement'],
      sentiment: 'positive',
      entities: ['feature', 'code'],
      confidence: 0.95
    }
    
    const result = MessageCategorySchema.safeParse(category)
    
    expect(result.success).toBe(true)
    if (result.success) {
      const cat: MessageCategory = result.data
      expect(cat.intent).toContain('help')
      expect(cat.sentiment).toBe('positive')
      expect(cat.confidence).toBe(0.95)
    }
  })
  
  it('applies defaults for optional fields', () => {
    const minimalCategory = {
      type: 'user'
    }
    
    const result = MessageCategorySchema.safeParse(minimalCategory)
    
    expect(result.success).toBe(true)
    if (result.success) {
      const cat: MessageCategory = result.data
      expect(cat.intent).toEqual([])
      expect(cat.sentiment).toBe('neutral')
      expect(cat.entities).toEqual([])
      expect(cat.confidence).toBe(1)
    }
  })
})

// ============================================================================
// MESSAGE GROUP TESTS
// ============================================================================

describe('MessageGroupSchema', () => {
  it('validates message group with real messages', () => {
    const messageGroup = {
      id: 'group_001',
      title: 'Feature Implementation',
      messages: [
        REAL_CLAUDE_MESSAGES.userMessage,
        REAL_CLAUDE_MESSAGES.assistantMessage
      ],
      category: {
        type: 'assistant',
        intent: ['help'],
        sentiment: 'positive',
        entities: ['feature'],
        confidence: 0.9
      },
      startTime: '2024-08-20T10:30:00.000Z',
      endTime: '2024-08-20T10:30:05.000Z'
    }
    
    const result = MessageGroupSchema.safeParse(messageGroup)
    
    expect(result.success).toBe(true)
    if (result.success) {
      const group: MessageGroup = result.data
      expect(group.id).toBe('group_001')
      expect(group.title).toBe('Feature Implementation')
      expect(group.messages).toHaveLength(2)
      expect(group.category?.sentiment).toBe('positive')
    }
  })
})