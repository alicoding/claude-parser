#!/usr/bin/env python3
"""
Black box TDD test for export API
@TDD_REAL_DATA: Uses actual JSONL files
@API_FIRST_TEST_DATA: Only tests through public API
@LOC_ENFORCEMENT: <80 LOC
"""

from claude_parser.export import export_for_llamaindex  # The API we're testing


def test_export_to_llamaindex_format():
    """Black box test - call API, check output"""
    # Use real JSONL data
    test_file = "/Volumes/AliDev/ai-projects/claude-parser/jsonl-prod-data-for-test/-Volumes-AliDev-ai-projects-claude-parser/3a7770b4-aba3-46dd-b677-8fc2d71d4e06.jsonl"

    # Call the export API (this doesn't exist yet - TDD!)
    docs = export_for_llamaindex(test_file)

    # Check expected format
    assert isinstance(docs, list), "Should return list of documents"
    assert len(docs) > 0, "Should have documents"

    # Check first document structure
    first_doc = docs[0]
    assert 'text' in first_doc, "Document should have 'text' field"
    assert 'metadata' in first_doc, "Document should have 'metadata' field"

    # Check metadata fields
    metadata = first_doc['metadata']
    assert 'speaker' in metadata, "Should have speaker"
    assert metadata['speaker'] in ['user', 'assistant', 'system']
    assert 'uuid' in metadata, "Should have UUID"
    assert 'timestamp' in metadata, "Should have timestamp"

    # Check text is actually text, not JSON structure
    text = first_doc['text']
    assert isinstance(text, str), "Text should be string"
    assert not text.startswith('[{"type"'), "Text should be plain, not JSON"

    # Print sample for inspection
    print(f"\n=== BLACK BOX TEST OUTPUT ===")
    print(f"Total docs exported: {len(docs)}")
    print(f"First doc text: {docs[0]['text'][:100]}...")
    print(f"First doc speaker: {docs[0]['metadata']['speaker']}")

    return docs


if __name__ == "__main__":
    # Run to see output
    docs = test_export_to_llamaindex_format()
    print(f"\n✅ Export test passed! Generated {len(docs)} documents")