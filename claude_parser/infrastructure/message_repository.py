"""
Message repository implementation using functional programming.

SOLID:
- SRP: Single responsibility - data access for messages
- DIP: Implements abstract repository interface

95/5 Principle:
- Uses orjson (not json) per specification
- Uses pydantic for validation per specification
- NO manual loops, state, or mutations - pure functional
"""

from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import orjson
from pydantic import ValidationError
from toolz import concat, pipe
from toolz import filter as toolz_filter
from toolz import map as toolz_map

from ..domain.interfaces.protocols import MessageRepository
from ..domain.value_objects.metadata import ConversationMetadata
from ..models import Message
from ..models.parser import parse_message
from .logger_config import logger


class JsonlMessageRepository(MessageRepository):
    """Repository for loading messages from JSONL files using functional approach."""

    def __init__(self):
        # Store errors as immutable tuple, not mutable list
        self._last_errors: Tuple[Tuple[int, str], ...] = ()
        self._last_raw_messages: Tuple[Dict[str, Any], ...] = ()

    def load_messages(self, filepath: Path) -> List[Message]:
        """Load and validate messages from JSONL file functionally.

        Uses orjson and pydantic per specification.
        No manual loops or state mutations.
        """

        def parse_line_with_index(
            indexed_line: Tuple[int, bytes],
        ) -> Optional[Dict[str, str]]:
            """Parse a single line and return tagged result."""
            line_num, line = indexed_line
            stripped = line.strip()

            if not stripped:
                return None

            try:
                raw_msg = orjson.loads(stripped)
                return {"type": "raw", "line_num": line_num, "data": raw_msg}
            except orjson.JSONDecodeError as e:
                logger.warning(f"Line {line_num}: JSON decode error: {e}")
                return {
                    "type": "error",
                    "line_num": line_num,
                    "error": f"JSON decode error: {e}",
                }

        def process_raw_message(raw_result: Dict[str, Any]) -> List[Dict[str, Any]]:
            """Process raw message into parsed messages or errors."""
            if raw_result["type"] != "raw":
                return [raw_result]  # Pass through errors

            try:
                # Keep raw message for metadata extraction
                raw_msg_result = [
                    {"type": "raw_for_metadata", "data": raw_result["data"]}
                ]

                message = parse_message(raw_result["data"])
                if message:
                    # Handle embedded tools case
                    if isinstance(message, list):
                        return raw_msg_result + pipe(
                            message,
                            lambda msgs: toolz_map(
                                lambda m: {"type": "message", "data": m}, msgs
                            ),
                            list,
                        )
                    else:
                        return raw_msg_result + [{"type": "message", "data": message}]
                else:
                    return raw_msg_result + [
                        {
                            "type": "error",
                            "line_num": raw_result["line_num"],
                            "error": "Failed to parse message",
                        }
                    ]
            except ValidationError as e:
                logger.warning(f"Line {raw_result['line_num']}: Validation error: {e}")
                return [
                    {
                        "type": "error",
                        "line_num": raw_result["line_num"],
                        "error": f"Validation error: {e}",
                    }
                ]

        try:
            # Read file and process functionally
            with open(filepath, "rb") as f:
                lines = list(f)

            # Process all lines functionally
            all_results = pipe(
                enumerate(lines, 1),
                lambda x: toolz_map(parse_line_with_index, x),
                lambda x: toolz_filter(lambda item: item is not None, x),
                lambda x: toolz_map(process_raw_message, x),
                concat,
                list,
            )

            # Partition results
            errors = pipe(
                all_results,
                lambda x: toolz_filter(lambda item: item["type"] == "error", x),
                lambda x: toolz_map(lambda item: (item["line_num"], item["error"]), x),
                tuple,  # Store as immutable tuple
            )

            messages = pipe(
                all_results,
                lambda x: toolz_filter(lambda item: item["type"] == "message", x),
                lambda x: toolz_map(lambda item: item["data"], x),
                list,
            )

            raw_messages = pipe(
                all_results,
                lambda x: toolz_filter(
                    lambda item: item.get("type") == "raw_for_metadata", x
                ),
                lambda x: toolz_map(lambda item: item["data"], x),
                tuple,  # Store as immutable tuple
            )

            # Store results immutably
            self._last_errors = errors
            self._last_raw_messages = raw_messages

            logger.info(f"Loaded {len(messages)} messages from {filepath.name}")
            if errors:
                logger.warning(f"Failed to parse {len(errors)} messages")

            return messages

        except FileNotFoundError:
            logger.error(f"File not found: {filepath}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error loading {filepath}: {e}")
            raise

    def get_metadata_from_messages(
        self, messages: List[Message], filepath: Path
    ) -> ConversationMetadata:
        """Extract metadata from loaded messages functionally."""

        # Extract session_id functionally
        session_id = pipe(
            messages,
            lambda msgs: toolz_filter(
                lambda m: hasattr(m, "session_id") and m.session_id, msgs
            ),
            lambda msgs: toolz_map(lambda m: m.session_id, msgs),
            lambda ids: next(iter(ids), None),  # Get first or None
        )

        # Extract metadata from raw messages functionally
        def extract_field(field_name: str) -> Optional[str]:
            return pipe(
                self._last_raw_messages,
                lambda msgs: toolz_filter(lambda msg: field_name in msg, msgs),
                lambda msgs: toolz_map(lambda msg: msg[field_name], msgs),
                lambda values: next(iter(values), None),  # Get first or None
            )

        current_dir = extract_field("cwd")
        git_branch = extract_field("gitBranch")

        return ConversationMetadata(
            session_id=session_id,
            filepath=filepath,
            current_dir=current_dir,
            git_branch=git_branch,
            message_count=len(messages),
            error_count=len(self._last_errors),
        )

    def get_metadata(
        self, messages: List[Message], filepath: Path
    ) -> ConversationMetadata:
        """Alias for get_metadata_from_messages for backward compatibility."""
        return self.get_metadata_from_messages(messages, filepath)

    @property
    def errors(self) -> List[Tuple[int, str]]:
        """Get parsing errors from last load operation."""
        return list(self._last_errors)  # Convert tuple to list for compatibility

    def load_messages_streaming(self, filepath: Path):
        """Generator for streaming message loading."""
        # Yield messages in chunks for memory efficiency
        # Implementation for future if needed
