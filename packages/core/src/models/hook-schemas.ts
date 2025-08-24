/**
 * @fileoverview Hook data schemas for Claude Code hooks
 * @module @claude-parser/core/models/hooks
 * 
 * ENGINEERING PRINCIPLES:
 * - Handle all real-world Claude formats
 * - Type-safe hook-specific contexts
 * - Developer-friendly API
 * 
 * BUG FIX: tool_response accepts strings (LS, Grep, Read, Bash output)
 */

import { z } from 'zod'

// ============================================================================
// HOOK EVENT TYPES
// ============================================================================

/**
 * All 8 Claude Code hook event types
 * @const
 */
export const HookEventTypeEnum = z.enum([
  'PreToolUse',
  'PostToolUse',
  'Notification',
  'UserPromptSubmit',
  'Stop',
  'SubagentStop',
  'PreCompact',
  'SessionStart'
] as const)

export type HookEventType = z.infer<typeof HookEventTypeEnum>

// ============================================================================
// TOOL RESPONSE SCHEMA - Fixed to handle all formats
// ============================================================================

/**
 * Tool response can be:
 * - String (LS, Grep, Read, Bash output)
 * - Object (structured responses)
 * - Array of objects (multiple responses)
 * - null/undefined (no response)
 * 
 * BUG FIX: Previously only accepted Dict/List[Dict], breaking string responses
 */
const ToolResponseSchema = z.union([
  z.string(),                              // LS, Grep, Read, Bash output
  z.record(z.unknown()),                   // Structured response
  z.array(z.record(z.unknown())),         // Multiple responses
  z.null(),                                // No response
  z.undefined()                            // Optional field
])

export type ToolResponse = z.infer<typeof ToolResponseSchema>

// ============================================================================
// BASE HOOK DATA SCHEMA
// ============================================================================

/**
 * Universal hook data schema - handles all 8 hook types
 * Follows DRY principle: single model for all hooks
 * 
 * PATTERN: Progressive enhancement - base fields + hook-specific fields
 */
export const HookDataSchema = z.object({
  // ===== Required fields (ALL hooks have these) =====
  // Support both camelCase and snake_case for all fields
  sessionId: z.string().min(1).optional(),
  session_id: z.string().min(1).optional(),
  transcriptPath: z.string().min(1).optional(),
  transcript_path: z.string().min(1).optional(),
  cwd: z.string().min(1),
  hookEventName: HookEventTypeEnum.optional(),
  hook_event_name: HookEventTypeEnum.optional(),
  
  // ===== Tool-specific fields (PreToolUse, PostToolUse) =====
  toolName: z.string().optional(),
  tool_name: z.string().optional(),
  toolInput: z.record(z.unknown()).optional(),
  tool_input: z.record(z.unknown()).optional(),
  toolResponse: ToolResponseSchema.optional(),  // FIXED: Now accepts strings
  tool_response: ToolResponseSchema.optional(),
  
  // ===== Other hook-specific fields =====
  prompt: z.string().optional(),                    // UserPromptSubmit
  message: z.string().optional(),                   // Notification
  stopHookActive: z.boolean().optional(),          // Stop, SubagentStop
  stop_hook_active: z.boolean().optional(),
  trigger: z.string().optional(),                   // PreCompact
  customInstructions: z.string().optional(),       // PreCompact
  custom_instructions: z.string().optional(),
  source: z.string().optional()                     // SessionStart
}).passthrough()  // Preserve unknown fields for forward compatibility
  .refine((data) => {
    // Ensure at least one version of required fields exists
    const hasSessionId = Boolean(data.sessionId || data.session_id)
    const hasTranscriptPath = Boolean(data.transcriptPath || data.transcript_path)
    const hasHookEventName = Boolean(data.hookEventName || data.hook_event_name)
    
    return hasSessionId && hasTranscriptPath && hasHookEventName
  }, {
    message: 'Missing required fields: sessionId/session_id, transcriptPath/transcript_path, and hookEventName/hook_event_name are required'
  })
  .transform((data) => {
  // Normalize field names (camelCase → snake_case for consistency)
  const normalized: Record<string, unknown> = { ...data }
  
  if ('sessionId' in data && !('session_id' in data)) {
    normalized.session_id = data.sessionId
  }
  if ('transcriptPath' in data && !('transcript_path' in data)) {
    normalized.transcript_path = data.transcriptPath
  }
  if ('hookEventName' in data && !('hook_event_name' in data)) {
    normalized.hook_event_name = data.hookEventName
  }
  if ('toolName' in data && !('tool_name' in data)) {
    normalized.tool_name = data.toolName
  }
  if ('toolInput' in data && !('tool_input' in data)) {
    normalized.tool_input = data.toolInput
  }
  if ('toolResponse' in data && !('tool_response' in data)) {
    normalized.tool_response = data.toolResponse
  }
  if ('stopHookActive' in data && !('stop_hook_active' in data)) {
    normalized.stop_hook_active = data.stopHookActive
  }
  if ('customInstructions' in data && !('custom_instructions' in data)) {
    normalized.custom_instructions = data.customInstructions
  }
  
  return normalized
})

export type HookData = z.infer<typeof HookDataSchema>

// ============================================================================
// TYPE GUARDS - Developer-friendly type narrowing
// ============================================================================

/**
 * Type guard for PreToolUse hooks
 * PATTERN: Runtime type narrowing for better DX
 */
export function isPreToolUse(data: HookData): boolean {
  return data.hook_event_name === 'PreToolUse' || data.hookEventName === 'PreToolUse'
}

/**
 * Type guard for PostToolUse hooks
 */
export function isPostToolUse(data: HookData): boolean {
  return data.hook_event_name === 'PostToolUse' || data.hookEventName === 'PostToolUse'
}

/**
 * Type guard for Stop hooks
 */
export function isStopHook(data: HookData): boolean {
  return data.hook_event_name === 'Stop' || data.hookEventName === 'Stop'
}

/**
 * Type guard for UserPromptSubmit hooks
 */
export function isUserPromptSubmit(data: HookData): boolean {
  return data.hook_event_name === 'UserPromptSubmit' || data.hookEventName === 'UserPromptSubmit'
}

// ============================================================================
// CONTEXT-SPECIFIC OUTPUT HELPERS (Developer Experience)
// ============================================================================

/**
 * PreToolUse context-specific outputs
 * PATTERN: Semantic clarity over generic functions
 */
export const PreToolUseOutputs = {
  /**
   * Deny tool execution with reason
   * Exit code 2 blocks the tool
   */
  deny(reason: string): never {
    console.error(reason)
    process.exit(2)
  },
  
  /**
   * Allow tool execution
   * Exit code 0 allows the tool
   */
  allow(): never {
    process.exit(0)
  },
  
  /**
   * Ask user for permission (stdout goes to Claude)
   * Exit code 0 with output prompts user
   */
  ask(message: string = 'Allow this tool?'): never {
    console.log(message)
    process.exit(0)
  }
} as const

/**
 * PostToolUse context-specific outputs
 */
export const PostToolUseOutputs = {
  /**
   * Accept tool results
   */
  accept(): never {
    process.exit(0)
  },
  
  /**
   * Challenge tool results with reason
   */
  challenge(reason: string): never {
    console.error(reason)
    process.exit(2)
  }
} as const

/**
 * Stop hook context-specific outputs
 */
export const StopOutputs = {
  /**
   * Prevent Claude from stopping
   */
  prevent(reason: string): never {
    console.error(reason)
    process.exit(2)
  },
  
  /**
   * Allow Claude to stop
   */
  allow(): never {
    process.exit(0)
  }
} as const

/**
 * UserPromptSubmit context-specific outputs
 */
export const UserPromptSubmitOutputs = {
  /**
   * Block user prompt with reason
   */
  block(reason: string): never {
    console.error(reason)
    process.exit(2)
  },
  
  /**
   * Add context to prompt (stdout goes to Claude)
   */
  addContext(context: string): never {
    console.log(context)
    process.exit(0)
  },
  
  /**
   * Allow prompt as-is
   */
  allow(): never {
    process.exit(0)
  }
} as const

// ============================================================================
// VALIDATION HELPERS
// ============================================================================

/**
 * Safe parse hook data with detailed errors
 */
export function parseHookData(data: unknown):
  | { success: true; data: HookData }
  | { success: false; error: z.ZodError } {
  return HookDataSchema.safeParse(data)
}

/**
 * Type guard for valid hook data
 */
export function isValidHookData(data: unknown): data is HookData {
  return HookDataSchema.safeParse(data).success
}