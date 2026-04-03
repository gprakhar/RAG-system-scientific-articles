# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Status

This repository is in the **planning phase** — no implementation code exists yet. The codebase currently contains:

- `claude_code_plan.md` — The primary architecture and strategy document. The authoritative source for all design decisions, with benchmarks and rationale.
- `literature-review.md` — Annotated bibliography of all research sources used to inform the architecture.
- `docs/example_input_docs/` — Sample peer-reviewed PDFs for testing the pipeline once built.

## What This System Does

A RAG (Retrieval-Augmented Generation) pipeline for peer-reviewed scientific articles, targeting Elsevier/ScienceDirect scale (millions of documents, diverse scientific domains).

## Planned Architecture

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
