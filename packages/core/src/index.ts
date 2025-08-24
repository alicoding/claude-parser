/**
 * @fileoverview Main entry point for @claude-parser/core
 * @module @claude-parser/core
 * 
 * ENGINEERING PRINCIPLES:
 * - Clean public API surface
 * - Type-first exports
 * - Tree-shakeable modules
 * - Zero runtime cost for type exports
 * 
 * PATTERN: Facade pattern - Single entry point for all functionality
 */

// ============================================================================
// MODEL EXPORTS - Schemas and types
// ============================================================================

export {
  // Schemas (runtime validation)
  MessageSchema,
  ConversationSchema,
  MessageCategorySchema,
  MessageGroupSchema,
  
  // Enums (runtime constants)
  MessageTypeEnum,
  
  // Validation utilities
  isValidMessage,
  isValidConversation,
  parseMessage,
  parseConversation
} from './models'

// Type-only exports (zero runtime cost)
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
} from './models'

// ============================================================================
// HOOK EXPORTS - Claude Code hook support
// ============================================================================

export {
  // Hook schemas and validation
  HookDataSchema,
  HookEventTypeEnum,
  parseHookData,
  isValidHookData,
  
  // Type guards
  isPreToolUse,
  isPostToolUse,
  isStopHook,
  isUserPromptSubmit,
  
  // Context-specific outputs (Developer Experience)
  PreToolUseOutputs,
  PostToolUseOutputs,
  StopOutputs,
  UserPromptSubmitOutputs
} from './models'

export type {
  HookData,
  HookEventType,
  ToolResponse
} from './models'

// ============================================================================
// PARSER EXPORTS - Coming next
// ============================================================================

// export {
//   parseConversation,
//   parseStreamingMessage
// } from './parser'

// ============================================================================
// STREAMING EXPORTS - Real-time message streaming
// ============================================================================

export {
  // Main factory (95% use case)
  createTransport,
  
  // Transport implementations (5% use case)
  SSETransport
} from './stream'

export type {
  // Core interfaces
  MessageStreamTransport,
  TransportConfig,
  StreamMessage,
  
  // Configuration
  TransportType,
  ConnectionState,
  
  // Event handlers
  TransportEvents,
  MessageHandler,
  ErrorHandler,
  StateChangeHandler,
  ReconnectHandler,
  
  // Factory type
  TransportFactory
} from './stream'

// ============================================================================
// OPERATIONS EXPORTS - Tool operation grouping
// ============================================================================

export {
  groupToolOperations,
  filterOperationsByTool,
  getOperationStats,
  type ToolOperation,
  type OperationStats
} from './operations'

// ============================================================================
// VERSION EXPORT
// ============================================================================

export const VERSION = '2.0.0' as const

// ============================================================================
// SDK METADATA
// ============================================================================

export const SDK_METADATA = {
  name: '@claude-parser/core',
  version: VERSION,
  author: 'Claude Parser Team',
  license: 'MIT',
  repository: 'https://github.com/anthropics/claude-parser'
} as const