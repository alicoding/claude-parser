/**
 * @fileoverview Zod schemas for Claude Code message validation
 * @module @claude-parser/core/models
 * 
 * ENGINEERING PRINCIPLES:
 * - Type-first: Every schema generates TypeScript types
 * - Runtime validation: Zod ensures data integrity
 * - Forward compatible: Unknown fields preserved
 * - Dual format support: camelCase (Claude) + snake_case (Python)
 * - Zero any types: Full type safety throughout
 * 
 * PATTERN: Schema → Type → Validator → Transformer
 */

import { z } from 'zod'

// ============================================================================
// BASE SCHEMAS - Building blocks for composition
// ============================================================================

/**
 * Message type enumeration - Single source of truth
 * @const
 */
export const MessageTypeEnum = z.enum([
  'user',
  'assistant', 
  'tool_use',
  'tool_result',
  'system',
  'summary'
] as const)

export type MessageType = z.infer<typeof MessageTypeEnum>

/**
 * Content block schema - Handles Claude's complex content format
 * PATTERN: Union types for flexibility with type narrowing
 */
const ContentBlockSchema = z.object({
  type: z.string(),
  text: z.string().optional(),
  // Additional fields preserved for forward compatibility
}).passthrough()

export type ContentBlock = z.infer<typeof ContentBlockSchema>

/**
 * Message content - Can be string or array of content blocks
 * PATTERN: Progressive enhancement - simple strings or rich content
 */
const MessageContentSchema = z.union([
  z.string(),
  z.array(ContentBlockSchema)
])

export type MessageContent = z.infer<typeof MessageContentSchema>

// ============================================================================
// MESSAGE SCHEMA - Core message validation
// ============================================================================

/**
 * Base message schema without transformations
 * PATTERN: Separation of validation from transformation
 */
const BaseMessageSchema = z.object({
  // Required fields
  type: MessageTypeEnum,
  uuid: z.string().min(1),
  timestamp: z.string().datetime(),
  content: MessageContentSchema,
  
  // Optional fields with dual format support
  sessionId: z.string().optional(),
  session_id: z.string().optional(),
  
  // Tool-specific fields
  tool_call_id: z.string().optional(),
  tool_name: z.string().optional(),
  tool_input: z.record(z.unknown()).optional(),
  
  // Metadata
  error: z.string().optional(),
  status: z.string().optional()
}).passthrough() // Preserve unknown fields for forward compatibility

/**
 * Message schema with field normalization
 * PATTERN: Transform at parse time for consistent internal representation
 */
export const MessageSchema = BaseMessageSchema.transform((data) => {
  // Normalize session ID field (camelCase → snake_case)
  if ('sessionId' in data && !('session_id' in data)) {
    return { ...data, session_id: data.sessionId }
  }
  return data
})

export type Message = z.infer<typeof MessageSchema>

// ============================================================================
// CONVERSATION SCHEMA - Message collection with metadata
// ============================================================================

/**
 * Conversation metadata schema
 * PATTERN: Extensible metadata object for analytics
 */
const ConversationMetadataSchema = z.object({
  sessionId: z.string().optional(),
  session_id: z.string().optional(),
  totalMessages: z.number().int().nonnegative().optional(),
  startTime: z.string().datetime().optional(),
  endTime: z.string().datetime().optional(),
  version: z.string().optional()
}).passthrough()

export type ConversationMetadata = z.infer<typeof ConversationMetadataSchema>

/**
 * Conversation schema - Collection of messages with metadata
 * PATTERN: Aggregate root containing entities
 */
export const ConversationSchema = z.object({
  messages: z.array(MessageSchema),
  metadata: ConversationMetadataSchema.optional()
})

export type Conversation = z.infer<typeof ConversationSchema>

// ============================================================================
// TOOL OPERATION SCHEMA - Grouped tool interactions
// ============================================================================

/**
 * Tool operation status enum
 * @const
 */
export const ToolOperationStatusEnum = z.enum([
  'pending',
  'in_progress',
  'success',
  'failed',
  'cancelled'
] as const)

export type ToolOperationStatus = z.infer<typeof ToolOperationStatusEnum>

/**
 * Tool operation schema - Represents a complete tool interaction
 * PATTERN: Domain model aggregating related messages
 */
export const ToolOperationSchema = z.object({
  // Identity
  id: z.string().min(1),
  name: z.string().min(1),
  
  // Input/Output
  input: z.record(z.unknown()),
  result: z.string().optional(),
  
  // Related messages (optional for flexibility)
  preHook: MessageSchema.optional(),
  toolUse: MessageSchema.optional(),
  toolResult: MessageSchema.optional(),
  postHook: MessageSchema.optional(),
  
  // Status tracking
  status: ToolOperationStatusEnum.default('pending'),
  success: z.boolean(),
  
  // Timing
  startTime: z.string().datetime(),
  endTime: z.string().datetime().optional(),
  duration: z.number().nonnegative().optional()
})

export type ToolOperation = z.infer<typeof ToolOperationSchema>

// ============================================================================
// MESSAGE CLASSIFICATION SCHEMA - For UI categorization
// ============================================================================

/**
 * Message category schema
 * PATTERN: Rich classification for UI filtering/display
 */
export const MessageCategorySchema = z.object({
  type: MessageTypeEnum,
  intent: z.array(z.string()).default([]),
  sentiment: z.enum(['positive', 'negative', 'neutral']).default('neutral'),
  entities: z.array(z.string()).default([]),
  confidence: z.number().min(0).max(1).default(1)
})

export type MessageCategory = z.infer<typeof MessageCategorySchema>

/**
 * Message group schema - Related messages grouped together
 * PATTERN: UI-focused grouping for conversation threads
 */
export const MessageGroupSchema = z.object({
  id: z.string().min(1),
  title: z.string().optional(),
  messages: z.array(MessageSchema),
  category: MessageCategorySchema.optional(),
  startTime: z.string().datetime(),
  endTime: z.string().datetime().optional()
})

export type MessageGroup = z.infer<typeof MessageGroupSchema>

// ============================================================================
// VALIDATION HELPERS - Type-safe validation utilities
// ============================================================================

/**
 * Type guard for message validation
 * PATTERN: Runtime type narrowing for conditional logic
 */
export function isValidMessage(data: unknown): data is Message {
  return MessageSchema.safeParse(data).success
}

/**
 * Type guard for conversation validation
 */
export function isValidConversation(data: unknown): data is Conversation {
  return ConversationSchema.safeParse(data).success
}

/**
 * Safe parse with detailed error reporting
 * PATTERN: Never throw, always return Result type
 */
export function parseMessage(data: unknown): 
  | { success: true; data: Message }
  | { success: false; error: z.ZodError } {
  return MessageSchema.safeParse(data)
}

/**
 * Safe parse for conversation
 */
export function parseConversation(data: unknown):
  | { success: true; data: Conversation }
  | { success: false; error: z.ZodError } {
  return ConversationSchema.safeParse(data)
}

// ============================================================================
// EXPORTS - Clean public API
// ============================================================================

export {
  // Re-export z for consumer convenience (they don't need to install zod)
  z
}