/**
 * @fileoverview Tool operation grouping functionality
 * @module @claude-parser/operations
 * 
 * ENGINEERING PRINCIPLES:
 * - Pure functions for grouping logic
 * - Type-safe operation tracking
 * - 95/5: Simple API, handles complexity internally
 */

import type { StreamMessage } from '../stream/types'

/**
 * Represents a complete tool operation lifecycle
 */
export interface ToolOperation {
  /** Unique operation ID */
  id: string
  
  /** Tool name (Bash, Edit, Write, etc.) */
  tool: string
  
  /** Tool input parameters */
  input: Record<string, unknown>
  
  /** Tool output (string for most tools) */
  output?: string | Record<string, unknown>
  
  /** Operation success status */
  success: boolean
  
  /** Error message if failed */
  error?: string
  
  /** Timing information */
  startTime: string
  endTime?: string
  duration?: number
  
  /** Related messages */
  messages: {
    toolUse?: StreamMessage
    toolResult?: StreamMessage
    preHook?: StreamMessage
    postHook?: StreamMessage
  }
}

/**
 * Groups tool-related messages into operations
 * 
 * @example 95% use case
 * ```typescript
 * const operations = groupToolOperations(messages)
 * // Returns array of complete tool operations
 * ```
 */
export function groupToolOperations(messages: StreamMessage[]): ToolOperation[] {
  const operations: ToolOperation[] = []
  const pendingOperations = new Map<string, Partial<ToolOperation>>()
  
  for (const message of messages) {
    // Handle tool_use messages (start of operation)
    if (message.type === 'assistant' && message.message.content) {
      const content = Array.isArray(message.message.content) 
        ? message.message.content 
        : [{ type: 'text', text: message.message.content }]
      
      for (const block of content) {
        if (block.type === 'tool_use' && block.id && block.name) {
          const operation: Partial<ToolOperation> = {
            id: block.id,
            tool: block.name,
            input: block.input || {},
            startTime: message.timestamp,
            success: false, // Will be updated
            messages: {
              toolUse: message
            }
          }
          pendingOperations.set(block.id, operation)
        }
      }
    }
    
    // Handle tool_result messages (end of operation)
    if (message.type === 'tool_result' && message.message.content) {
      // Find matching tool_use by ID
      const toolId = extractToolId(message)
      
      if (toolId && pendingOperations.has(toolId)) {
        const operation = pendingOperations.get(toolId)!
        
        // Extract output based on content type
        const content = Array.isArray(message.message.content)
          ? message.message.content
          : [{ type: 'text', text: message.message.content }]
        
        operation.output = extractToolOutput(content)
        operation.endTime = message.timestamp
        operation.success = !hasError(content)
        
        if (!operation.success) {
          operation.error = extractErrorMessage(content)
        }
        
        // Calculate duration if we have both timestamps
        if (operation.startTime && operation.endTime) {
          const start = new Date(operation.startTime).getTime()
          const end = new Date(operation.endTime).getTime()
          operation.duration = end - start
        }
        
        if (operation.messages) {
          operation.messages.toolResult = message
        }
        
        // Move to completed operations
        operations.push(operation as ToolOperation)
        pendingOperations.delete(toolId)
      }
    }
  }
  
  // Add any pending operations (incomplete)
  for (const [id, operation] of pendingOperations) {
    operations.push({
      ...operation,
      id,
      tool: operation.tool || 'unknown',
      input: operation.input || {},
      success: false,
      error: 'Operation did not complete'
    } as ToolOperation)
  }
  
  return operations
}

/**
 * Extract tool ID from tool_result message
 */
function extractToolId(message: StreamMessage): string | undefined {
  // Tool results often reference the tool_use ID
  // This needs to match how Claude Code structures these messages
  if (message.parentUuid) {
    return message.parentUuid
  }
  
  // Check content for tool_use_id reference
  const content = Array.isArray(message.message.content)
    ? message.message.content
    : [message.message.content]
  
  for (const block of content) {
    if (typeof block === 'object' && block && 'tool_use_id' in block) {
      return (block as any).tool_use_id
    }
  }
  
  return undefined
}

/**
 * Extract tool output from content blocks
 */
function extractToolOutput(content: any[]): string | Record<string, unknown> {
  // Most tools return text output
  const textBlocks = content.filter(b => 
    typeof b === 'string' || (b && b.type === 'text')
  )
  
  if (textBlocks.length > 0) {
    return textBlocks
      .map(b => typeof b === 'string' ? b : b.text || '')
      .join('\n')
  }
  
  // Some tools might return structured data
  const dataBlock = content.find(b => b && b.type === 'data')
  if (dataBlock) {
    return dataBlock.data || dataBlock
  }
  
  // Fallback to first content block
  return content[0] || ''
}

/**
 * Check if content indicates an error
 */
function hasError(content: any[]): boolean {
  const text = extractToolOutput(content)
  const textStr = typeof text === 'string' ? text : JSON.stringify(text)
  
  return textStr.toLowerCase().includes('error') || 
         textStr.toLowerCase().includes('failed') ||
         textStr.includes('❌')
}

/**
 * Extract error message from content
 */
function extractErrorMessage(content: any[]): string {
  const output = extractToolOutput(content)
  const text = typeof output === 'string' ? output : JSON.stringify(output)
  
  // Try to extract just the error message
  const errorMatch = text.match(/error:?\s*(.+?)(?:\n|$)/i)
  if (errorMatch && errorMatch[1]) {
    return errorMatch[1].trim()
  }
  
  // Return full text if no specific error found
  return text.substring(0, 200) // Limit length
}

/**
 * Filter operations by tool name
 */
export function filterOperationsByTool(
  operations: ToolOperation[],
  tool: string
): ToolOperation[] {
  return operations.filter(op => 
    op.tool.toLowerCase() === tool.toLowerCase()
  )
}

/**
 * Get operation statistics
 */
export interface OperationStats {
  total: number
  successful: number
  failed: number
  byTool: Record<string, number>
  avgDuration: number
  totalDuration: number
}

export function getOperationStats(operations: ToolOperation[]): OperationStats {
  const stats: OperationStats = {
    total: operations.length,
    successful: 0,
    failed: 0,
    byTool: {},
    avgDuration: 0,
    totalDuration: 0
  }
  
  let durationCount = 0
  
  for (const op of operations) {
    // Success/failure counts
    if (op.success) {
      stats.successful++
    } else {
      stats.failed++
    }
    
    // Tool counts
    stats.byTool[op.tool] = (stats.byTool[op.tool] || 0) + 1
    
    // Duration stats
    if (op.duration !== undefined) {
      stats.totalDuration += op.duration
      durationCount++
    }
  }
  
  // Calculate average duration
  if (durationCount > 0) {
    stats.avgDuration = stats.totalDuration / durationCount
  }
  
  return stats
}