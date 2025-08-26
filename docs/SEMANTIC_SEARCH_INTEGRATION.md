# Semantic Search Integration Plan

## Current Status
Removed temporary implementation. Waiting for `semantic-search-service` SDK to be completed.

## Challenges Discovered

### 1. Rate Limiting Complexity
- ElectronHub: 7 RPM (free tier) with 3-minute cooldown on violation
- OpenAI: Different tiers with different limits
- Each provider has different error codes and cooldown requirements

### 2. Embedding API Differences
- ElectronHub uses `/embeddings` endpoint (not OpenAI-compatible)
- Different auth headers and request formats
- Need custom clients for each provider

### 3. Indexing Challenges
- Large codebases exceed rate limits quickly
- Need intelligent chunking and batching
- Must cache embeddings to avoid re-processing

### 4. Memory Management
- Vector indexes consume significant memory
- Need persistence for large projects
- Incremental indexing for file changes

## Requirements for semantic-search-service SDK

### Core Features Needed
1. **Provider Abstraction**
   - Support multiple embedding providers (OpenAI, ElectronHub, Ollama, etc.)
   - Automatic fallback between providers
   - Provider-specific rate limit handling

2. **Smart Rate Limiting**
   - Per-provider rate limit tracking
   - Automatic cooldown management
   - Request queuing and batching
   - Exponential backoff with jitter

3. **Efficient Indexing**
   - Incremental indexing (only changed files)
   - Cached embeddings with versioning
   - Background indexing with progress callbacks
   - Multi-project index management

4. **Search Interface**
   ```python
   from semantic_search_service import SemanticSearchSDK
   
   sdk = SemanticSearchSDK(
       project_path="/path/to/project",
       provider="auto",  # Auto-select best available
       cache_dir="~/.semantic-search-cache"
   )
   
   # Async indexing with progress
   await sdk.index_project(
       file_patterns=["*.py", "*.md"],
       max_files=100,
       on_progress=lambda p: print(f"Indexed: {p}%")
   )
   
   # Search with various modes
   results = await sdk.search(
       query="todo domain implementation",
       mode="semantic",  # or "hybrid", "keyword"
       top_k=5,
       filters={"file_type": "python"}
   )
   ```

5. **Caching & Persistence**
   - SQLite/DuckDB for embedding storage
   - File hash tracking for change detection
   - Automatic cache invalidation
   - Export/import index capability

## Migration Plan

### Phase 1: Wait for SDK (Current)
- No temporary implementation 
- semantic-search-service is being developed with proper architecture
- Will provide clean SDK interface

### Phase 2: SDK Integration (When Ready)
1. Install semantic-search-service SDK
2. Replace `ElectronHubEmbedding` with SDK client
3. Remove manual rate limiting code
4. Migrate to SDK's search interface

### Phase 3: Full Integration
- Use SDK for all search operations
- Leverage caching and persistence
- Enable background indexing
- Support multiple projects

## semantic-search-service Architecture (From Exploration)

### Key Design Decisions
- **Vector DB**: Qdrant (better incremental updates than Chroma)
- **DDD Architecture**: 5 bounded contexts
  - Code Intelligence (semantic search)
  - Architecture Analysis (project structure)
  - Library Knowledge (dependencies)
  - Quality Analysis (violations)
  - Documentation Generation
- **API Gateway Pattern**: FastAPI orchestrating contexts
- **Proper DI**: dependency-injector for clean testing

## Notes for semantic-search-service Development

### Lessons Learned
1. **Don't underestimate rate limits** - They're stricter than expected
2. **Batch size matters** - Even batch_size=10 can hit limits
3. **Cooldown is real** - 3-minute wait is enforced strictly
4. **Different tiers need different strategies** - Free vs paid tiers

### Suggested Architecture
```
semantic-search-service/
├── sdk/
│   ├── __init__.py
│   ├── client.py          # Main SDK client
│   ├── providers/         # Provider implementations
│   │   ├── base.py
│   │   ├── openai.py
│   │   ├── electronhub.py
│   │   └── ollama.py
│   ├── rate_limiter.py    # Smart rate limiting
│   ├── indexer.py         # Indexing engine
│   ├── cache.py           # Caching layer
│   └── search.py          # Search algorithms
├── server/                # Optional REST API
└── cli/                   # CLI tools
```

## Dependencies to Consider
- `llama-index` - Good base but needs heavy customization
- `chromadb` or `qdrant` - For vector storage
- `sqlite-vec` - Lightweight vector extension for SQLite
- `tenacity` - For retry logic
- `httpx` - Async HTTP client
- `diskcache` - For embedding cache

## Action Items
1. ✅ Document current implementation challenges
2. ✅ Define SDK requirements
3. ⏳ Wait for semantic-search-service SDK
4. 📝 Migrate when ready