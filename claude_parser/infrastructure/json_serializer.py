"""Central JSON serialization service - ONLY file that imports msgspec.

SOLID: Single Responsibility - only this service handles JSON serialization.
All other files call SDK methods and get strings back.
"""

from typing import Any
import msgspec


class JsonSerializer:
    """Central JSON serialization service.

    The ONLY place in the entire codebase that handles JSON serialization.
    All other components call SDK methods and receive strings.
    """

    @staticmethod
    def serialize(data: Any) -> str:
        """Serialize data to JSON string."""
        return msgspec.json.encode(data).decode()

    @staticmethod
    def serialize_lines(data_list: list[Any]) -> str:
        """Serialize list to JSON Lines format."""
        return "\n".join(JsonSerializer.serialize(item) for item in data_list)

    @staticmethod
    def deserialize_safe(data: bytes) -> tuple[bool, Any]:
        """Deserialize JSON with error handling.

        Returns: (success, result_or_error_string)
        """
        try:
            return True, msgspec.json.decode(data)
        except msgspec.DecodeError as e:
            return False, str(e)

    @staticmethod
    def deserialize_message_safe(data: bytes):
        """Deserialize JSON as validated Message with error handling.

        For MessageRepository to use instead of direct msgspec calls.
        Returns: (success, message_or_error)
        """
        from ..msgspec_models import Message  # Import here to avoid circular deps
        try:
            message = msgspec.json.decode(data, type=Message)
            raw_data = msgspec.json.decode(data)  # Also get raw dict
            return True, {"message": message, "raw": raw_data}
        except msgspec.DecodeError as e:
            return False, str(e)


# Global instance for SDK to use
_json_serializer = JsonSerializer()
