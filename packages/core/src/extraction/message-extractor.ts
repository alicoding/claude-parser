/**
 * @fileoverview Message extraction between conversation points
 * @module @claude-parser/extraction
 * 
 * ENGINEERING PRINCIPLES:
 * - Multiple identification strategies
 * - Flexible range queries
 * - 95/5: Simple API for common cases
 */

import type { StreamMessage } from '../stream/types'

/**
 * Ways to identify a point in conversation
 */
export interface MessagePoint {
  /** Match by exact UUID */
  uuid?: string
  
  /** Match by timestamp (ISO string or Date) */
  timestamp?: string | Date
  
  /** Match by content substring */
  contentIncludes?: string
  
  /** Match by content regex */
  contentMatches?: RegExp
  
  /** Match by message type */
  type?: StreamMessage['type']
  
  /** Match by session ID */
  sessionId?: string
  
  /** Match by tool name (for tool_use messages) */
  toolName?: string
  
  /** Custom predicate function */
  predicate?: (message: StreamMessage) => boolean
  
  /** Match by message index (0-based) */
  index?: number
}

/**
 * Extraction options
 */
export interface ExtractionOptions {
  /** Include the start/end boundary messages (default: true) */
  inclusive?: boolean
  
  /** Filter to only specific message types */
  messageTypes?: StreamMessage['type'][]
  
  /** Maximum messages to extract (safety limit) */
  maxMessages?: number
  
  /** Extract in reverse order */
  reverse?: boolean
}

/**
 * Extraction result
 */
export interface ExtractionResult {
  /** Extracted messages */
  messages: StreamMessage[]
  
  /** Start point that was matched */
  startPoint: StreamMessage | null
  
  /** End point that was matched */
  endPoint: StreamMessage | null
  
  /** Total messages in range before filtering */
  totalInRange: number
  
  /** Extraction metadata */
  metadata: {
    startIndex: number
    endIndex: number
    duration?: number // milliseconds between start and end
    sessionIds: string[]
  }
}

/**
 * Extract messages between two conversation points
 * 
 * @example 95% use case - extract by content
 * ```typescript
 * const result = extractMessagesBetween(messages, 
 *   { contentIncludes: "start analyzing" },
 *   { contentIncludes: "analysis complete" }
 * )
 * const assistantMessages = result.messages.filter(m => m.type === 'assistant')
 * ```
 * 
 * @example Extract by timestamps  
 * ```typescript
 * const result = extractMessagesBetween(messages,
 *   { timestamp: "2024-01-01T10:00:00Z" },
 *   { timestamp: "2024-01-01T11:00:00Z" }
 * )
 * ```
 * 
 * @example Extract by UUIDs
 * ```typescript
 * const result = extractMessagesBetween(messages,
 *   { uuid: "start-message-uuid" },
 *   { uuid: "end-message-uuid" }
 * )
 * ```
 */
export function extractMessagesBetween(
  messages: StreamMessage[],
  startPoint: MessagePoint,
  endPoint: MessagePoint,
  options: ExtractionOptions = {}
): ExtractionResult {
  const {
    inclusive = true,
    messageTypes,
    maxMessages = 10000,
    reverse = false
  } = options
  
  // Find start and end indices
  const startIndex = findMessagePoint(messages, startPoint)
  const endIndex = findMessagePoint(messages, endPoint, startIndex + 1) // Start search after start point
  
  if (startIndex === -1 || endIndex === -1) {
    return {
      messages: [],
      startPoint: startIndex >= 0 ? messages[startIndex] : null,
      endPoint: endIndex >= 0 ? messages[endIndex] : null,
      totalInRange: 0,
      metadata: {
        startIndex,
        endIndex,
        sessionIds: []
      }
    }
  }
  
  // Extract range
  const rangeStart = inclusive ? startIndex : startIndex + 1
  const rangeEnd = inclusive ? endIndex + 1 : endIndex
  
  let extractedMessages = messages.slice(rangeStart, rangeEnd)
  
  // Apply reverse if requested
  if (reverse) {
    extractedMessages = extractedMessages.reverse()
  }
  
  const totalInRange = extractedMessages.length
  
  // Filter by message types
  if (messageTypes) {
    extractedMessages = extractedMessages.filter(msg => 
      messageTypes.includes(msg.type)
    )
  }
  
  // Apply max limit
  if (extractedMessages.length > maxMessages) {
    extractedMessages = extractedMessages.slice(0, maxMessages)
  }
  
  // Calculate duration
  const startMsg = messages[startIndex]
  const endMsg = messages[endIndex]
  let duration: number | undefined
  
  if (startMsg.timestamp && endMsg.timestamp) {
    const startTime = new Date(startMsg.timestamp).getTime()
    const endTime = new Date(endMsg.timestamp).getTime()
    duration = endTime - startTime
  }
  
  // Get unique session IDs
  const sessionIds = [...new Set(extractedMessages.map(m => m.sessionId))]
  
  return {
    messages: extractedMessages,
    startPoint: messages[startIndex],
    endPoint: messages[endIndex],
    totalInRange,
    metadata: {
      startIndex,
      endIndex,
      duration,
      sessionIds
    }
  }
}

/**
 * Extract all assistant messages between two points
 * Convenience function for the most common use case
 */
export function extractAssistantMessagesBetween(
  messages: StreamMessage[],
  startPoint: MessagePoint,
  endPoint: MessagePoint,
  options?: Omit<ExtractionOptions, 'messageTypes'>
): ExtractionResult {
  return extractMessagesBetween(messages, startPoint, endPoint, {
    ...options,
    messageTypes: ['assistant']
  })
}

/**
 * Extract messages from a point to the end
 */
export function extractMessagesFrom(
  messages: StreamMessage[],
  startPoint: MessagePoint,
  options?: ExtractionOptions
): ExtractionResult {
  // Use last message as end point
  const lastIndex = messages.length - 1
  if (lastIndex < 0) {
    return {
      messages: [],
      startPoint: null,
      endPoint: null,
      totalInRange: 0,
      metadata: { startIndex: -1, endIndex: -1, sessionIds: [] }
    }
  }
  
  return extractMessagesBetween(
    messages,
    startPoint,
    { index: lastIndex },
    options
  )
}

/**
 * Extract messages from the beginning to a point
 */
export function extractMessagesUntil(
  messages: StreamMessage[],
  endPoint: MessagePoint,
  options?: ExtractionOptions
): ExtractionResult {
  return extractMessagesBetween(
    messages,
    { index: 0 },
    endPoint,
    options
  )
}

/**
 * Find the index of a message matching the point criteria
 */
function findMessagePoint(
  messages: StreamMessage[],
  point: MessagePoint,
  startFrom = 0
): number {
  for (let i = startFrom; i < messages.length; i++) {
    const message = messages[i]
    
    // Check index match first (most specific)
    if (point.index !== undefined && i === point.index) {
      return i
    }
    
    // Check UUID match
    if (point.uuid && message.uuid === point.uuid) {
      return i
    }
    
    // Check timestamp match
    if (point.timestamp) {
      const targetTime = typeof point.timestamp === 'string' 
        ? point.timestamp 
        : point.timestamp.toISOString()
      if (message.timestamp === targetTime) {
        return i
      }
    }
    
    // Check session ID
    if (point.sessionId && message.sessionId === point.sessionId) {
      return i
    }
    
    // Check message type
    if (point.type && message.type === point.type) {
      return i
    }
    
    // Check content substring
    if (point.contentIncludes) {
      const content = getMessageTextContent(message)
      if (content.toLowerCase().includes(point.contentIncludes.toLowerCase())) {
        return i
      }
    }
    
    // Check content regex
    if (point.contentMatches) {
      const content = getMessageTextContent(message)
      if (point.contentMatches.test(content)) {
        return i
      }
    }
    
    // Check tool name
    if (point.toolName && message.type === 'assistant') {
      const content = Array.isArray(message.message.content) 
        ? message.message.content 
        : []
      
      for (const block of content) {
        if (typeof block === 'object' && block.type === 'tool_use' && block.name === point.toolName) {
          return i
        }
      }
    }
    
    // Check custom predicate (most flexible)
    if (point.predicate && point.predicate(message)) {
      return i
    }
  }
  
  return -1
}

/**
 * Extract text content from a message for searching
 */
function getMessageTextContent(message: StreamMessage): string {
  const content = message.message.content
  
  if (typeof content === 'string') {
    return content
  }
  
  if (Array.isArray(content)) {
    return content
      .map(block => {
        if (typeof block === 'string') return block
        if (typeof block === 'object' && block.text) return block.text
        return ''
      })
      .join(' ')
  }
  
  return ''
}

/**
 * Extract messages around a specific point (before and after)
 */
export function extractMessagesAround(
  messages: StreamMessage[],
  centerPoint: MessagePoint,
  options: ExtractionOptions & { 
    beforeCount?: number, 
    afterCount?: number 
  } = {}
): ExtractionResult {
  const { beforeCount = 5, afterCount = 5, ...extractOptions } = options
  
  const centerIndex = findMessagePoint(messages, centerPoint)
  if (centerIndex === -1) {
    return {
      messages: [],
      startPoint: null,
      endPoint: null,
      totalInRange: 0,
      metadata: { startIndex: -1, endIndex: -1, sessionIds: [] }
    }
  }
  
  const startIndex = Math.max(0, centerIndex - beforeCount)
  const endIndex = Math.min(messages.length - 1, centerIndex + afterCount)
  
  return extractMessagesBetween(
    messages,
    { index: startIndex },
    { index: endIndex },
    extractOptions
  )
}

/**
 * Extract messages by session boundaries
 */
export function extractMessagesBySession(
  messages: StreamMessage[],
  sessionId: string,
  options?: ExtractionOptions
): ExtractionResult {
  const sessionMessages = messages.filter(m => m.sessionId === sessionId)
  
  if (sessionMessages.length === 0) {
    return {
      messages: [],
      startPoint: null,
      endPoint: null,
      totalInRange: 0,
      metadata: { startIndex: -1, endIndex: -1, sessionIds: [] }
    }
  }
  
  // Find indices in original array
  const firstSessionMsg = sessionMessages[0]
  const lastSessionMsg = sessionMessages[sessionMessages.length - 1]
  
  const startIndex = messages.findIndex(m => m.uuid === firstSessionMsg.uuid)
  const endIndex = messages.findIndex(m => m.uuid === lastSessionMsg.uuid)
  
  return {
    messages: sessionMessages,
    startPoint: firstSessionMsg,
    endPoint: lastSessionMsg,
    totalInRange: sessionMessages.length,
    metadata: {
      startIndex,
      endIndex,
      sessionIds: [sessionId]
    }
  }
}