# CLAUDE.md

## Project Overview

A RAG (Retrieval-Augmented Generation) pipeline for peer-reviewed scientific articles, targeting Elsevier/ScienceDirect scale (millions of documents, diverse scientific domains).

**Current state:** Early implementation. Active modules: `src/pdf_reader.py`, `src/main.py`. Config: `config.yaml`. Tests: `tests/`. Reference docs: `claude_code_plan.md` (architecture), `literature-review.md` (research sources).

## Architecture

### Parsing Layer (Phase 1)
- **Primary**: GROBID (TEI XML output, section boundaries, bibliography) — use for biomedical/social sciences
- **Math-heavy domains**: Nougat (preserves LaTeX equations) — use for physics/chemistry, GPU required (~19.5s/page)
- **Elsevier shortcut**: For ScienceDirect articles, use structured XML from their API directly — bypasses PDF parsing entirely
- **Tables**: TATR for detection + Camelot for CSV extraction
- **Figures**: Vision model (Claude or GPT-4o) → descriptive summary + caption verbatim

### Chunking Strategy (Phase 2)
Three-tier hierarchical structure with **small-to-big retrieval**:

| Tier | Content | Size | Purpose |
|---|---|---|---|
| Tier 1 (Macro) | Document metadata + abstract | 200–400 tokens | High-level discovery |
| Tier 2 (Meso) | Section-level summaries (auto-generated) | 300–500 tokens | Section-scoped queries |
| Tier 3 (Micro) | Paragraph-level chunks — **primary retrieval unit** | 512 tokens, 75-token overlap | Precise citable retrieval |

**Small-to-big pattern**: Index small child chunks (~256 tokens) for retrieval precision; return parent chunks (600–800 tokens, 3–5x child size) to the LLM for context richness. Implemented via LangChain `ParentDocumentRetriever`.

### Metadata Envelope per Chunk
Every chunk must carry: `chunk_id`, `document_doi`, `title`, `journal`, `publication_year`, `authors`, `section`, `subsection_path`, `chunk_index`, `total_chunks_in_section`, boolean flags for equations/tables/figures, `element_type`, `domain_keywords`, `mesh_terms`, `license`, `version`.

### Recommended Tech Stack
- **Chunking**: LangChain `RecursiveTextSplitter` (512 tokens, 75 overlap)
- **Vector DB**: Weaviate / Qdrant / Pinecone (must support metadata filtering)
- **Retrieval**: `ParentDocumentRetriever` + hybrid BM25 + dense embeddings
- **Embeddings**: `text-embedding-3-large` or `e5-mistral-7b`

## Key Design Decisions (Do Not Revisit Without Benchmarks)

- **Recursive 512-token chunking beats semantic chunking** (69% vs 54% accuracy, 50-paper benchmark, Feb 2026). Do not default to semantic chunking.
- **No fixed-size flat chunking** — 13% accuracy on clinical benchmarks.
- **Reference lists are not retrievable chunks** — extract as structured data for graph-based retrieval only.
- **Equations must not be chunked mid-expression** — preserve as LaTeX, never convert to plaintext.
- **Supplementary materials require a separate ingestion pipeline** with explicit linkage to main paper.

## Evaluation Plan
- Parser QA: 100-paper sample per domain, manual verification of equation preservation and reading order
- Chunk QA: assert no chunk < 2 sentences, no mid-equation splits, no pure citation-list chunks
- Retrieval eval: 500-question golden dataset, measure Recall@5 and MRR
- End-to-end eval: RAGAS framework (faithfulness, answer relevancy, context precision, context recall)

## Development Guidelines

### Git & Commits

**Format:** `[Action] [Component]: Brief description`
- `Add pdf_reader: implement PDF text extraction`
- `Fix config: correct output path resolution`

**Never:**
- Include "Co-Authored-By: Claude" or "Generated with Claude Code" in commit messages
- Combine unrelated changes in one commit
- Commit broken or non-functional code

### Code Style

- **Named arguments**: Always use keyword arguments in function calls — `func(param=value)`, never positional
- **Type hints**: All function signatures must have type annotations
- **Package manager**: Use `uv` — never `pip` or `poetry`
- **Imports**: Do not prefix module imports with `src.` — the build system adds `src/` to the path, so modules are imported directly (e.g. `from pdf_reader import read_pdf`, not `from src.pdf_reader import read_pdf`)

### Documentation

Google-style docstrings on all modules, classes, and functions. Minimum required fields: description, `Args:`, `Returns:`, `Raises:` (if applicable).

```python
def read_pdf(file_path: str, output_path: str) -> None:
    """Read all PDFs in a directory and write extracted text to output.

    Args:
        file_path: Path to directory containing input PDF files.
        output_path: Path to directory where output text files are written.
    """
```

### Logging & Error Handling

- Use Python's `logging` module — never `print()` for runtime output
- Log at every significant operation, state change, and error — with enough context to diagnose without a debugger
- Catch specific exceptions only — never bare `except:` or silent `except Exception: pass`
- Always log the error before re-raising or returning a fallback

### Testing

- Write tests for every feature — both success and failure paths
- Do not mock components where the real implementation must be exercised (e.g. actual file I/O, real API responses) — test against real behaviour at system boundaries
- Each source module in `src/` gets a corresponding test file in `tests/` — e.g. `src/pdf_reader.py` → `tests/test_pdf_reader.py`
- Standard structure:
  ```
  tests/
    __init__.py
    test_pdf_reader.py
    test_<module>.py
    ...
  ```
