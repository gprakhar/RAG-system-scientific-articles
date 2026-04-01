# Optimal Chunking Strategy for Elsevier Peer-Reviewed Article PDFs

## Context

Elsevier publishes ~500,000 articles/year across ScienceDirect and related platforms. A RAG system over this corpus must handle:
- Diverse scientific domains (biomedical, chemistry, physics, social sciences)
- Complex layouts (multi-column, equations, tables, figures)
- IMRaD-structured scientific prose
- High retrieval precision demands (researchers expect exact, citable results)
- Scale: millions of documents in the index

The chunking layer is the single most consequential architectural decision in this pipeline — it determines what can and cannot be retrieved, and directly governs answer quality.

---

## The Core Problem: Why PDFs Are Hard

Before strategy, we must acknowledge what we are fighting:

| Problem | Impact |
|---|---|
| Multi-column layouts | Parser interleaves columns, destroying reading order |
| Mathematical equations | Text-only parsers flatten `e^{-βE}` to garbage |
| Figure/table interruption | Text flow broken; captions separated from narrative |
| Scanned PDFs (older journals) | OCR errors compound all other problems |
| Footnotes + endnotes | Rich signal content disconnected from main body |
| Supplementary materials | Often longer than main paper; usually ignored |
| Preprint vs. published versions | Same content, different layouts, duplicate indexing risk |

**Critical stat**: Even the best parsers achieve only ~60% accuracy on challenging scientific documents with equations and complex layouts (2024 OmniDocBench benchmark).

---

## Phase 1: Parsing Layer — Get Clean Text First

Chunking quality is bounded by parse quality. This is non-negotiable.

### Recommended: Dual-Parser Pipeline

```
PDF Input
   ├── GROBID → Structured XML/TEI (sections, bibliography, metadata)
   └── Nougat → Markdown with preserved LaTeX equations
       ↓
   Merge: GROBID structure + Nougat equation content
       ↓
   Table extraction (TATR / Camelot)
       ↓
   Figure caption extraction (PyMuPDF or vision model)
```

**Why GROBID as primary?**
- Specifically trained on academic papers
- Outputs TEI XML with explicit section boundaries, subsection hierarchy, and bibliography
- F1 = 0.89 on reference parsing (highest of 10 tools tested)
- Production-ready (Docker, REST API, LangChain integration)
- Free, open-source — important at Elsevier scale

**Why Nougat for equations?**
- Meta's model trained on arXiv papers
- Preserves LaTeX: `H₂O` stays `H_2O`, not `H2O`
- Handles subscripts, superscripts, Greek letters
- Trade-off: ~19.5s/page vs GROBID's 10.6 PDFs/s — use selectively for equation-heavy domains (physics, chemistry, math)

**Why not just one parser?**
- No single parser wins on all dimensions simultaneously
- GROBID's weakness is equations; Nougat's weakness is speed and table structure
- For Elsevier's scale, parallelize by domain: use Nougat for physics/chemistry, GROBID for biomedical/social sciences

### Elsevier-Specific Shortcut (Important!)
Elsevier **already has structured XML** via the ScienceDirect API and their internal content management system. For articles in ScienceDirect, **bypass PDF parsing entirely** and work from the source XML. This eliminates ~40% of parsing failures immediately. Reserve the PDF parsing pipeline for:
- External/ingested papers
- Backfile digitization
- Partner content without XML

---

## Phase 2: Chunking Strategy — The Recommended Approach

### Recommended: Structure-Aware Hierarchical Chunking with Small-to-Big Retrieval

This is a three-tier system.

```
Tier 1 (Macro): Document metadata chunk
  - Title, abstract, authors, DOI, journal, year, keywords
  - ~200-400 tokens
  - Purpose: high-level discovery queries ("papers about X by Y lab")

Tier 2 (Meso): Section-level summaries
  - Auto-generated summary of each IMRaD section
  - ~300-500 tokens
  - Purpose: "what does the Methods section say about statistical analysis?"

Tier 3 (Micro): Paragraph-level chunks (PRIMARY retrieval units)
  - Recursive splitting at 512 tokens, 75-token overlap
  - Respects sentence boundaries (no mid-sentence cuts)
  - Each chunk carries full metadata breadcrumb
  - Purpose: precise, citable evidence retrieval
```

**Why recursive 512-token with overlap?**
- Feb 2026 benchmark across 50 academic papers: **69% accuracy** — 15 percentage points above semantic chunking
- Overlap ensures boundary concepts aren't lost between adjacent chunks
- 512 tokens aligns well with most retrieval model context windows

**Why hierarchical tiers?**
- Different query types require different granularity
- "Summarize the methodology" → Tier 2
- "What p-value was reported for the main finding?" → Tier 3
- Multi-level retrieval can cascade: start broad, drill down

### The Small-to-Big Pattern (Critical for LLM Quality)

```
Index:  [child chunk 1] [child chunk 2] [child chunk 3]  ← ~256 tokens, for retrieval precision
                              ↕
Store:  [         parent chunk (600-800 tokens)        ]  ← returned to LLM for context richness
```

- **Retrieve** with small, precise child chunks (better embedding match to query)
- **Return** the surrounding parent chunk to the LLM (enough context to generate accurate answer)
- Optimal ratio: parent = 3-5x child size
- This directly addresses the "dangling reference" problem: "As shown in Figure 3..." is meaningless without the surrounding context explaining what Figure 3 shows

---

## Phase 3: Special Element Handling

### Figures
```
Figure → Vision model (GPT-4o / Claude) → descriptive summary
Caption text → extracted verbatim
Combined chunk: {caption} + {AI summary} + metadata: {figure_number, paper_doi, page}
```
Index figure chunks separately with `element_type: figure` metadata tag.

### Tables
```
Table → TATR extraction → structured markdown/JSON representation
Table caption → verbatim text
Combined chunk: {caption} + {markdown table or row-by-row summary}
```
For large tables (>50 rows), chunk by logical row groups with repeated headers.

### Equations
- Preserve LaTeX formatting — do not convert to plaintext
- If equation is inline, keep in paragraph chunk as-is
- If equation is display-block and multi-line, create a standalone equation chunk with surrounding sentence context
- Tag with `element_type: equation` and `notation: latex`

### References / Bibliography
- **Do not index reference list as retrievable chunks** — they contain no prose, just citation metadata
- Extract reference metadata via GROBID and store as structured data
- Link citing chunk → cited paper DOI for graph-based retrieval (GraphRAG pattern, optional)

### Abstract
- Always index as a standalone high-priority chunk (Tier 1)
- Abstracts are the highest-signal, densest summaries in scientific writing
- Use `section: abstract` metadata for boosted retrieval weighting

---

## Phase 4: Metadata Enrichment per Chunk

Every chunk should carry this envelope:

```json
{
  "chunk_id": "uuid",
  "document_doi": "10.1016/j.xxx.2024.xxx",
  "document_title": "...",
  "journal": "Cell",
  "publication_year": 2024,
  "authors": ["Smith, J.", "Lee, K."],
  "section": "Methods",
  "subsection_path": ["Methods", "Statistical Analysis", "Regression Models"],
  "chunk_index": 3,
  "total_chunks_in_section": 8,
  "has_equations": true,
  "has_table_reference": false,
  "has_figure_reference": true,
  "element_type": "text",
  "domain_keywords": ["p-value", "logistic regression", "confidence interval"],
  "mesh_terms": ["Statistics as Topic", "Regression Analysis"],
  "license": "CC-BY-4.0",
  "version": "published"
}
```

**Why this metadata matters:**
- Self-query retrieval: filter by journal, year, section before semantic search
- 15-25% precision improvement from metadata filtering (Azure RAG guidance)
- Enables section-aware retrieval: "only look in Methods sections"
- License metadata critical at Elsevier for downstream usage rights

---

## Failure Modes & Mitigations

| Failure | Root Cause | Mitigation |
|---|---|---|
| Equation garbling | Text-only parser | Use Nougat for math-heavy domains |
| Column interleaving | Poor layout detection | GROBID layout analysis; validate reading order |
| Mid-concept splits | Fixed chunking ignores semantics | Sentence-boundary-aware recursive splitting |
| "See Figure 3" orphan chunks | Figure reference without context | Small-to-big retrieval returns parent with context |
| Abstract missing from results | Poor section detection | Always index abstract as standalone Tier 1 chunk |
| Supplementary ignored | Not part of main PDF | Separate ingestion pipeline with explicit linkage |
| Duplicate preprint/published | Same content, different DOI | Canonical ID deduplication; prefer published DOI |
| Scanned/OCR PDFs | No embedded text | Flag for OCR pipeline; lower confidence score in metadata |

---

## What NOT to Do

1. **Don't use fixed-size chunking alone** — 13% accuracy in clinical RAG benchmarks (2025)
2. **Don't use semantic chunking as primary strategy** — higher compute, worse results than recursive in most benchmarks; 43-token average chunk size breaks retrieval
3. **Don't treat the reference list as retrievable text** — it adds noise, not signal
4. **Don't chunk mid-equation** — destroys mathematical meaning entirely
5. **Don't ignore supplementary materials** — increasingly contain the actual data and methods details
6. **Don't use a single-tier flat index** — loses the structural hierarchy that scientific papers provide for free

---

## Recommended Technology Stack

| Component | Tool | Notes |
|---|---|---|
| Primary parser | GROBID | Open-source, Docker |
| Math-heavy parser | Nougat | GPU-accelerated |
| Table extraction | TATR + Camelot | TATR for detection, Camelot for CSV |
| Figure understanding | Claude / GPT-4o | One-time ingestion cost |
| Chunking framework | LangChain RecursiveTextSplitter | 512 tokens, 75 overlap |
| Vector DB | Weaviate / Qdrant / Pinecone | With metadata filter support |
| Retrieval pattern | Parent-child document retriever | LangChain `ParentDocumentRetriever` |
| Hybrid search | BM25 + Dense embeddings | Weaviate or Elasticsearch hybrid |
| Embeddings | `text-embedding-3-large` or `e5-mistral-7b` | Benchmark on Elsevier corpus |

---

## Verification Plan

1. **Parser QA**: Sample 100 papers per domain; manually verify equation preservation, reading order, section detection rate
2. **Chunk QA**: Assert no chunk < 2 sentences; no chunk is pure citation list; no chunk splits mid-equation
3. **Retrieval eval**: Build golden dataset of 500 question-answer pairs with cited source; measure Recall@5 and MRR
4. **End-to-end eval**: RAGAS framework — faithfulness, answer relevancy, context precision, context recall
5. **Regression test**: After any pipeline change, run against golden dataset to detect degradation

---

---

## Literature Review

> All sources gathered during research for this plan. Grouped by topic area.

### PDF Parsing & Document Extraction

- **GROBID**: Romary & Sinclair (2015+), ongoing. Machine learning for extracting bibliographic data from scholarly documents. [GitHub](https://github.com/kermitt2/grobid). LangChain integration: https://python.langchain.com/docs/integrations/providers/grobid/
- **Nougat** — Blecher, N. et al. (2023). *Nougat: Neural Optical Understanding for Academic Documents*. Meta AI. [arXiv:2308.13418](https://arxiv.org/pdf/2308.13418). Key finding: superior equation preservation vs. classical parsers.
- **OmniDocBench** — Ouyang et al. (2025). *Benchmarking Diverse PDF Document Parsing with Comprehensive Annotations*. CVPR 2025. [Paper](https://openaccess.thecvf.com/content/CVPR2025/papers/Ouyang_OmniDocBench_Benchmarking_Diverse_PDF_Document_Parsing_with_Comprehensive_Annotations_CVPR_2025_paper.pdf). Key finding: even best parsers ~60% accuracy on complex scientific documents.
- **PDF Parsing Comparative Study** — (2024). *A Comparative Study of PDF Parsing Tools Across Diverse Document Categories*. [arXiv:2410.09871](https://arxiv.org/html/2410.09871v1). Tests PyMuPDF, PDFMiner, GROBID, Nougat across categories.
- **State of PDF Parsing** (2024). *The State of PDF Parsing: What 800+ Documents and 7 Frontier LLMs Taught Us*. Applied AI. [Link](https://www.applied-ai.com/briefings/pdf-parsing-benchmark/). Key finding: character corruption patterns documented.
- **Equation Extraction** — Florian (2024). *How to Extract Formulas from Scientific PDF Papers*. Medium. [Link](https://medium.com/@florian_algo/unveiling-pdf-parsing-how-to-extract-formulas-from-scientific-pdf-papers-a8f126f3511d).
- **ADAPARSE** (2025). *An Adaptive Parallel PDF Parsing and Resource Scaling Engine*. [arXiv:2505.01435](https://arxiv.org/pdf/2505.01435).
- **Document Parsing Survey** — (2024). *Document Parsing Unveiled: Techniques, Challenges, and Prospects*. [arXiv:2410.21169](https://arxiv.org/html/2410.21169v2).
- **PDF Library Benchmarks** — py-pdf project. [GitHub](https://github.com/py-pdf/benchmarks). PyMuPDF: 42ms vs PDFMiner: 2.5s per page.
- **Unstract 2026 Evaluation**. *Best Python PDF to Text Parser Libraries: A 2026 Evaluation*. [Link](https://unstract.com/blog/evaluating-python-pdf-to-text-libraries/).
- **GROBID Reference Parsing Benchmark** — Tkaczyk et al. (2018). *Machine Learning vs. Rules and Out-of-the-Box vs. Retrained*. [arXiv:1802.01168](https://arxiv.org/pdf/1802.01168). Key finding: GROBID F1=0.89, highest of 10 tools.

### Chunking Strategies

- **Recursive Chunking Benchmark** (Feb 2026). *RAG Chunking Strategies: The 2026 Benchmark Guide*. Premai Blog. [Link](https://blog.premai.io/rag-chunking-strategies-the-2026-benchmark-guide/). Key finding: recursive 512-token with 50-100 overlap = 69% accuracy across 50 academic papers.
- **Clinical Chunking Comparison** (Nov 2025). *Comparative Evaluation of Advanced Chunking for RAG in Clinical Decision Support*. PMC. [Link](https://pmc.ncbi.nlm.nih.gov/articles/PMC12649634/). Key finding: fixed-size 13% vs adaptive 87% accuracy.
- **Chunking Paradigm** (2025). *The Chunking Paradigm: Recursive Semantic for RAG Optimization*. ICNLSP. [PDF](https://aclanthology.org/2025.icnlsp-1.15.pdf).
- **Reconstructing Context** (2025). *Evaluating Advanced Chunking Strategies for RAG*. [arXiv:2504.19754](https://arxiv.org/abs/2504.19754).
- **Is Semantic Chunking Worth It?** (2024). [arXiv:2410.13070](https://arxiv.org/html/2410.13070v1). Key finding: semantic chunking benefits rarely justify computational cost; 43-token avg chunk size hurts retrieval.
- **Semantic Chunking Guide** — Weaviate. [Link](https://weaviate.io/blog/chunking-strategies-for-rag).
- **Chemistry RAG Chunking** (2025). *Chunk Twice, Embed Once: Chemistry-Aware Retrieval-Augmented Generation*. [arXiv:2506.17277](https://arxiv.org/html/2506.17277v1).
- **Max-Min Semantic Chunking** (2025). [Springer Link](https://link.springer.com/article/10.1007/s10791-025-09638-7).
- **Nine Chunking Strategies** (2025). Firecrawl Blog. [Link](https://www.firecrawl.dev/blog/best-chunking-strategies-rag).
- **Document Chunking 70% Accuracy** (2025). Langcopilot. [Link](https://langcopilot.com/posts/2025-10-11-document-chunking-for-rag-practical-guide).
- **Pinecone Chunking Strategies Guide**. [Link](https://www.pinecone.io/learn/chunking-strategies/).
- **Weaviate Chunking Blog**. [Link](https://weaviate.io/blog/chunking-strategies-for-rag).
- **Stack Overflow Blog on Chunking** (Dec 2024). [Link](https://stackoverflow.blog/2024/12/27/breaking-up-is-hard-to-do-chunking-in-rag-applications/).

### Hierarchical & Structure-Aware Chunking

- **HiChunk** (2025). *Evaluating and Enhancing Retrieval-Augmented Generation*. [arXiv:2509.11552](https://arxiv.org/pdf/2509.11552). QA benchmark for hierarchical document structure.
- **SF-RAG** (2026). *Structure-Fidelity Retrieval-Augmented Generation for Academic Question Answering*. [arXiv:2602.13647](https://arxiv.org/html/2602.13647). Treats native paper hierarchy as retrieval prior.
- **TreeRAG** (2025). *Unleashing the Power of Hierarchical Storage*. ACL Findings. [PDF](https://aclanthology.org/2025.findings-acl.20.pdf).
- **MultiDocFusion** (2025). *Hierarchical and Multimodal Chunking Pipeline for Enhanced RAG on Long Industrial Documents*. EMNLP. [Link](https://aclanthology.org/2025.emnlp-main.1062/).
- **Hierarchical Text Segmentation** (2025). *Enhancing RAG with Hierarchical Text Segmentation Chunking*. [arXiv:2507.09935](https://arxiv.org/html/2507.09935v1).
- **Hierarchical Chunking Guide** — Cobus Greyling. Medium. [Link](https://cobusgreyling.medium.com/hierarchical-chunking-in-rag-in-a-quick-guide-6c3193156efd).
- **Structural Preprocessing in RAG** (2025). *Evaluating Structural Preprocessing in RAG for Academic Curriculum Applications*. Springer. [Link](https://link.springer.com/chapter/10.1007/978-981-95-6786-7_33).

### Small-to-Big / Parent-Child Retrieval

- **Advanced RAG: Small-to-Big Retrieval** — Towards Data Science. [Link](https://medium.com/data-science/advanced-rag-01-small-to-big-retrieval-172181b396d4).
- **Parent-Child Chunking in LangChain**. Seahorse Technologies. [Link](https://medium.com/@seahorse.technologies.sl/parent-child-chunking-in-langchain-for-advanced-rag-e7c37171995a).
- **Parent-Child Retriever — GraphRAG**. [Link](https://graphrag.com/reference/graphrag/parent-child-retriever/).
- **Parent Document Retrieval** — DZone. [Link](https://dzone.com/articles/parent-document-retrieval-useful-technique-in-rag).
- **Dify v0.15.0**: Parent-child retrieval launch blog. [Link](https://dify.ai/blog/introducing-parent-child-retrieval-for-enhanced-knowledge).
- **Advanced Indexing Strategies**. APxml. [Link](https://apxml.com/courses/langchain-production-llm/chapter-4-production-data-retrieval/advanced-indexing-strategies).

### Late Chunking & ColBERT

- **Late Chunking** — Günther et al. (2024). *Late Chunking: Contextual Chunk Embedding*. Jina AI. [arXiv:2409.04701](https://arxiv.org/pdf/2409.04701). Embed full document, then chunk — preserves long-range context.
- **Late Chunking Weaviate** — *Balancing Precision and Cost in Long Context Retrieval*. [Link](https://weaviate.io/blog/late-chunking).
- **ColBERT Overview** — *An Overview of Late Interaction Retrieval Models: ColBERT, ColPali, ColQwen*. Weaviate. [Link](https://weaviate.io/blog/late-interaction-overview).
- **Late Chunking vs Contextual Retrieval** — KX Systems. [Link](https://medium.com/kx-systems/late-chunking-vs-contextual-retrieval-the-math-behind-rags-context-problem-d5a26b9bbd38).
- **ColBERT in RAG** — AI Forum. [Link](https://medium.com/the-ai-forum/supercharge-rag-with-contextualized-late-interactions-802a0f4a1e9d).
- **Late Chunking Evaluation** — Superlinked VectorHub. [Link](https://superlinked.com/vectorhub/articles/evaluation-rag-retrieval-chunking-methods).

### Propositional Chunking

- **RAG Techniques Notebook** — Nir Diamant. [GitHub](https://github.com/NirDiamant/RAG_Techniques/blob/main/all_rag_techniques/proposition_chunking.ipynb).
- **Five Levels of Chunking** — Medium (Greg's video notes). [Link](https://medium.com/@anuragmishra_27746/five-levels-of-chunking-strategies-in-rag-notes-from-gregs-video-7b735895694d). Propositional = Level 4.
- **ChunkRAG** (2024). *A Novel LLM-Chunk Filtering Method for RAG Systems*. [arXiv:2410.19572](https://arxiv.org/pdf/2410.19572).

### Metadata Enrichment

- **Metadata-Driven RAG for Finance** (2025). [arXiv:2510.24402](https://arxiv.org/html/2510.24402v1).
- **Self-Query Retrievers** — Medium. [Link](https://medium.com/@lorevanoudenhove/enhancing-rag-performance-with-metadata-the-power-of-self-query-retrievers-e29d4eecdb73).
- **Metadata for Better RAG** (2025). [arXiv:2601.11863](https://arxiv.org/html/2601.11863v1).
- **RAG Enrichment Phase** — Azure Architecture Center. [Link](https://learn.microsoft.com/en-us/azure/architecture/ai-ml/guide/rag/rag-enrichment-phase). 15-25% precision improvement from metadata filtering cited here.
- **Beyond Fixed Chunks** — Medium. [Link](https://medium.com/@shaikmohdhuz/beyond-fixed-chunks-how-semantic-chunking-and-metadata-enrichment-transform-rag-accuracy-07136e8cf562).
- **Automated Metadata Enrichment** — Haystack Cookbook. [Link](https://haystack.deepset.ai/cookbook/metadata_enrichment).
- **LLM-Generated Metadata for Enterprise RAG** (2024). [arXiv:2512.05411](https://arxiv.org/html/2512.05411v1).

### Multimodal RAG

- **Vision-Guided Chunking** (2025). *Vision-Guided Chunking Is All You Need: Enhancing RAG with Multimodal Document Understanding*. [arXiv:2506.16035](https://arxiv.org/pdf/2506.16035). HuggingFace: https://huggingface.co/papers/2506.16035
- **MHier-RAG** (2025). *Multi-Modal RAG for Visual-Rich Document Question-Answering*. [arXiv:2508.00579](https://arxiv.org/pdf/2508.00579).
- **Multimodal RAG with Tables** — Towards Data Science. [Link](https://towardsdatascience.com/building-a-multimodal-rag-with-text-images-tables-from-sources-in-response/).
- **Multimodal Semantic RAG** — GitHub. [Link](https://github.com/AhmedAl93/multimodal-semantic-RAG).

### RAG Surveys & Academic Literature Navigation

- **RAG Survey** — Gao et al. (2023). *Retrieval-Augmented Generation for Large Language Models: A Survey*. [arXiv:2312.10997](https://arxiv.org/abs/2312.10997).
- **Comprehensive RAG Survey** (2024). [arXiv:2410.12837](https://arxiv.org/abs/2410.12837).
- **Systematic RAG Review** (2025). [arXiv:2507.18910](https://arxiv.org/html/2507.18910v1).
- **Academic Literature Navigation RAG** (2024). *A Retrieval-Augmented Generation Framework for Academic Literature Navigation in Data Science*. [arXiv:2412.15404](https://arxiv.org/html/2412.15404v1).
- **Synergistic Multi-Stage RAG** (2025). *A Synergistic Multi-Stage RAG Architecture for Data Science Literature*. ScienceDirect. [Link](https://www.sciencedirect.com/science/article/pii/S294971912500055X).
- **RAG in Healthcare** (2025). [MDPI AI Journal](https://www.mdpi.com/2673-2688/6/9/226).
- **Production RAG Guide** (2026). Premai. [Link](https://blog.premai.io/building-production-rag-architecture-chunking-evaluation-monitoring-2026-guide/).

### Hybrid Search & Graph-Augmented Retrieval

- **Graph-Augmented Hybrid Retrieval** — Dev.to. [Link](https://dev.to/lucash_ribeiro_dev/graph-augmented-hybrid-retrieval-and-multi-stage-re-ranking-a-framework-for-high-fidelity-chunk-retrieval-in-rag-systems-50ca).
- **KG-Enhanced RAG** (2025). *Research on Construction and Application of RAG Model Based on Knowledge Graph*. Nature/Scientific Reports. [Link](https://www.nature.com/articles/s41598-025-21222-z).
- **Advanced RAG: Elastic** — Data Processing & Ingestion. [Link](https://www.elastic.co/search-labs/blog/advanced-rag-techniques-part-1).

---

## Open Questions for Discussion

1. **Domain prioritization**: Which subject areas (biomedical, chemistry, physics) should we tackle first? This determines parser choice weighting.
2. **ScienceDirect XML access**: Confirm availability of structured XML for the full backfile — this changes the pipeline significantly.
3. **Query type distribution**: What are users primarily asking? Factoid retrieval, literature synthesis, methods replication, or claim verification? This affects chunk size tuning.
4. **Multimodality timeline**: Is figure understanding (vision models) in scope for Phase 1, or a later iteration?
5. **Late Chunking**: For the most equation-dense domains, consider Jina AI's late chunking approach — embed full document first, chunk after. Higher compute but better semantic coherence.
