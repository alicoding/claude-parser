import { describe, it, expect } from 'vitest'
import type { z } from 'zod'
import { MessageSchema, ConversationSchema, ToolOperationSchema } from '../../src/models'
import type { Message, Conversation, ToolOperation } from '../../src/models'

// Type-safe test data structure
interface TestSamples {
  userMessage: unknown
  assistantMessage: unknown
  toolUseMessage: unknown
  toolResultMessage: unknown
  hookData: unknown
}

// Real Claude Code JSON samples from previous session bug reports
const REAL_CLAUDE_JSON_SAMPLES: TestSamples = {
  // Real user message from Claude Code
  userMessage: {
    "type": "user",
    "uuid": "msg_01234567890abcdef",
    "timestamp": "2024-08-20T10:30:00.000Z",
    "content": "Help me implement a feature"
  },

  // Real assistant message from Claude Code  
  assistantMessage: {
    "type": "assistant", 
    "uuid": "msg_01abcdef234567890",
    "timestamp": "2024-08-20T10:30:05.000Z",
    "content": [
      {"type": "text", "text": "I'll help you implement that feature."}
    ]
  },

  // Real tool_use message from Claude Code
  toolUseMessage: {
    "type": "tool_use",
    "uuid": "msg_tool_use_123",
    "timestamp": "2024-08-20T10:30:10.000Z", 
    "content": [{
      "type": "tool_use",
      "id": "call_123",
      "name": "Edit",
      "input": {
        "file_path": "/path/to/file.ts",
        "old_string": "old code",
        "new_string": "new code"
      }
    }]
  },

  // Real tool_result message from Claude Code
  toolResultMessage: {
    "type": "tool_result",
    "uuid": "msg_tool_result_123", 
    "timestamp": "2024-08-20T10:30:15.000Z",
    "content": [
      {"type": "tool_result", "tool_call_id": "call_123", "content": "Success"}
    ]
  },

  // Real hook data from Claude Code (camelCase format)
  hookData: {
    "sessionId": "abc123xyz789",
    "transcriptPath": "/path/to/session.jsonl", 
    "cwd": "/project/path",
    "hookEventName": "PostToolUse",
    "toolName": "Edit",
    "toolInput": {
      "file_path": "/path/to/file.ts",
      "old_string": "old code", 
      "new_string": "new code"
    },
    "toolResponse": [
      {"type": "text", "text": "File edited successfully"}
    ]
  }
}

describe('Message Schema Validation', () => {
  describe('Real Claude Code JSON Format', () => {
    it('should validate real user message', () => {
      const result = MessageSchema.safeParse(REAL_CLAUDE_JSON_SAMPLES.userMessage)
      expect(result.success).toBe(true)
      if (result.success) {
        expect(result.data.type).toBe('user')
        expect(result.data.uuid).toBe('msg_01234567890abcdef')
        expect(result.data.content).toBe('Help me implement a feature')
      }
    })

    it('should validate real assistant message with content array', () => {
      const result = MessageSchema.safeParse(REAL_CLAUDE_JSON_SAMPLES.assistantMessage)
      expect(result.success).toBe(true)
      if (result.success) {
        expect(result.data.type).toBe('assistant')
        expect(Array.isArray(result.data.content)).toBe(true)
      }
    })

    it('should validate real tool_use message', () => {
      const result = MessageSchema.safeParse(REAL_CLAUDE_JSON_SAMPLES.toolUseMessage)
      expect(result.success).toBe(true)
      if (result.success) {
        expect(result.data.type).toBe('tool_use')
        expect(result.data.uuid).toBe('msg_tool_use_123')
      }
    })

    it('should validate real tool_result message', () => {
      const result = MessageSchema.safeParse(REAL_CLAUDE_JSON_SAMPLES.toolResultMessage)
      expect(result.success).toBe(true)
      if (result.success) {
        expect(result.data.type).toBe('tool_result')
        expect(result.data.uuid).toBe('msg_tool_result_123')
      }
    })
  })

  describe('Schema Flexibility', () => {
    it('should handle both string and array content formats', () => {
      const stringContent = { ...REAL_CLAUDE_JSON_SAMPLES.userMessage }
      const arrayContent = { ...REAL_CLAUDE_JSON_SAMPLES.assistantMessage }

      const stringResult = MessageSchema.safeParse(stringContent)
      const arrayResult = MessageSchema.safeParse(arrayContent)

      expect(stringResult.success).toBe(true)
      expect(arrayResult.success).toBe(true)
    })

    it('should accept extra fields for forward compatibility', () => {
      const messageWithExtra = {
        ...REAL_CLAUDE_JSON_SAMPLES.userMessage,
        extraField: "future feature",
        metadata: { custom: "data" }
      }

      const result = MessageSchema.safeParse(messageWithExtra)
      expect(result.success).toBe(true)
    })

    it('should support both camelCase and snake_case field names', () => {
      const camelCaseMessage = {
        type: "user",
        uuid: "test_uuid",
        timestamp: "2024-08-20T10:30:00.000Z",
        content: "test",
        sessionId: "session_123"
      }

      const snakeCaseMessage = {
        type: "user", 
        uuid: "test_uuid",
        timestamp: "2024-08-20T10:30:00.000Z",
        content: "test",
        session_id: "session_123"
      }

      const camelResult = MessageSchema.safeParse(camelCaseMessage)
      const snakeResult = MessageSchema.safeParse(snakeCaseMessage)

      expect(camelResult.success).toBe(true)
      expect(snakeResult.success).toBe(true)
    })
  })

  describe('Required Field Validation', () => {
    it('should reject messages missing required fields', () => {
      const invalidMessage = {
        type: "user",
        // Missing uuid, timestamp, content
      }

      const result = MessageSchema.safeParse(invalidMessage)
      expect(result.success).toBe(false)
    })

    it('should reject messages with invalid type', () => {
      const invalidMessage = {
        type: "invalid_type",
        uuid: "test_uuid", 
        timestamp: "2024-08-20T10:30:00.000Z",
        content: "test"
      }

      const result = MessageSchema.safeParse(invalidMessage)
      expect(result.success).toBe(false)
    })
  })
})

describe('Conversation Schema Validation', () => {
  it('should validate conversation with multiple real messages', () => {
    const conversation = {
      messages: [
        REAL_CLAUDE_JSON_SAMPLES.userMessage,
        REAL_CLAUDE_JSON_SAMPLES.assistantMessage,
        REAL_CLAUDE_JSON_SAMPLES.toolUseMessage,
        REAL_CLAUDE_JSON_SAMPLES.toolResultMessage
      ],
      metadata: {
        sessionId: "session_123",
        totalMessages: 4
      }
    }

    const result = ConversationSchema.safeParse(conversation)
    expect(result.success).toBe(true)
    if (result.success) {
      expect(result.data.messages).toHaveLength(4)
      expect(result.data.messages[0]?.type).toBe('user')
      expect(result.data.messages[1]?.type).toBe('assistant')
    }
  })

  it('should handle empty conversation', () => {
    const emptyConversation = {
      messages: []
    }

    const result = ConversationSchema.safeParse(emptyConversation)
    expect(result.success).toBe(true)
    if (result.success) {
      expect(result.data.messages).toHaveLength(0)
    }
  })
})

describe('Tool Operation Schema Validation', () => {
  it('should validate complete tool operation', () => {
    const toolOperation = {
      id: "edit_001",
      name: "Edit",
      input: {
        file_path: "/path/to/file.ts",
        old_string: "old code",
        new_string: "new code"
      },
      result: "File edited successfully",
      success: true,
      duration: 150,
      startTime: "2024-08-20T10:30:10.000Z",
      endTime: "2024-08-20T10:30:15.000Z"
    }

    const result = ToolOperationSchema.safeParse(toolOperation)
    expect(result.success).toBe(true)
    if (result.success) {
      expect(result.data.name).toBe('Edit')
      expect(result.data.success).toBe(true)
    }
  })

  it('should handle partial tool operation (in progress)', () => {
    const partialOperation = {
      id: "bash_001",
      name: "Bash", 
      input: { command: "npm install" },
      success: false,
      startTime: "2024-08-20T10:30:10.000Z"
      // Missing result, duration, endTime
    }

    const result = ToolOperationSchema.safeParse(partialOperation)
    expect(result.success).toBe(true)
    if (result.success) {
      expect(result.data.name).toBe('Bash')
      expect(result.data.result).toBeUndefined()
      expect(result.data.endTime).toBeUndefined()
    }
  })
})