"""Memory export implementation.

Provides functionality to export Claude conversations to memory systems.
Designed to work with mem0 and similar vector databases.
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from pathlib import Path
import hashlib

from ..domain.conversation import Conversation
from ..models import Message, AssistantMessage, UserMessage, ToolUse, ToolResult, Summary


@dataclass
class ConversationMemory:
    """A memory extracted from a conversation."""
    
    content: str
    metadata: Dict[str, Any]
    embedding_text: Optional[str] = None
    memory_id: Optional[str] = None
    
    def generate_id(self) -> str:
        """Generate a unique ID for this memory."""
        content_hash = hashlib.sha256(self.content.encode()).hexdigest()[:16]
        self.memory_id = f"mem_{content_hash}"
        return self.memory_id


class MemoryExporter:
    """Export conversations to memory format.
    
    This class provides methods to extract memories from conversations
    and prepare them for storage in vector databases like mem0.
    
    Example:
        exporter = MemoryExporter()
        memories = exporter.export(conversation)
        
        # Memories are ready for mem0 or other systems
        for memory in memories:
            print(f"Memory: {memory.content[:100]}...")
            print(f"Metadata: {memory.metadata}")
    """
    
    def __init__(
        self,
        chunk_size: int = 1000,
        include_metadata: bool = True,
        batch_size: int = 100
    ):
        """Initialize the memory exporter.
        
        Args:
            chunk_size: Maximum characters per memory chunk
            include_metadata: Whether to include message metadata
            batch_size: Number of memories to process at once
        """
        self.chunk_size = chunk_size
        self.include_metadata = include_metadata
        self.batch_size = batch_size
    
    def export(self, conversation: Conversation) -> List[ConversationMemory]:
        """Export a conversation to memory format.
        
        Args:
            conversation: The conversation to export
            
        Returns:
            List of ConversationMemory objects ready for storage
        """
        memories = []
        
        # Extract memories from user-assistant pairs
        user_messages = list(conversation.user_messages)
        assistant_messages = list(conversation.assistant_messages)
        
        for user_msg in user_messages:
            # Find corresponding assistant response
            assistant_response = self._find_response(
                user_msg, 
                assistant_messages
            )
            
            if assistant_response:
                memory = self._create_memory_pair(
                    user_msg,
                    assistant_response
                )
                memories.append(memory)
        
        # Extract memories from tool uses
        tool_memories = self._extract_tool_memories(conversation)
        memories.extend(tool_memories)
        
        # Extract summary if available
        summaries = conversation.summaries
        if summaries:
            for summary in summaries:
                summary_memory = self._create_summary_memory(summary)
                memories.append(summary_memory)
        
        return memories
    
    def export_batch(
        self, 
        conversations: List[Conversation]
    ) -> List[ConversationMemory]:
        """Export multiple conversations in batch.
        
        Args:
            conversations: List of conversations to export
            
        Returns:
            Combined list of memories from all conversations
        """
        all_memories = []
        
        for i in range(0, len(conversations), self.batch_size):
            batch = conversations[i:i + self.batch_size]
            for conv in batch:
                memories = self.export(conv)
                all_memories.extend(memories)
        
        return all_memories
    
    def _find_response(
        self,
        user_msg: UserMessage,
        assistant_messages: List[AssistantMessage]
    ) -> Optional[AssistantMessage]:
        """Find the assistant response to a user message."""
        # Find the next assistant message after this user message
        user_time = user_msg.parsed_timestamp
        if not user_time:
            return None
            
        for assistant_msg in assistant_messages:
            assistant_time = assistant_msg.parsed_timestamp
            if assistant_time and assistant_time > user_time:
                return assistant_msg
        
        return None
    
    def _create_memory_pair(
        self,
        user_msg: UserMessage,
        assistant_msg: AssistantMessage
    ) -> ConversationMemory:
        """Create a memory from a user-assistant message pair."""
        # Combine user question and assistant answer
        content = f"Q: {user_msg.text_content}\nA: {assistant_msg.text_content}"
        
        # Truncate if needed
        if len(content) > self.chunk_size:
            content = content[:self.chunk_size] + "..."
        
        metadata = {
            "type": "conversation_pair",
            "user_uuid": user_msg.uuid,
            "assistant_uuid": assistant_msg.uuid,
            "timestamp": user_msg.timestamp,
        }
        
        if self.include_metadata:
            metadata["user_message_type"] = user_msg.type
            metadata["assistant_message_type"] = assistant_msg.type
        
        memory = ConversationMemory(
            content=content,
            metadata=metadata,
            embedding_text=content  # Use full content for embedding
        )
        memory.generate_id()
        
        return memory
    
    def _extract_tool_memories(
        self,
        conversation: Conversation
    ) -> List[ConversationMemory]:
        """Extract memories from tool uses."""
        memories = []
        
        for msg in conversation.tool_uses:
            if not isinstance(msg, ToolUse):
                continue
                
            tool_use = msg
            content = f"Tool: {tool_use.tool_name}\n"
            
            # Add input summary
            if tool_use.parameters:
                input_str = str(tool_use.parameters)[:200]
                content += f"Input: {input_str}\n"
            
            # Find corresponding tool result
            for other_msg in conversation.tool_uses:
                if isinstance(other_msg, ToolResult) and other_msg.tool_use_id == tool_use.uuid:
                    result_str = str(other_msg.tool_result)[:200] if other_msg.tool_result else "No result"
                    content += f"Result: {result_str}"
                    break
            
            metadata = {
                "type": "tool_use",
                "tool_name": tool_use.tool_name,
                "tool_uuid": tool_use.uuid,
                "timestamp": tool_use.timestamp,
            }
            
            memory = ConversationMemory(
                content=content,
                metadata=metadata,
                embedding_text=content
            )
            memory.generate_id()
            memories.append(memory)
        
        return memories
    
    def _create_summary_memory(
        self,
        summary
    ) -> ConversationMemory:
        """Create a memory from a summary."""
        
        content = f"Conversation Summary:\n{summary.summary_content}"
        
        metadata = {
            "type": "summary",
            "uuid": summary.uuid,
            "timestamp": summary.timestamp,
        }
        
        memory = ConversationMemory(
            content=content,
            metadata=metadata,
            embedding_text=summary.summary_content
        )
        memory.generate_id()
        
        return memory


