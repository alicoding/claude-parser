"""
LlamaIndex export format - 100% framework delegation
@ZERO_CUSTOM_CODE: No loops, only map/filter
@FRAMEWORK_FIRST: Reuse existing functions
@DRY_FIRST: Don't duplicate text extraction logic
@LOC_ENFORCEMENT: <80 lines
"""

from typing import List, Dict, Any, Union, Iterator
from operator import methodcaller
from functools import partial
from more_itertools import chunked

from ..main import load_session
from ..filtering import filter_pure_conversation
from ..messages.utils import get_text


def _extract_document(msg: Dict[str, Any]) -> Dict[str, Any]:
    """Transform message to LlamaIndex document format

    @SEMANTIC_INTERFACE: Returns simple text + metadata
    @NO_IMPLEMENTATION_EXPOSURE: Hides message complexity
    """
    return {
        'text': get_text(msg),  # Reuse existing text extractor
        'metadata': {
            'speaker': msg.get('type', 'unknown'),
            'uuid': msg.get('uuid', ''),
            'timestamp': msg.get('timestamp', ''),
            'session_id': msg.get('sessionId', '')
        }
    }


def export_for_llamaindex(jsonl_path: str, batch_size: int = None) -> Union[List[Dict[str, Any]], Iterator[List[Dict[str, Any]]]]:
    """Export conversation for LlamaIndex indexing with optional batching

    @API_FIRST: Public interface for semantic-search
    @FRAMEWORK_FIRST: 100% delegation to existing functions
    @ZERO_CUSTOM_CODE: No manual loops, only map and chunked

    Args:
        jsonl_path: Path to JSONL conversation file
        batch_size: Optional batch size for memory-efficient processing

    Returns:
        If batch_size=None: List of all documents
        If batch_size>0: Iterator yielding batches of documents
        Each document has:
        - text: Plain text content
        - metadata: speaker, uuid, timestamp, session_id
    """
    # Load using existing SDK
    session = load_session(jsonl_path)
    if not session:
        return [] if not batch_size else iter([])

    # Get messages
    messages = session.get('messages', [])

    # Filter using existing function (returns generator)
    clean_messages = filter_pure_conversation(messages)

    # Transform using map (no custom loops!)
    documents = map(_extract_document, clean_messages)

    # Return batched or full list based on batch_size
    if batch_size:
        # more-itertools handles all batching logic!
        return chunked(documents, batch_size)
    else:
        # Current behavior - return full list
        return list(documents)