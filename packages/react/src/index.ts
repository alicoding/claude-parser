/**
 * @fileoverview React hooks for Claude Parser
 * @module @claude-parser/react
 * 
 * Dead simple React integration for Claude Code streaming
 */

export {
  useClaudeStream,
  useFilteredMessages,
  useLatestMessages,
  useSessionMessages,
  type UseClaudeStreamState,
  type UseClaudeStreamOptions
} from './useClaudeStream'

// Re-export core types for convenience
export type {
  StreamMessage,
  ToolOperation,
  OperationStats,
  ConnectionState,
  TransportConfig
} from '@claude-parser/core'