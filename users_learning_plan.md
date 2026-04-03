# From Zero to RAG & Agentic Hero
## A Practitioner's Learning Plan for Building a Scientific Literature Intelligence System

**Goal:** Build a production-grade agentic RAG system over 10,000 peer-reviewed biology papers from PubMed, deployed entirely on GCP.

**Prerequisites assumed:** Python fluency, basic NLP concepts, LLM API fundamentals.

**Estimated timeline:** 14–16 weeks (part-time, ~15 hrs/week)

---

## Phase 1: The Dumbest RAG That Works (Weeks 1–2)

### Why this phase matters
You need to feel the pain of naive RAG before you can appreciate why better approaches exist. Every failure you observe here becomes a lesson you internalize permanently. No frameworks — raw components only.

### Core concepts to learn
- Text embeddings: what they capture, what they lose
- Cosine similarity and dot product as distance metrics
- The retrieve-then-generate pattern
- Prompt construction with retrieved context
- Why "similarity ≠ relevance" (the central insight of our entire journey)

### What you build
A bare-bones RAG pipeline over 5 biology papers.

### Steps

**1.1 — Set up your GCP environment**
- Create a GCP project dedicated to this work
- Provision a Compute Engine VM (e2-standard-4 is fine to start; you won't need GPUs yet)
- Set up Cloud Storage bucket for your document corpus
- Install Python environment, Jupyter for experimentation
- Enable Vertex AI APIs (you'll use these for embeddings and LLM calls later)
- Set up a service account with appropriate IAM roles

**1.2 — Get your first 5 papers**
- Go to PubMed, pick 5 biology papers on a topic you find interesting (e.g., mTOR signaling, CRISPR applications, a specific pathway)
- Download the PDFs
- Upload them to your Cloud Storage bucket
- This small corpus lets you manually verify every retrieval result — essential for learning

**1.3 — Parse PDFs to text**
- Use PyMuPDF (fitz) for basic text extraction
- Write a simple script that extracts raw text from each PDF
- Observe the mess: two-column layouts merging incorrectly, figure captions interleaved with body text, tables becoming garbled strings, headers/footers repeating on every page
- **Document every parsing failure in a notebook.** This failure catalogue is gold.

**1.4 — Chunk the text**
- Start with the simplest strategy: fixed-size chunks of ~500 tokens with 50-token overlap
- Store each chunk as a dictionary: `{paper_id, chunk_id, text, source_page}`
- Count your chunks. For 5 papers you'll probably have 200–400 chunks.

**1.5 — Generate embeddings**
- Use Vertex AI's text embedding API (`text-embedding-005` model)
- Embed every chunk, store the vectors alongside the text
- Also try `text-embedding-005` with the `RETRIEVAL_DOCUMENT` and `RETRIEVAL_QUERY` task types — Vertex AI lets you specify these, and they matter
- Store everything in a Python list of dictionaries. Yes, a list. No database yet.

**1.6 — Build the retrieval function**
- Write a function: takes a query string, embeds it (with `RETRIEVAL_QUERY` task type), computes cosine similarity against all chunk vectors, returns top-k chunks
- Test with 10 questions you write yourself — questions whose answers you know from reading the papers
- For each question, examine the top-5 retrieved chunks manually. Ask: did it find the right content? Is the relevant information actually in these chunks?

**1.7 — Build the generation step**
- Take the top-5 chunks, format them into a prompt: "Based on the following excerpts from scientific papers, answer this question: {query}\n\nExcerpts:\n{chunks}\n\nAnswer:"
- Use Vertex AI's Gemini API (or Claude API) to generate the answer
- Evaluate: is the answer correct? Does it hallucinate? Does it cite the right papers?

**1.8 — Document your failure modes**
Write a structured analysis of what went wrong. You will likely observe:
- Chunks that are topically related but don't contain the actual answer
- Important context lost at chunk boundaries
- Figures and tables completely absent from retrieval
- The LLM confidently stating things that aren't in the retrieved text
- Queries about specific genes or proteins returning generic biology text

### Deliverable
A working Jupyter notebook with end-to-end naive RAG, plus a written analysis of its failure modes. This analysis is your roadmap for everything that follows.

### GCP services used
- Compute Engine (VM)
- Cloud Storage (document store)
- Vertex AI Embeddings API
- Vertex AI Gemini API (or Claude API via direct integration)

---

## Phase 2: Making Retrieval Smarter (Weeks 3–5)

### Why this phase matters
Each improvement you add teaches you a core retrieval concept. By changing one thing at a time, you isolate the impact of each technique — something you can never learn from a framework that bundles everything together.

### Core concepts to learn
- Vector indexes and approximate nearest neighbor (ANN) search
- Sparse retrieval (BM25) and why it complements dense retrieval
- Hybrid search and rank fusion algorithms
- Cross-encoder re-ranking
- Chunking strategies and their downstream effects
- Evaluation methodology for retrieval systems

### Steps

**2.1 — Replace your Python list with a real vector store**
- Option A (recommended to start): Use FAISS locally on your VM. It's a library, not a service, so zero infrastructure overhead. Learn the difference between `IndexFlatIP` (exact search) and `IndexIVFFlat` (approximate search). At 5 papers this doesn't matter, but the concepts matter when you scale.
- Option B (for later): Set up Vertex AI Vector Search (formerly Matching Engine). This is GCP's managed ANN service. It's overkill for now but you'll need it at scale. Bookmark the docs.
- Rebuild your retrieval using FAISS. Verify you get the same results as your Python list approach (you should, at this scale).

**2.2 — Add BM25 sparse retrieval**
- Install `rank-bm25` library
- Index the same chunks with BM25
- Run your same 10 test queries through BM25 only
- Compare results side-by-side with vector search results
- Key observation to make: find queries where BM25 wins (exact gene names, specific terminology like "Western blot") and queries where vectors win (paraphrased concepts, synonym matching)
- Understand *why* each method wins where it does

**2.3 — Implement hybrid search with Reciprocal Rank Fusion (RRF)**
- For each query, get top-20 from vector search and top-20 from BM25
- Implement RRF: for each document, `score = Σ 1/(k + rank_i)` where k is typically 60 and rank_i is its rank in each list
- Merge and re-sort by fused score
- Test on your 10 queries. Hybrid should beat either method alone on most queries.
- Experiment with weighting: try giving BM25 more weight for entity-heavy queries

**2.4 — Add a cross-encoder re-ranker**
- Use a cross-encoder model from `sentence-transformers` (e.g., `cross-encoder/ms-marco-MiniLM-L-12-v2`)
- Pipeline: hybrid search returns top-20 candidates → cross-encoder scores each (query, chunk) pair → re-sort by cross-encoder score → take top-5
- Compare retrieval quality before and after re-ranking
- Understand why this works: the cross-encoder sees query and document *together*, enabling token-level interaction that bi-encoders can't do
- Note the latency tradeoff: cross-encoders are 10–100x slower than bi-encoders, which is why you only run them on a small candidate set

**2.5 — Experiment with chunking strategies**
- Keep your original fixed-size chunks as baseline
- Implement semantic chunking: split on section boundaries (Abstract, Introduction, Methods, Results, Discussion)
- Implement sliding window with larger chunks (1000 tokens, 200 overlap)
- Implement parent-child chunking: index small chunks for precision, but retrieve the parent (larger surrounding context) for the LLM
- Run your 10 test queries against each strategy. Measure which one retrieves the most relevant content.
- This experiment teaches you that chunking is not a minor preprocessing detail — it fundamentally determines what your system can and cannot find

**2.6 — Build a proper evaluation framework**
- Expand your test set to 30 questions across different difficulty levels:
  - 10 factual lookup questions ("What concentration of X was used in study Y?")
  - 10 conceptual questions ("How does pathway X relate to disease Y?")
  - 10 synthesis questions ("What do these papers collectively suggest about mechanism Z?")
- For each question, manually identify the gold-standard passages that contain the answer
- Implement retrieval metrics:
  - Recall@k: of the relevant passages, how many appear in the top-k?
  - Precision@k: of the top-k retrieved passages, how many are actually relevant?
  - MRR (Mean Reciprocal Rank): how high does the first relevant passage rank?
- Track these metrics across every experiment you run from here on. This discipline is non-negotiable.

### Deliverable
A retrieval pipeline with hybrid search + re-ranking, multiple chunking strategies compared, and a 30-question evaluation benchmark with metrics. All in well-organized Python scripts (not just notebooks anymore).

### GCP services used
- Same as Phase 1, plus familiarity with Vertex AI Vector Search docs for future use

---

## Phase 3: Conquering Scientific PDFs (Weeks 5–7)

### Why this phase matters
This is where your system stops being a toy and starts handling real biology literature. PDF ingestion quality is the single biggest determinant of downstream performance. Most RAG tutorials skip this because it's hard and messy. You won't skip it.

### Core concepts to learn
- Structured document parsing vs raw text extraction
- Multimodal content handling (figures, tables, diagrams)
- Metadata extraction and enrichment
- Scientific entity recognition
- Document-level vs passage-level indexing

### Steps

**3.1 — Set up a proper PDF parsing pipeline**
- Install and test Docling (IBM's document parser — excellent for scientific papers)
- Also try PyMuPDF4LLM which outputs markdown-formatted text preserving some structure
- Parse your 5 papers with each tool. Compare output quality:
  - Does it correctly separate sections?
  - Does it handle two-column layouts?
  - Does it extract table content in a structured way?
  - Does it identify figure captions and link them to figure positions?
- Pick the best parser (likely Docling for your use case) and build your pipeline around it

**3.2 — Extract structured metadata**
- For each paper, extract and store:
  - Title, authors, journal, publication year, DOI
  - Abstract (separately — this is your document-level summary)
  - Section headings and their hierarchy
  - References list
- Use the PubMed API (Entrez) to enrich metadata: pull MeSH terms, keywords, and related article IDs for each paper. These become powerful filters later.
- Store metadata in a structured format (JSON or a lightweight database)

**3.3 — Handle figures and tables**
- Extract figures as images from PDFs (PyMuPDF can do this)
- Extract figure captions and associate them with the correct image
- Use Vertex AI's Gemini multimodal API to generate text descriptions of each figure:
  - For pathway diagrams: describe the components and their relationships
  - For charts/plots: describe what's being measured, trends, key data points
  - For gel images: describe lanes, bands, what's being demonstrated
- Store these descriptions as indexable text chunks, tagged with their source paper and figure number
- For tables: extract into structured format (pandas DataFrames) and also generate natural language summaries
- Index both the structured table data and the summary

**3.4 — Build a scientific entity extraction step**
- Use a biomedical NER model (scispaCy with the `en_ner_bionlp13cg_md` model, or PubMedBERT-based NER)
- Extract key entities from each paper: genes, proteins, diseases, organisms, chemicals, cell lines, experimental methods
- Store entities as metadata per chunk and per document
- This enables entity-based filtering at query time: "find papers about BRCA1" can first filter to papers containing that entity, then search within those

**3.5 — Scale to 100 papers**
- Download 100 papers from PubMed on your chosen topic area
- Run your full pipeline: parse → extract metadata → extract figures/tables → describe figures → extract entities → chunk → embed → index
- Build this as a proper batch pipeline, not a script you run manually. Use error handling and logging — some papers *will* fail to parse. Log failures, don't crash.
- Store the processed output in Cloud Storage with a clear directory structure
- Rebuild your FAISS index and BM25 index over the new corpus
- Re-run your evaluation benchmark. Metrics should improve (better parsing = better chunks = better retrieval)

**3.6 — Build a document-level index**
- Separate from your chunk-level index, create a document-level index:
  - Each entry represents one paper
  - Indexed content: abstract + LLM-generated 3-sentence finding summary + entities + MeSH terms
  - This enables coarse-grained retrieval: "which papers are about X?" before you drill into chunks
- This two-tier architecture (find relevant papers → find relevant passages within those papers) is fundamental to scaling

### Deliverable
A robust ingestion pipeline that handles scientific PDFs end-to-end (text, structure, figures, tables, metadata, entities), tested on 100 papers with measurable quality improvements over Phase 2.

### GCP services used
- Compute Engine (may need a beefier VM for NER and figure processing)
- Cloud Storage (structured corpus storage)
- Vertex AI Gemini API (multimodal — figure descriptions)
- Pub/Sub or Cloud Functions (optional, for pipeline orchestration)

---

## Phase 4: Agentic Retrieval (Weeks 8–10)

### Why this phase matters
Everything up to now has been single-shot retrieval: query in, chunks out. Real synthesis questions can't be answered in one pass. This phase teaches you to build systems that *think* about retrieval, execute multi-step plans, and self-correct.

### Core concepts to learn
- Tool use / function calling with LLMs
- Agent loops (observe-think-act cycles)
- Query decomposition
- Iterative retrieval with reasoning
- When to stop (termination conditions)
- Token budgets and cost management

### Steps

**4.1 — Define your tool set**
Design and implement these tools as Python functions that your LLM can call:

```
search_corpus(query, top_k=10)
  → Hybrid search over your chunk-level index. Returns ranked passages with metadata.

search_papers(query, top_k=5)
  → Search the document-level index. Returns paper summaries with IDs.

get_paper_sections(paper_id)
  → Returns the section headings and hierarchy for a specific paper.

read_section(paper_id, section_name)
  → Returns the full text of a specific section from a specific paper.

get_figure_description(paper_id, figure_number)
  → Returns the multimodal description of a figure.

get_table(paper_id, table_number)
  → Returns structured table data.

get_paper_entities(paper_id)
  → Returns the extracted biological entities for a paper.

find_papers_by_entity(entity_name, entity_type)
  → Searches the entity metadata to find all papers mentioning a specific gene/protein/disease.
```

Each tool should have a clear description that helps the LLM understand when to use it.

**4.2 — Build a basic agent loop**
- Use Claude's tool use API (or Vertex AI Gemini's function calling)
- The loop:
  1. Send user query + tool definitions to LLM
  2. LLM either responds with an answer or requests a tool call
  3. Execute the tool call, return result to LLM
  4. Repeat until LLM generates a final answer
- System prompt should instruct the agent to:
  - Think about what information it needs before searching
  - Use document-level search before diving into specific papers
  - Cross-reference findings across multiple papers
  - Cite specific papers and sections in its answer
  - State when evidence is conflicting or insufficient

**4.3 — Implement query decomposition**
- For complex queries, add a planning step before retrieval:
  - LLM receives the user's question
  - LLM outputs a plan: a list of sub-questions that need to be answered
  - Each sub-question is pursued through the agent loop
  - Results are synthesized at the end
- Example: "What is known about the relationship between autophagy and apoptosis in neurodegeneration?"
  - Sub-question 1: "Which papers discuss autophagy in neurodegeneration?"
  - Sub-question 2: "Which papers discuss apoptosis in neurodegeneration?"
  - Sub-question 3: "What molecular mechanisms link autophagy and apoptosis?"
  - Sub-question 4: "Are there conflicting findings?"
- Test this on your 10 synthesis questions from the evaluation benchmark

**4.4 — Add iterative retrieval with reasoning**
- After the agent retrieves information, it should evaluate:
  - "Do I have enough information to answer this question?"
  - "Are there gaps in what I've found?"
  - "Did any retrieved text reference other sections or papers I should check?"
- Implement a reflection step: after each retrieval round, the agent explicitly reasons about what it has and what it still needs
- Add a maximum step count (e.g., 10 tool calls) and a token budget to prevent runaway loops

**4.5 — Observe and debug agent behavior**
- Build comprehensive logging: every tool call, every LLM reasoning step, every retrieved passage
- Run your 30 evaluation questions through the agentic system
- Manually review the logs for at least 10 questions:
  - Did the agent decompose the query sensibly?
  - Did it search in the right places?
  - Did it go down any unproductive rabbit holes?
  - Did it know when to stop?
  - Where did it waste tool calls?
- This observability practice is critical. Agents are hard to debug without visibility into their reasoning.

**4.6 — Compare single-shot vs agentic retrieval**
- Run the same 30 questions through:
  - Your Phase 2 single-shot hybrid search + re-ranker
  - Your new agentic system
- Compare: answer quality, retrieval precision, citation accuracy, latency, cost (token usage)
- You should see agentic retrieval win decisively on synthesis questions but potentially be overkill (slower, more expensive) for simple factual lookups
- Build routing logic: classify incoming queries as "simple" or "complex" and use the appropriate retrieval strategy

### Deliverable
A working agentic RAG system with tool use, query decomposition, iterative retrieval, and comprehensive logging. Comparative evaluation against single-shot retrieval.

### GCP services used
- Compute Engine
- Cloud Storage
- Vertex AI APIs (Gemini for agent LLM, embeddings for search tools)
- Cloud Logging (for agent trace logs)

---

## Phase 5: Multi-Document Synthesis & Verification (Weeks 10–12)

### Why this phase matters
Retrieval is only half the problem. Your users — biologists — need the system to *synthesize* across papers, identify consensus and conflict, and never hallucinate a citation. This phase is where your system becomes genuinely useful.

### Core concepts to learn
- Multi-document synthesis prompting
- Citation verification and grounding
- Contradiction detection
- Evidence weighting (recency, methodology, impact)
- Structured output generation

### Steps

**5.1 — Design your synthesis prompt architecture**
- Don't try to do everything in one prompt. Build a multi-stage synthesis pipeline:
  - Stage 1: **Evidence gathering** — the agent retrieves relevant passages from multiple papers (Phase 4)
  - Stage 2: **Evidence extraction** — for each retrieved passage, extract the specific claim, the methodology used, the organism/cell line, and the year
  - Stage 3: **Evidence clustering** — group extracted claims by sub-topic (the LLM does this)
  - Stage 4: **Synthesis generation** — generate a structured synthesis that covers agreements, conflicts, gaps, and strength of evidence
  - Stage 5: **Citation verification** — check every citation in the synthesis against the retrieved passages

**5.2 — Implement citation verification**
- After the synthesis is generated, parse out every citation claim (e.g., "Smith et al. (2020) found that X increases Y")
- For each claim, retrieve the cited passage and use the LLM to verify: "Does this passage support this specific claim? Answer yes, no, or partially."
- Flag any unverified claims. Either remove them or mark them with a warning.
- This is non-negotiable for a scientific system. A single hallucinated citation destroys the credibility of the entire system with scientist users.

**5.3 — Build contradiction detection**
- When the agent gathers evidence from multiple papers, explicitly prompt it to identify:
  - Papers that agree on a finding
  - Papers that disagree or report conflicting results
  - Possible reasons for the conflict (different cell lines, different methodologies, different concentrations, in vitro vs in vivo)
- Structure the output so contradictions are surfaced clearly, not hidden in a fluent-sounding paragraph that glosses over them

**5.4 — Add evidence weighting**
- Not all papers are equal. Build heuristics for evidence strength:
  - Recency: a 2024 paper supersedes a 2015 paper on the same topic (usually)
  - Methodology: clinical trial > in vivo > in vitro > computational prediction
  - Journal impact: Nature > a predatory journal (use journal metadata from PubMed)
  - Replication: a finding reported in 5 papers is stronger than one reported in 1
- Include these weightings in the synthesis output: "Strong evidence from 4 recent studies supports X, while one older in vitro study suggests Y"

**5.5 — Generate structured synthesis outputs**
- Design an output format that scientists will actually find useful:
  - A one-paragraph executive summary of the answer
  - A detailed evidence synthesis organized by sub-topic
  - A table of supporting and conflicting evidence with citations
  - A "confidence assessment" noting where evidence is strong, weak, or absent
  - A list of suggested follow-up queries for deeper exploration
- Iterate on this format. Show it to a biologist friend if possible. Scientist feedback is invaluable.

**5.6 — Comprehensive evaluation**
- Expand your benchmark to 50 questions
- For each synthesis answer, evaluate:
  - Factual accuracy (does the answer match what the papers actually say?)
  - Citation accuracy (does every citation check out?)
  - Completeness (did it find all relevant papers in the corpus?)
  - Contradiction handling (did it surface real conflicts?)
  - Hallucination rate (did it fabricate any claims or citations?)
- Calculate metrics for each dimension. This becomes your system quality scorecard.

### Deliverable
A multi-document synthesis pipeline with citation verification, contradiction detection, and evidence weighting. Comprehensive evaluation across 50 benchmark questions.

### GCP services used
- Same as Phase 4
- BigQuery (optional — for storing evaluation results and tracking metrics over time)

---

## Phase 6: Knowledge Graph Layer (Weeks 12–14)

### Why this phase matters
Vector search finds similar text. Your agentic system can reason about documents. But neither naturally captures the *structured relationships* in your corpus: Gene X regulates Protein Y, Drug A inhibits Pathway B, Study 1 contradicts Study 2. A knowledge graph makes these relationships explicit, traversable, and queryable.

### Core concepts to learn
- Knowledge graph basics: nodes, edges, properties
- Relation extraction from scientific text
- Graph querying (Cypher or Gremlin)
- Graph-enhanced retrieval
- How agents can use graph traversal as a retrieval tool

### Steps

**6.1 — Design your graph schema**
- Define node types relevant to biology literature:
  - `Paper` (properties: title, year, journal, DOI)
  - `Gene` / `Protein`
  - `Disease`
  - `Pathway`
  - `Organism`
  - `Drug` / `Chemical`
  - `CellLine`
  - `ExperimentalMethod`
  - `Finding` (a specific claim from a specific paper)
- Define edge types:
  - `Paper → MENTIONS → Gene`
  - `Paper → REPORTS_FINDING → Finding`
  - `Gene → REGULATES → Gene`
  - `Drug → INHIBITS → Protein`
  - `Finding → SUPPORTS → Finding`
  - `Finding → CONTRADICTS → Finding`
  - `Paper → CITES → Paper`

**6.2 — Extract relationships**
- Use your entity extraction from Phase 3 as a starting point (you already have entities per paper)
- Build a relation extraction pipeline using the LLM:
  - For each paper section, prompt the LLM: "Extract biological relationships from this text. For each relationship, state: subject entity, relationship type, object entity, confidence, and the source sentence."
  - Parse the output into structured triples
  - This is imperfect and noisy. That's okay — you'll refine.
- Use scispaCy's relation extraction or REACH/Biofactoid if available for your domain

**6.3 — Set up a graph database on GCP**
- Option A: Deploy Neo4j on a Compute Engine VM (simplest for learning)
- Option B: Use a managed graph service — JanusGraph on Cloud Bigtable, or Neo4j AuraDB
- Load your extracted entities and relationships
- Learn basic Cypher queries:
  - "Find all genes that regulate BRCA1"
  - "Find all papers that mention both mTOR and glioblastoma"
  - "Find chains: Gene A → regulates → Gene B → associated_with → Disease C"

**6.4 — Add graph tools to your agent**
- New tools for the agent:
  ```
  query_knowledge_graph(cypher_query)
    → Execute a Cypher query and return results

  find_entity_connections(entity_name, max_hops=2)
    → Find all entities within N hops of a given entity

  find_common_connections(entity_a, entity_b)
    → Find shared connections between two entities (useful for "how does X relate to Y?" queries)

  get_evidence_for_relationship(entity_a, relationship, entity_b)
    → Find all papers and findings that support or contradict a specific relationship
  ```
- The agent can now reason: "The user asks about the connection between X and Y. Let me check the knowledge graph for known relationships, then search for papers that provide evidence for those relationships."

**6.5 — Evaluate graph-enhanced retrieval**
- Run your benchmark questions (especially the synthesis ones) with and without graph tools
- Measure: does the agent find relevant connections it would otherwise miss? Does synthesis quality improve?
- The graph should particularly help with:
  - "How does X relate to Y?" (path finding)
  - "What genes are involved in pathway Z?" (neighborhood queries)
  - "What are the conflicting findings about mechanism Q?" (contradiction edges)

### Deliverable
A knowledge graph populated from your corpus, integrated as agent tools, with measurable improvement on synthesis queries.

### GCP services used
- Compute Engine (Neo4j)
- Cloud Storage
- Vertex AI APIs

---

## Phase 7: Scale to 10,000 Papers & Production Hardening (Weeks 14–16)

### Why this phase matters
Everything until now ran on 100 papers. Real-world performance, reliability, and cost only reveal themselves at scale. This phase transforms your prototype into a system you could actually deploy.

### Core concepts to learn
- Batch processing pipelines on GCP
- Vector index management at scale
- Cost optimization (token usage, compute, storage)
- Monitoring and observability
- Failure handling and recovery

### Steps

**7.1 — Build the large-scale ingestion pipeline**
- Download 10,000 papers from PubMed using the Entrez API (respect rate limits)
- Set up a batch processing pipeline:
  - Cloud Storage trigger → Cloud Functions or Cloud Run → Processing pipeline
  - Steps: PDF parsing → metadata extraction → figure extraction → entity extraction → chunking → embedding → indexing
  - Each step should be idempotent and recoverable — if a paper fails at entity extraction, it shouldn't block the pipeline
  - Log all failures to Cloud Logging with enough detail to diagnose and retry
- Use Cloud Run Jobs for batch processing — it scales horizontally and you pay only for what you use
- Expect ~5–10% of papers to have parsing issues. Build a quarantine queue for manual review.

**7.2 — Scale your vector index**
- At 10,000 papers you'll have roughly 500K–1M chunks
- FAISS with IVF index is still viable on a single machine at this scale
- Alternatively, migrate to Vertex AI Vector Search for a managed solution:
  - Create an index endpoint
  - Deploy your embeddings
  - Benchmark query latency and recall vs your local FAISS
- Rebuild your BM25 index. At this scale, consider Elasticsearch on GCP (Elastic Cloud) for both BM25 and metadata filtering in one service.

**7.3 — Optimize for cost**
- Audit your token usage:
  - How many tokens per agent query? Track the distribution.
  - Which tool calls are most expensive? Can you cache frequent queries?
  - Are there cheaper models that work for specific steps? (e.g., a smaller model for entity extraction, a larger one for synthesis)
- Implement caching:
  - Cache embedding results (same text → same vector, no need to recompute)
  - Cache frequent entity lookups from the knowledge graph
  - Cache document-level index search results for popular queries
- Use Cloud Memorystore (Redis) for your caching layer

**7.4 — Add monitoring and observability**
- Instrument your system with:
  - Query latency tracking (end-to-end and per-step)
  - Retrieval quality logging (which chunks were retrieved, which were used in the answer)
  - Agent behavior logging (tool calls, reasoning steps, termination reason)
  - Cost per query tracking
  - Error rates by pipeline stage
- Set up dashboards in Cloud Monitoring
- Create alerts for: high error rates in ingestion, latency spikes in retrieval, unusual token consumption patterns

**7.5 — Build a simple API and interface**
- Wrap your system in a FastAPI service deployed on Cloud Run
- Endpoints:
  - `POST /query` — accepts a question, returns a synthesized answer with citations
  - `POST /query/stream` — streaming version for better UX
  - `GET /paper/{paper_id}` — returns metadata and summary for a specific paper
  - `GET /status` — system health check
- Build a minimal Streamlit or Gradio frontend for interactive use
- Deploy the frontend on Cloud Run

**7.6 — Final comprehensive evaluation**
- Run your full 50-question benchmark against the scaled system
- Add 20 new questions that specifically test cross-corpus synthesis (questions whose answers span 3+ papers)
- Measure everything: accuracy, citation fidelity, latency, cost per query, failure rate
- Compare metrics to your Phase 2 baseline. Document the improvement at each phase.
- Write up a "lessons learned" document. This is as valuable as the code itself.

### Deliverable
A production-ready agentic RAG system over 10,000 biology papers, accessible via API, with monitoring, caching, and comprehensive evaluation. Plus a detailed lessons-learned writeup.

### GCP services used
- Compute Engine / Cloud Run (services)
- Cloud Storage (corpus)
- Vertex AI (embeddings, LLM, vector search)
- Cloud Memorystore (caching)
- Cloud Monitoring + Cloud Logging (observability)
- Cloud Functions (pipeline triggers)
- Elastic Cloud on GCP or Vertex AI Search (BM25 at scale)
- Neo4j on Compute Engine (knowledge graph)

---

## GCP Architecture Summary

```
                    ┌──────────────────────────────┐
                    │       User Interface          │
                    │  (Streamlit on Cloud Run)      │
                    └──────────────┬───────────────┘
                                   │
                    ┌──────────────▼───────────────┐
                    │        FastAPI Service         │
                    │      (Cloud Run)               │
                    └──────────────┬───────────────┘
                                   │
                    ┌──────────────▼───────────────┐
                    │        Agent Core              │
                    │  (Query planning, tool use,    │
                    │   synthesis, verification)     │
                    └──────────────┬───────────────┘
                                   │
              ┌────────────┬───────┼───────┬────────────┐
              │            │       │       │            │
     ┌────────▼──┐  ┌──────▼──┐ ┌─▼────┐ ┌▼────────┐  │
     │  Vertex AI │  │  FAISS / │ │ BM25 │ │ Neo4j   │  │
     │  Gemini /  │  │  Vertex  │ │      │ │Knowledge│  │
     │  Claude    │  │  Vector  │ │      │ │ Graph   │  │
     │  API       │  │  Search  │ │      │ │         │  │
     └───────────┘  └─────────┘ └──────┘ └─────────┘  │
                                                        │
                    ┌──────────────────────────────┐   │
                    │    Cloud Storage               │◄──┘
                    │  (PDFs, processed docs,        │
                    │   metadata, figure images)     │
                    └──────────────────────────────┘
                    ┌──────────────────────────────┐
                    │    Ingestion Pipeline          │
                    │  (Cloud Run Jobs)              │
                    │  PDF parse → extract → embed   │
                    └──────────────────────────────┘
```

---

## Key Resources & Tools Reference

### PDF Parsing
- **Docling** — IBM's document parser, excellent for scientific papers
- **PyMuPDF / PyMuPDF4LLM** — fast, reliable PDF text extraction
- **Nougat** — Meta's academic document parser (neural-based)

### Embeddings
- **Vertex AI text-embedding-005** — GCP-native, supports task types
- **PubMedBERT / BiomedBERT** — domain-specific for biomedical text (via sentence-transformers)
- **BGE / E5** — strong general-purpose open-source models

### Vector Search
- **FAISS** — local library, great for development and moderate scale
- **Vertex AI Vector Search** — GCP managed service for production scale

### NER & Entity Extraction
- **scispaCy** — biomedical NLP pipelines with pre-trained NER models
- **PubTator** — NCBI's entity annotation service for PubMed articles

### Knowledge Graph
- **Neo4j** — most mature graph database, excellent Cypher query language

### Evaluation
- **RAGAS** — framework for evaluating RAG systems (faithfulness, relevance, etc.)
- **Custom benchmarks** — always build domain-specific evaluation; generic benchmarks don't capture scientific retrieval quality

### Frameworks (use AFTER you've built from scratch)
- **LlamaIndex** — good for document indexing abstractions once you understand the primitives
- **LangGraph** — useful for complex agent workflows once you've built a basic agent loop

---

## Principles to Live By

1. **Measure before you optimize.** Every change should be evaluated against your benchmark. Gut feeling is not a metric.

2. **Ingestion quality > retrieval algorithm.** A perfect retrieval algorithm over poorly parsed documents will lose to a mediocre algorithm over well-parsed documents. Every time.

3. **Build from scratch first, then use frameworks.** You need to understand what LangChain does before you decide whether it helps or hurts. Usually, for serious systems, simpler custom code wins.

4. **Your users are scientists.** They will verify your citations. They will catch hallucinations. They will lose trust permanently if your system fabricates evidence. Citation fidelity is not a nice-to-have — it is the core requirement.

5. **Similarity ≠ relevance.** This is the lesson that runs through everything. Keep it tattooed on your mental model.

6. **The best retrieval system is hybrid.** Vectors for recall, BM25 for precision, graphs for structure, re-rankers for refinement, agents for reasoning. Each layer compensates for the others' weaknesses.

7. **Log everything.** When your agent gives a wrong answer, you need to trace back through its reasoning to find where it went wrong. Without logs, debugging agents is like debugging code without a stack trace.
