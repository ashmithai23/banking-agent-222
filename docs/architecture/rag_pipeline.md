# Vector Knowledge Ingestion & RAG Pipeline

## Vector Store Configuration
- **Engine**: ChromaDB Persistent Client
- **Collection Name**: `vectrabank_knowledge`
- **Embedding Function**: Google Gemini text-embedding-004 / OpenAI text-embedding-3-small

## Pipeline Lifecycle
1. **Document Upload**: Multi-part upload via `/api/documents/upload` supporting `.pdf`, `.md`, and `.txt`.
2. **Text Extraction & Sanitization**: PyPDF / UTF-8 text readers extract content and strip non-printable tokens.
3. **Chunking Strategy**: Recursive character chunking with 800-character windows and 150-character overlaps.
4. **Metadata Annotation**: Chunks tagged with source filename, upload timestamp, and chunk sequence index.
5. **Context Injection**: Top-k semantic matches (k=4, cosine similarity >= 0.72) injected into LLM system prompts.
