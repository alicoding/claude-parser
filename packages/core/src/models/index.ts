/**
 * @fileoverview Models module barrel export
 * @module @claude-parser/core/models
 * 
 * ENGINEERING PATTERN: Centralized exports with clear boundaries
 * - Single source of truth for all model exports
 * - Type-only exports for optimal tree-shaking
 * - Clear separation between runtime and type exports
 */

// ============================================================================
// SCHEMA EXPORTS - Runtime validation schemas
// ============================================================================

export {
  // Schemas (runtime objects)
  MessageSchema,
  ConversationSchema,
  MessageCategorySchema,
  MessageGroupSchema,
  
  // Enums (runtime constants)
  MessageTypeEnum,
  
  // Validation utilities (runtime functions)
  isValidMessage,
  isValidConversation,
  parseMessage,
  parseConversation,
  
  // Re-export zod for convenience
  z
} from './schemas'

// ============================================================================
// TYPE EXPORTS - TypeScript types only (zero runtime cost)
// ============================================================================

export type {
  // Core types
  Message,
  Conversation,
  MessageCategory,
  MessageGroup,
  
  // Enum types
  MessageType,
  
  // Component types
  ContentBlock,
  MessageContent,
  ConversationMetadata
} from './schemas'

// ============================================================================
// HOOK SCHEMAS - Claude Code hook support
// ============================================================================

export {
  // Schemas
  HookDataSchema,
  HookEventTypeEnum,
  
  // Type guards
  isPreToolUse,
  isPostToolUse,
  isStopHook,
  isUserPromptSubmit,
  
  // Validation helpers
  parseHookData,
  isValidHookData,
  
  // Context-specific outputs (Developer Experience)
  PreToolUseOutputs,
  PostToolUseOutputs,
  StopOutputs,
  UserPromptSubmitOutputs
} from './hook-schemas'

export type {
  HookData,
  HookEventType,
  ToolResponse
} from './hook-schemas'

// ============================================================================
// DOMAIN MODELS - Business logic classes (future)
// ============================================================================

// export { ConversationModel } from './conversation'
// export { ToolOperationGrouper } from './tool-operation'
// export { MessageClassifier } from './classifier'