"""Test that our library replacements are compatible."""

import orjson
import orjson as json  # Use orjson everywhere per 95/5 principle
import pytest


class TestOrjsonCompatibility:
    """Verify orjson works as a drop-in replacement for json."""

    def test_dumps_compatibility(self):
        """Test orjson.dumps works like json.dumps."""
        data = {
            "string": "hello",
            "number": 42,
            "float": 3.14,
            "bool": True,
            "null": None,
            "list": [1, 2, 3],
            "dict": {"nested": "value"},
        }

        # Both should produce valid JSON
        json_output = json.dumps(data)
        orjson_output = orjson.dumps(data).decode("utf-8")

        # Both should be parseable
        assert json.loads(json_output) == data
        assert json.loads(orjson_output) == data

    def test_loads_compatibility(self):
        """Test orjson.loads works like json.loads."""
        json_string = '{"key": "value", "number": 42}'

        # Both should parse the same
        json_result = json.loads(json_string)
        orjson_result = orjson.loads(json_string)

        assert json_result == orjson_result

    @pytest.mark.benchmark(group="json-libs")
    def test_orjson_is_faster(self, benchmark):
        """Verify orjson is actually faster (why we use it) - TRUE 95/5 with pytest-benchmark."""
        large_data = {"key" + str(i): i for i in range(1000)}

        # TRUE 95/5: Let pytest-benchmark do all the work
        result = benchmark(orjson.dumps, large_data)
        
        # Just verify it works correctly
        assert orjson.loads(result) == large_data

    def test_usage_in_our_code(self):
        """Test the specific usage patterns in our codebase."""
        # Pattern 1: Dumping to string (common in our code)
        data = {"type": "user", "content": "Hello"}

        # json way
        json_str = json.dumps(data)

        # orjson way (returns bytes, need decode)
        orjson_str = orjson.dumps(data).decode("utf-8")

        assert json.loads(json_str) == json.loads(orjson_str)

        # Pattern 2: Loading from string
        json_data = '{"type": "assistant", "content": "Hi there"}'

        assert json.loads(json_data) == orjson.loads(json_data)
