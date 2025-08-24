/**
 * @fileoverview Tests for tool operation grouping
 */

import { describe, it, expect } from 'vitest'
import { 
  groupToolOperations, 
  filterOperationsByTool,
  getOperationStats,
  type ToolOperation 
} from '../tool-grouper'
import type { StreamMessage } from '../../stream/types'

// Test data based on real Claude messages
const createToolUseMessage = (
  id: string,
  tool: string,
  input: any
): StreamMessage => ({
  uuid: `msg-${id}`,
  parentUuid: null,
  sessionId: 'test-session',
  type: 'assistant',
  timestamp: '2024-01-01T00:00:00Z',
  cwd: '/test',
  gitBranch: 'main',
  version: '1.0.0',
  isSidechain: false,
  userType: 'external',
  message: {
    id: `msg-${id}`,
    type: 'message',
    role: 'assistant',
    content: [{
      type: 'tool_use',
      id: `tool-${id}`,
      name: tool,
      input
    }],
    stop_reason: null,
    stop_sequence: null
  },
  requestId: `req-${id}`
})

const createToolResultMessage = (
  id: string,
  output: string,
  parentId: string
): StreamMessage => ({
  uuid: `result-${id}`,
  parentUuid: `tool-${parentId}`,
  sessionId: 'test-session',
  type: 'tool_result',
  timestamp: '2024-01-01T00:00:05Z',
  cwd: '/test',
  gitBranch: 'main',
  version: '1.0.0',
  isSidechain: false,
  userType: 'external',
  message: {
    id: `result-${id}`,
    type: 'message',
    role: 'tool',
    content: output,
    stop_reason: null,
    stop_sequence: null
  },
  requestId: `req-${id}`
})

describe('Tool Operation Grouping', () => {
  describe('groupToolOperations', () => {
    it('groups simple tool use and result', () => {
      const messages: StreamMessage[] = [
        createToolUseMessage('1', 'Bash', { command: 'ls' }),
        createToolResultMessage('1', 'file1.txt\nfile2.txt', '1')
      ]
      
      const operations = groupToolOperations(messages)
      
      expect(operations).toHaveLength(1)
      expect(operations[0]).toMatchObject({
        id: 'tool-1',
        tool: 'Bash',
        input: { command: 'ls' },
        output: 'file1.txt\nfile2.txt',
        success: true,
        duration: 5000 // 5 seconds between timestamps
      })
    })
    
    it('handles multiple tool operations', () => {
      const messages: StreamMessage[] = [
        createToolUseMessage('1', 'Bash', { command: 'ls' }),
        createToolResultMessage('1', 'output1', '1'),
        createToolUseMessage('2', 'Edit', { file: 'test.js', old: 'a', new: 'b' }),
        createToolResultMessage('2', 'File edited successfully', '2')
      ]
      
      const operations = groupToolOperations(messages)
      
      expect(operations).toHaveLength(2)
      expect(operations[0].tool).toBe('Bash')
      expect(operations[1].tool).toBe('Edit')
    })
    
    it('handles incomplete operations', () => {
      const messages: StreamMessage[] = [
        createToolUseMessage('1', 'Bash', { command: 'sleep 100' })
        // No result message
      ]
      
      const operations = groupToolOperations(messages)
      
      expect(operations).toHaveLength(1)
      expect(operations[0]).toMatchObject({
        id: 'tool-1',
        tool: 'Bash',
        success: false,
        error: 'Operation did not complete'
      })
    })
    
    it('detects failed operations', () => {
      const messages: StreamMessage[] = [
        createToolUseMessage('1', 'Bash', { command: 'invalid' }),
        createToolResultMessage('1', 'Error: command not found', '1')
      ]
      
      const operations = groupToolOperations(messages)
      
      expect(operations[0]).toMatchObject({
        success: false,
        error: 'command not found'
      })
    })
    
    it('handles text content in assistant messages', () => {
      const message: StreamMessage = {
        ...createToolUseMessage('1', 'Bash', { command: 'ls' }),
        message: {
          ...createToolUseMessage('1', 'Bash', { command: 'ls' }).message,
          content: [
            { type: 'text', text: 'Running command...' },
            { type: 'tool_use', id: 'tool-1', name: 'Bash', input: { command: 'ls' } }
          ]
        }
      }
      
      const operations = groupToolOperations([
        message,
        createToolResultMessage('1', 'output', '1')
      ])
      
      expect(operations).toHaveLength(1)
      expect(operations[0].tool).toBe('Bash')
    })
  })
  
  describe('filterOperationsByTool', () => {
    it('filters operations by tool name', () => {
      const operations: ToolOperation[] = [
        { id: '1', tool: 'Bash', input: {}, success: true, startTime: '' },
        { id: '2', tool: 'Edit', input: {}, success: true, startTime: '' },
        { id: '3', tool: 'Bash', input: {}, success: true, startTime: '' }
      ] as ToolOperation[]
      
      const bashOps = filterOperationsByTool(operations, 'Bash')
      
      expect(bashOps).toHaveLength(2)
      expect(bashOps.every(op => op.tool === 'Bash')).toBe(true)
    })
    
    it('handles case-insensitive filtering', () => {
      const operations: ToolOperation[] = [
        { id: '1', tool: 'Bash', input: {}, success: true, startTime: '' }
      ] as ToolOperation[]
      
      const bashOps = filterOperationsByTool(operations, 'bash')
      
      expect(bashOps).toHaveLength(1)
    })
  })
  
  describe('getOperationStats', () => {
    it('calculates operation statistics', () => {
      const operations: ToolOperation[] = [
        { 
          id: '1', 
          tool: 'Bash', 
          input: {}, 
          success: true, 
          startTime: '', 
          duration: 100,
          messages: {}
        },
        { 
          id: '2', 
          tool: 'Edit', 
          input: {}, 
          success: false, 
          startTime: '', 
          duration: 200,
          messages: {}
        },
        { 
          id: '3', 
          tool: 'Bash', 
          input: {}, 
          success: true, 
          startTime: '', 
          duration: 150,
          messages: {}
        }
      ]
      
      const stats = getOperationStats(operations)
      
      expect(stats).toEqual({
        total: 3,
        successful: 2,
        failed: 1,
        byTool: {
          Bash: 2,
          Edit: 1
        },
        avgDuration: 150,
        totalDuration: 450
      })
    })
    
    it('handles operations without duration', () => {
      const operations: ToolOperation[] = [
        { id: '1', tool: 'Bash', input: {}, success: true, startTime: '', messages: {} }
      ]
      
      const stats = getOperationStats(operations)
      
      expect(stats.avgDuration).toBe(0)
      expect(stats.totalDuration).toBe(0)
    })
  })
})