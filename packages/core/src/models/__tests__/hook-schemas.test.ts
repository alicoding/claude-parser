/**
 * @fileoverview Hook schema validation tests - CRITICAL BUG FIXES
 * 
 * Testing against real Claude Code hook data including:
 * - String tool_response from LS, Grep, Read, Bash
 * - Context-specific output methods
 * - Type guards for developer experience
 */

import { describe, it, expect } from 'vitest'
import {
  HookDataSchema,
  parseHookData,
  isValidHookData,
  isPreToolUse,
  isPostToolUse,
  isStopHook,
  isUserPromptSubmit
} from '../hook-schemas'
import type { HookData } from '../hook-schemas'

// ============================================================================
// CRITICAL BUG FIX TESTS - tool_response string support
// ============================================================================

describe('HookDataSchema - Critical Bug Fixes', () => {
  describe('Bug #1: tool_response accepts strings (BLOCKING FIX)', () => {
    it('validates PostToolUse with STRING response from LS tool', () => {
      const lsResponse = {
        sessionId: 'abc123',
        transcriptPath: '/path/to/session.jsonl',
        cwd: '/project',
        hookEventName: 'PostToolUse',
        toolName: 'LS',
        toolResponse: '- /Users/ali/.claude/projects/\n  - file.md\n  - subdir/\n'  // STRING!
      }
      
      const result = parseHookData(lsResponse)
      
      expect(result.success).toBe(true)
      if (result.success) {
        const data: HookData = result.data
        expect(data.tool_name).toBe('LS')
        expect(typeof data.tool_response).toBe('string')
        expect(data.tool_response).toContain('file.md')
      }
    })
    
    it('validates PostToolUse with STRING response from Grep tool', () => {
      const grepResponse = {
        sessionId: 'abc123',
        transcriptPath: '/path/to/session.jsonl',
        cwd: '/project',
        hookEventName: 'PostToolUse',
        toolName: 'Grep',
        toolResponse: 'file.ts:10: const result = parseMessage(data)\nfile.ts:20: if (result.success) {'
      }
      
      const result = parseHookData(grepResponse)
      
      expect(result.success).toBe(true)
      if (result.success) {
        const data: HookData = result.data
        expect(data.tool_name).toBe('Grep')
        expect(typeof data.tool_response).toBe('string')
        expect(data.tool_response).toContain('parseMessage')
      }
    })
    
    it('validates PostToolUse with STRING response from Read tool', () => {
      const readResponse = {
        sessionId: 'abc123',
        transcriptPath: '/path/to/session.jsonl',
        cwd: '/project',
        hookEventName: 'PostToolUse',
        toolName: 'Read',
        toolResponse: '# README\n\nThis is the file content...\n\nMultiple lines of text.'
      }
      
      const result = parseHookData(readResponse)
      
      expect(result.success).toBe(true)
      if (result.success) {
        const data: HookData = result.data
        expect(data.tool_name).toBe('Read')
        expect(typeof data.tool_response).toBe('string')
        expect(data.tool_response).toContain('README')
      }
    })
    
    it('validates PostToolUse with STRING response from Bash tool', () => {
      const bashResponse = {
        sessionId: 'abc123',
        transcriptPath: '/path/to/session.jsonl',
        cwd: '/project',
        hookEventName: 'PostToolUse',
        toolName: 'Bash',
        toolResponse: 'npm test\n\n✓ 23 tests passed\n✓ 0 tests failed\n\nTest suite completed.'
      }
      
      const result = parseHookData(bashResponse)
      
      expect(result.success).toBe(true)
      if (result.success) {
        const data: HookData = result.data
        expect(data.tool_name).toBe('Bash')
        expect(typeof data.tool_response).toBe('string')
        expect(data.tool_response).toContain('tests passed')
      }
    })
    
    it('still validates PostToolUse with OBJECT response', () => {
      const objectResponse = {
        sessionId: 'abc123',
        transcriptPath: '/path/to/session.jsonl',
        cwd: '/project',
        hookEventName: 'PostToolUse',
        toolName: 'CustomTool',
        toolResponse: {
          status: 'success',
          data: { result: 42 }
        }
      }
      
      const result = parseHookData(objectResponse)
      
      expect(result.success).toBe(true)
      if (result.success) {
        const data: HookData = result.data
        expect(data.tool_name).toBe('CustomTool')
        expect(typeof data.tool_response).toBe('object')
        expect(data.tool_response).toHaveProperty('status', 'success')
      }
    })
    
    it('still validates PostToolUse with ARRAY response', () => {
      const arrayResponse = {
        sessionId: 'abc123',
        transcriptPath: '/path/to/session.jsonl',
        cwd: '/project',
        hookEventName: 'PostToolUse',
        toolName: 'Edit',
        toolResponse: [
          { type: 'text', text: 'File edited successfully' }
        ]
      }
      
      const result = parseHookData(arrayResponse)
      
      expect(result.success).toBe(true)
      if (result.success) {
        const data: HookData = result.data
        expect(data.tool_name).toBe('Edit')
        expect(Array.isArray(data.tool_response)).toBe(true)
      }
    })
    
    it('validates PostToolUse with NULL response', () => {
      const nullResponse = {
        sessionId: 'abc123',
        transcriptPath: '/path/to/session.jsonl',
        cwd: '/project',
        hookEventName: 'PostToolUse',
        toolName: 'SomeTool',
        toolResponse: null
      }
      
      const result = parseHookData(nullResponse)
      
      expect(result.success).toBe(true)
      if (result.success) {
        const data: HookData = result.data
        expect(data.tool_response).toBe(null)
      }
    })
    
    it('validates PostToolUse with MISSING response', () => {
      const missingResponse = {
        sessionId: 'abc123',
        transcriptPath: '/path/to/session.jsonl',
        cwd: '/project',
        hookEventName: 'PostToolUse',
        toolName: 'SomeTool'
        // No toolResponse field
      }
      
      const result = parseHookData(missingResponse)
      
      expect(result.success).toBe(true)
      if (result.success) {
        const data: HookData = result.data
        expect(data.tool_response).toBeUndefined()
      }
    })
  })
  
  describe('Field Normalization (camelCase → snake_case)', () => {
    it('normalizes all camelCase fields to snake_case', () => {
      const camelCaseData = {
        sessionId: 'abc123',
        transcriptPath: '/path/to/session.jsonl',
        cwd: '/project',
        hookEventName: 'PreToolUse',
        toolName: 'Edit',
        toolInput: { file: 'test.ts' },
        stopHookActive: false,
        customInstructions: 'Be careful'
      }
      
      const result = parseHookData(camelCaseData)
      
      expect(result.success).toBe(true)
      if (result.success) {
        const data: HookData = result.data
        // Should have both formats available
        expect(data.session_id).toBe('abc123')
        expect(data.transcript_path).toBe('/path/to/session.jsonl')
        expect(data.hook_event_name).toBe('PreToolUse')
        expect(data.tool_name).toBe('Edit')
        expect(data.tool_input).toEqual({ file: 'test.ts' })
        expect(data.stop_hook_active).toBe(false)
        expect(data.custom_instructions).toBe('Be careful')
      }
    })
    
    it('preserves snake_case fields when already present', () => {
      const snakeCaseData = {
        session_id: 'xyz789',
        transcript_path: '/other/path.jsonl',
        cwd: '/workspace',
        hook_event_name: 'PostToolUse',
        tool_name: 'Bash',
        tool_response: 'command output'
      }
      
      const result = parseHookData(snakeCaseData)
      
      expect(result.success).toBe(true)
      if (result.success) {
        const data: HookData = result.data
        expect(data.session_id).toBe('xyz789')
        expect(data.transcript_path).toBe('/other/path.jsonl')
        expect(data.hook_event_name).toBe('PostToolUse')
        expect(data.tool_name).toBe('Bash')
        expect(data.tool_response).toBe('command output')
      }
    })
  })
})

// ============================================================================
// TYPE GUARD TESTS - Developer Experience
// ============================================================================

describe('Type Guards for Developer Experience', () => {
  const preToolUseData = {
    sessionId: 'test',
    transcriptPath: '/test.jsonl',
    cwd: '/test',
    hookEventName: 'PreToolUse',
    toolName: 'Edit',
    toolInput: { file: 'test.ts' }
  }
  
  const postToolUseData = {
    sessionId: 'test',
    transcriptPath: '/test.jsonl',
    cwd: '/test',
    hookEventName: 'PostToolUse',
    toolName: 'LS',
    toolResponse: 'file list'
  }
  
  const stopData = {
    sessionId: 'test',
    transcriptPath: '/test.jsonl',
    cwd: '/test',
    hookEventName: 'Stop',
    stopHookActive: false
  }
  
  const userPromptData = {
    sessionId: 'test',
    transcriptPath: '/test.jsonl',
    cwd: '/test',
    hookEventName: 'UserPromptSubmit',
    prompt: 'User input here'
  }
  
  it('correctly identifies PreToolUse hooks', () => {
    const preResult = parseHookData(preToolUseData)
    const postResult = parseHookData(postToolUseData)
    
    if (preResult.success && postResult.success) {
      expect(isPreToolUse(preResult.data)).toBe(true)
      expect(isPreToolUse(postResult.data)).toBe(false)
    }
  })
  
  it('correctly identifies PostToolUse hooks', () => {
    const preResult = parseHookData(preToolUseData)
    const postResult = parseHookData(postToolUseData)
    
    if (preResult.success && postResult.success) {
      expect(isPostToolUse(preResult.data)).toBe(false)
      expect(isPostToolUse(postResult.data)).toBe(true)
    }
  })
  
  it('correctly identifies Stop hooks', () => {
    const stopResult = parseHookData(stopData)
    const otherResult = parseHookData(preToolUseData)
    
    if (stopResult.success && otherResult.success) {
      expect(isStopHook(stopResult.data)).toBe(true)
      expect(isStopHook(otherResult.data)).toBe(false)
    }
  })
  
  it('correctly identifies UserPromptSubmit hooks', () => {
    const promptResult = parseHookData(userPromptData)
    const otherResult = parseHookData(preToolUseData)
    
    if (promptResult.success && otherResult.success) {
      expect(isUserPromptSubmit(promptResult.data)).toBe(true)
      expect(isUserPromptSubmit(otherResult.data)).toBe(false)
    }
  })
})

// ============================================================================
// VALIDATION HELPER TESTS
// ============================================================================

describe('Validation Helpers', () => {
  it('isValidHookData correctly validates data', () => {
    const validData = {
      sessionId: 'test',
      transcriptPath: '/test.jsonl',
      cwd: '/test',
      hookEventName: 'PreToolUse'
    }
    
    const invalidData = {
      // Missing required fields
      hookEventName: 'PreToolUse'
    }
    
    expect(isValidHookData(validData)).toBe(true)
    expect(isValidHookData(invalidData)).toBe(false)
    expect(isValidHookData(null)).toBe(false)
    expect(isValidHookData(undefined)).toBe(false)
    expect(isValidHookData('string')).toBe(false)
  })
  
  it('parseHookData returns detailed errors', () => {
    const invalidData = {
      sessionId: '',  // Empty string fails min(1)
      transcriptPath: '/test.jsonl',
      cwd: '/test',
      hookEventName: 'InvalidType'  // Invalid enum value
    }
    
    const result = parseHookData(invalidData)
    
    expect(result.success).toBe(false)
    if (!result.success) {
      expect(result.error.issues.length).toBeGreaterThan(0)
      // Check for validation errors on invalid fields
      expect(result.error.issues.some(i => 
        i.path.includes('sessionId') || 
        i.path.includes('hookEventName') ||
        i.message.includes('sessionId') ||
        i.message.includes('Invalid')
      )).toBe(true)
    }
  })
})

// ============================================================================
// FORWARD COMPATIBILITY TESTS
// ============================================================================

describe('Forward Compatibility', () => {
  it('preserves unknown fields for future Claude features', () => {
    const futureData = {
      sessionId: 'test',
      transcriptPath: '/test.jsonl',
      cwd: '/test',
      hookEventName: 'PreToolUse',
      // Future fields
      futureField: 'future value',
      metadata: { extra: 'data' },
      tags: ['important', 'security']
    }
    
    const result = parseHookData(futureData)
    
    expect(result.success).toBe(true)
    if (result.success) {
      const data = result.data as HookData & Record<string, unknown>
      expect(data.futureField).toBe('future value')
      expect(data.metadata).toEqual({ extra: 'data' })
      expect(data.tags).toEqual(['important', 'security'])
    }
  })
})