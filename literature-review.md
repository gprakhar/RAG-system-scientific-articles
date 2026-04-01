# Literature Review: Chunking Strategies for Scientific Article PDFs in RAG Systems

> Compiled: 2026-03-26
> Context: Day 1 research for Elsevier AI RAG roadmap — optimal chunking of peer-reviewed article PDFs.

---

## PDF Parsing & Document Extraction

- **GROBID** — Romary & Sinclair (2015+), ongoing. Machine learning software for extracting information from scholarly documents. Outputs TEI XML with section boundaries, subsection hierarchy, and bibliography. Production-ready (Docker, REST API, LangChain integration).
  - [GitHub](https://github.com/kermitt2/grobid)
  - [LangChain GROBID Integration](https://python.langchain.com/docs/integrations/providers/grobid/)
  - [How to Use GROBID to Extract Text from PDFs — Medium](https://medium.com/@researchgraph/how-to-use-grobid-67df995b16fa)

- **GROBID Reference Parsing Benchmark** — Tkaczyk et al. (2018). *Machine Learning vs. Rules and Out-of-the-Box vs. Retrained*. Key finding: GROBID achieves F1=0.89, highest of 10 tools tested.
  - [arXiv:1802.01168](https://arxiv.org/pdf/1802.01168)

- **Nougat** — Blecher, N. et al. (2023). *Nougat: Neural Optical Understanding for Academic Documents*. Meta AI. Transformer encoder-decoder model trained on arXiv papers. Preserves LaTeX equations, Greek letters, subscripts/superscripts that text-only parsers destroy. ~19.5s/page (GPU required).
  - [arXiv:2308.13418](https://arxiv.org/pdf/2308.13418)

- **OmniDocBench** — Ouyang et al. (2025). *Benchmarking Diverse PDF Document Parsing with Comprehensive Annotations*. CVPR 2025. Key finding: even best parsers achieve only ~60% accuracy on complex scientific documents with equations and multi-column layouts.
  - [CVPR 2025 Paper](https://openaccess.thecvf.com/content/CVPR2025/papers/Ouyang_OmniDocBench_Benchmarking_Diverse_PDF_Document_Parsing_with_Comprehensive_Annotations_CVPR_2025_paper.pdf)

- **A Comparative Study of PDF Parsing Tools Across Diverse Document Categories** (2024). Tests PyMuPDF, PDFMiner, GROBID, Nougat across academic, legal, and financial document categories. PyMuPDF: 42ms/page; PDFMiner: 2.5s/page. Scientific papers most challenging category.
  - [arXiv:2410.09871](https://arxiv.org/html/2410.09871v1)

- **The State of PDF Parsing: What 800+ Documents and 7 Frontier LLMs Taught Us** (2024). Applied AI. Documents character corruption patterns: whitespace injection, character scrambling, garbled SMILES notation, flattened subscripts.
  - [Applied AI Blog](https://www.applied-ai.com/briefings/pdf-parsing-benchmark/)

- **How to Extract Formulas from Scientific PDF Papers** — Florian (2024). Covers equation extraction approaches using Nougat, GROBID XML markup, and hybrid methods.
  - [Medium](https://medium.com/@florian_algo/unveiling-pdf-parsing-how-to-extract-formulas-from-scientific-pdf-papers-a8f126f3511d)

- **ADAPARSE: An Adaptive Parallel PDF Parsing and Resource Scaling Engine** (2025). Adaptive routing of documents to parsers based on complexity features.
  - [arXiv:2505.01435](https://arxiv.org/pdf/2505.01435)

- **Document Parsing Unveiled: Techniques, Challenges, and Prospects for Structured Information Extraction** (2024). Comprehensive survey of document parsing methods including layout analysis, table/figure extraction, and reading order detection.
  - [arXiv:2410.21169](https://arxiv.org/html/2410.21169v2)

- **py-pdf Benchmarks** — Open-source PDF library benchmarking project. Speed and accuracy comparisons.
  - [GitHub](https://github.com/py-pdf/benchmarks)

- **Best Python PDF to Text Parser Libraries: A 2026 Evaluation** — Unstract (2026).
  - [Unstract Blog](https://unstract.com/blog/evaluating-python-pdf-to-text-libraries/)

- **Comparing PDF Parsers** — McGough (2024). Practical comparison of PyMuPDF, pdfplumber, PDFMiner, pypdf.
  - [Medium](https://medium.com/@bpmcgough/comparing-pdf-parsers-1b9f5ae24afe)

- **Introducing PDF Parser v2: Faster Extraction with Auto Mode** — Firecrawl (2024).
  - [Firecrawl Blog](https://www.firecrawl.dev/blog/pdf-parser-v2)

---

## Chunking Strategies — Core Literature

- **RAG Chunking Strategies: The 2026 Benchmark Guide** — Premai (Feb 2026). Benchmarks across 50 academic papers. Key finding: **recursive 512-token with 50-100 token overlap achieves 69% accuracy** — 15 percentage points above semantic chunking on the same corpus.
  - [Premai Blog](https://blog.premai.io/rag-chunking-strategies-the-2026-benchmark-guide/)

- **Comparative Evaluation of Advanced Chunking for Retrieval-Augmented Generation in Large Language Models for Clinical Decision Support** (Nov 2025). PMC. Key finding: fixed-size chunking 13% accuracy vs. adaptive chunking 87% accuracy on clinical document QA.
  - [PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC12649634/)

- **The Chunking Paradigm: Recursive Semantic for RAG Optimization** (2025). ICNLSP proceedings. Comparative analysis of recursive vs. semantic strategies.
  - [ACL Anthology PDF](https://aclanthology.org/2025.icnlsp-1.15.pdf)

- **Reconstructing Context: Evaluating Advanced Chunking Strategies for Retrieval-Augmented Generation** (2025).
  - [arXiv:2504.19754](https://arxiv.org/abs/2504.19754)

- **Is Semantic Chunking Worth the Computational Cost?** (2024). Key finding: semantic chunking "occasionally improved performance on high-diversity datasets, but these benefits were insufficient to justify additional computational cost." Average chunk size of 43 tokens from semantic methods is too small for effective retrieval.
  - [arXiv:2410.13070](https://arxiv.org/html/2410.13070v1)

- **Max–Min Semantic Chunking of Documents for RAG Application** (2025). Springer. Proposes balanced semantic chunk sizing to avoid the 43-token fragment problem.
  - [Springer](https://link.springer.com/article/10.1007/s10791-025-09638-7)

- **Chunk Twice, Embed Once: A Systematic Study of Segmentation and Representation Trade-offs in Chemistry-Aware Retrieval-Augmented Generation** (2025). Domain-specific findings for chemistry papers with complex notation.
  - [arXiv:2506.17277](https://arxiv.org/html/2506.17277v1)

- **An Evaluation of RAG Retrieval Chunking Methods** — Superlinked VectorHub.
  - [Superlinked](https://superlinked.com/vectorhub/articles/evaluation-rag-retrieval-chunking-methods)

- **Best Chunking Strategies for RAG in 2025/2026** — Firecrawl.
  - [Firecrawl Blog](https://www.firecrawl.dev/blog/best-chunking-strategies-rag)

- **Document Chunking for RAG: 9 Strategies Tested (70% Accuracy Boost 2025)** — Langcopilot.
  - [Langcopilot](https://langcopilot.com/posts/2025-10-11-document-chunking-for-rag-practical-guide)

- **Chunking Strategies for LLM Applications** — Pinecone. Comprehensive practitioner guide.
  - [Pinecone](https://www.pinecone.io/learn/chunking-strategies/)

- **Breaking Up is Hard to Do: Chunking in RAG Applications** — Stack Overflow Blog (Dec 2024).
  - [Stack Overflow Blog](https://stackoverflow.blog/2024/12/27/breaking-up-is-hard-to-do-chunking-in-rag-applications/)

- **Chunking Strategies to Improve LLM RAG Pipeline Performance** — Weaviate.
  - [Weaviate Blog](https://weaviate.io/blog/chunking-strategies-for-rag)

- **Building Production RAG: Architecture, Chunking, Evaluation & Monitoring (2026 Guide)** — Premai.
  - [Premai Blog](https://blog.premai.io/building-production-rag-architecture-chunking-evaluation-monitoring-2026-guide/)

- **11 Chunking Strategies for RAG — Simplified & Visualized** — Medium.
  - [Medium](https://masteringllm.medium.com/11-chunking-strategies-for-rag-simplified-visualized-df0dbec8e373)

---

## Hierarchical & Structure-Aware Chunking

- **HiChunk: Evaluating and Enhancing Retrieval-Augmented Generation** (2025). Introduces QA benchmark specifically designed to evaluate hierarchical document structure handling in RAG.
  - [arXiv:2509.11552](https://arxiv.org/pdf/2509.11552)

- **SF-RAG: Structure-Fidelity Retrieval-Augmented Generation for Academic Question Answering** (2026). Treats native paper hierarchy as retrieval prior; uses IMRaD structure to guide chunk organization and retrieval cascade.
  - [arXiv:2602.13647](https://arxiv.org/html/2602.13647)

- **TreeRAG: Unleashing the Power of Hierarchical Storage** (2025). ACL Findings. Tree-structured document organization for RAG retrieval.
  - [ACL Anthology PDF](https://aclanthology.org/2025.findings-acl.20.pdf)

- **MultiDocFusion: Hierarchical and Multimodal Chunking Pipeline for Enhanced RAG on Long Industrial Documents** (2025). EMNLP. LLM-based hierarchical reconstruction for long documents; multimodal support.
  - [ACL Anthology](https://aclanthology.org/2025.emnlp-main.1062/)

- **Enhancing Retrieval Augmented Generation with Hierarchical Text Segmentation Chunking** (2025).
  - [arXiv:2507.09935](https://arxiv.org/html/2507.09935v1)

- **Hierarchical Chunking in RAG: A Quick Guide** — Cobus Greyling. Practitioner overview.
  - [Medium](https://cobusgreyling.medium.com/hierarchical-chunking-in-rag-in-a-quick-guide-6c3193156efd)

- **Evaluating Structural Preprocessing in RAG for Academic Curriculum Applications** (2025). Springer. Academic domain-specific structural chunking evaluation.
  - [Springer Chapter](https://link.springer.com/chapter/10.1007/978-981-95-6786-7_33)

- **A Retrieval-Augmented Generation Framework for Academic Literature Navigation in Data Science** (2024). Multi-stage retrieval with document structure awareness.
  - [arXiv:2412.15404](https://arxiv.org/html/2412.15404v1)

- **A Synergistic Multi-Stage RAG Architecture for Boosting Context Relevance in Data Science Literature** (2025). ScienceDirect.
  - [ScienceDirect](https://www.sciencedirect.com/science/article/pii/S294971912500055X)

---

## Small-to-Big / Parent-Child Retrieval

- **Advanced RAG 01: Small-to-Big Retrieval** — Towards Data Science. Index small child chunks (~256 tokens) for precise retrieval; return larger parent chunks (600-800 tokens) to LLM for context richness. Optimal parent:child ratio = 3-5x.
  - [Medium / TDS](https://medium.com/data-science/advanced-rag-01-small-to-big-retrieval-172181b396d4)

- **Parent-Child Chunking in LangChain for Advanced RAG** — Seahorse Technologies. Implementation guide using `ParentDocumentRetriever`.
  - [Medium](https://medium.com/@seahorse.technologies.sl/parent-child-chunking-in-langchain-for-advanced-rag-e7c37171995a)

- **Parent-Child Retriever — GraphRAG Reference**.
  - [GraphRAG Docs](https://graphrag.com/reference/graphrag/parent-child-retriever/)

- **Parent Document Retrieval: Useful Technique in RAG** — DZone.
  - [DZone](https://dzone.com/articles/parent-document-retrieval-useful-technique-in-rag)

- **Dify v0.15.0: Introducing Parent-child Retrieval for Enhanced Knowledge** — Launch blog with product rationale.
  - [Dify Blog](https://dify.ai/blog/introducing-parent-child-retrieval-for-enhanced-knowledge)

- **Advanced Indexing Strategies for RAG** — APxml LangChain Course.
  - [APxml](https://apxml.com/courses/langchain-production-llm/chapter-4-production-data-retrieval/advanced-indexing-strategies)

- **All You Need to Know About Chunking in Agentic RAG** — Towards AI.
  - [Towards AI](https://pub.towardsai.net/all-you-need-to-know-about-chunking-in-agentic-rag-bdc34c21a6e6)

- **Advanced Chunking Strategies for RAG** — Addaxis AI.
  - [Addaxis Blog](https://addaxis.ai/advanced-chunking-strategies-for-rag/)

---

## Late Chunking & ColBERT

- **Late Chunking: Contextual Chunk Embedding** — Günther et al. (2024). Jina AI. Embed the full document through a long-context model first, then pool token vectors into chunks after the fact. Each chunk vector carries awareness of the entire document context, solving the "lost context" problem.
  - [arXiv:2409.04701](https://arxiv.org/pdf/2409.04701)

- **Late Chunking: Balancing Precision and Cost in Long Context Retrieval** — Weaviate. Practical analysis of when late chunking is worth the compute cost.
  - [Weaviate Blog](https://weaviate.io/blog/late-chunking)

- **An Overview of Late Interaction Retrieval Models: ColBERT, ColPali, and ColQwen** — Weaviate. Multi-vector token-level embeddings for more precise passage retrieval.
  - [Weaviate Blog](https://weaviate.io/blog/late-interaction-overview)

- **Late Chunking vs Contextual Retrieval: The Math Behind RAG's Context Problem** — KX Systems. Mathematical comparison of approaches.
  - [Medium / KX](https://medium.com/kx-systems/late-chunking-vs-contextual-retrieval-the-math-behind-rags-context-problem-d5a26b9bbd38)

- **Supercharge RAG with Contextualized Late Interactions** — AI Forum.
  - [Medium](https://medium.com/the-ai-forum/supercharge-rag-with-contextualized-late-interactions-802a0f4a1e9d)

- **Late Chunking: Embedding First Chunk Later — Long-Context Retrieval in RAG Applications** — Medium.
  - [Medium](https://medium.com/@bavalpreetsinghh/late-chunking-embedding-first-chunk-later-long-context-retrieval-in-rag-applications-3a292f6443bb)

- **Milvus and Late Chunking: Context-Aware Embedding in RAG** — Dev.to.
  - [Dev.to](https://dev.to/e_b680bbca20c348/milvus-and-late-chunking-what-i-learned-about-context-aware-embedding-in-rag-4cbl)

---

## Propositional Chunking

- **Proposition-Based Chunking Notebook** — Nir Diamant (RAG Techniques repo). Extracts atomic fact-level statements from paragraphs; groups propositions by topic coherence or token budget.
  - [GitHub](https://github.com/NirDiamant/RAG_Techniques/blob/main/all_rag_techniques/proposition_chunking.ipynb)

- **Five Levels of Chunking Strategies in RAG** — Medium. Propositional chunking = Level 4 (Level 5 = agent-driven adaptive). Note: "Proposition-based chunking achieved worse results than other methods" in long prose tests due to high cost and fragmentation.
  - [Medium](https://medium.com/@anuragmishra_27746/five-levels-of-chunking-strategies-in-rag-notes-from-gregs-video-7b735895694d)

- **ChunkRAG: A Novel LLM-Chunk Filtering Method for RAG Systems** (2024). Post-retrieval chunk filtering using LLM relevance scoring; complementary to propositional approaches.
  - [arXiv:2410.19572](https://arxiv.org/pdf/2410.19572)

---

## Metadata Enrichment

- **Metadata-Driven Retrieval-Augmented Generation for Financial Question Answering** (2025). Demonstrates metadata-filtered retrieval with self-query retrievers; applicable to scientific domain with DOI/journal/section filters.
  - [arXiv:2510.24402](https://arxiv.org/html/2510.24402v1)

- **Enhancing RAG Performance with Metadata: The Power of Self-Query Retrievers** — Medium. Practical implementation guide.
  - [Medium](https://medium.com/@lorevanoudenhove/enhancing-rag-performance-with-metadata-the-power-of-self-query-retrievers-e29d4eecdb73)

- **Utilizing Metadata for Better Retrieval-Augmented Generation** (2025).
  - [arXiv:2601.11863](https://arxiv.org/html/2601.11863v1)

- **Develop a RAG Solution – Chunk Enrichment Phase** — Azure Architecture Center. Documents 15-25% precision improvement from metadata filtering. Covers entity extraction, classification, and summarization as enrichment steps.
  - [Microsoft Azure](https://learn.microsoft.com/en-us/azure/architecture/ai-ml/guide/rag/rag-enrichment-phase)

- **Beyond Fixed Chunks: How Semantic Chunking and Metadata Enrichment Transform RAG Accuracy** — Medium.
  - [Medium](https://medium.com/@shaikmohdhuz/beyond-fixed-chunks-how-semantic-chunking-and-metadata-enrichment-transform-rag-accuracy-07136e8cf562)

- **Advanced RAG: Automated Structured Metadata Enrichment** — Haystack Cookbook. End-to-end implementation of LLM-based metadata extraction at ingestion.
  - [Haystack](https://haystack.deepset.ai/cookbook/metadata_enrichment)

- **A Systematic Framework for Enterprise Knowledge Retrieval: Leveraging LLM-Generated Metadata to Enhance RAG Systems** (2024).
  - [arXiv:2512.05411](https://arxiv.org/html/2512.05411v1)

- **Advanced RAG Techniques: Data Processing & Ingestion** — Elasticsearch Labs.
  - [Elastic Blog](https://www.elastic.co/search-labs/blog/advanced-rag-techniques-part-1)

---

## Multimodal RAG (Figures, Tables, Equations)

- **Vision-Guided Chunking Is All You Need: Enhancing RAG with Multimodal Document Understanding** (2025). Uses Large Multimodal Models (LMMs) to understand figures and visual content during chunking; generates descriptive summaries for figure chunks.
  - [arXiv:2506.16035](https://arxiv.org/pdf/2506.16035)
  - [HuggingFace Paper Page](https://huggingface.co/papers/2506.16035)

- **MHier-RAG: Multi-Modal RAG for Visual-Rich Document Question-Answering** (2025). Hierarchical multimodal approach combining text, figure, and table understanding.
  - [arXiv:2508.00579](https://arxiv.org/pdf/2508.00579)

- **Building a Multimodal RAG That Responds with Text, Images, and Tables from Sources** — Towards Data Science.
  - [TDS](https://towardsdatascience.com/building-a-multimodal-rag-with-text-images-tables-from-sources-in-response/)

- **Multimodal Semantic RAG** — Ahmed Al-93 (GitHub). Reference implementation.
  - [GitHub](https://github.com/AhmedAl93/multimodal-semantic-RAG)

---

## RAG Surveys

- **Retrieval-Augmented Generation for Large Language Models: A Survey** — Gao et al. (2023). Foundational survey covering naive, advanced, and modular RAG.
  - [arXiv:2312.10997](https://arxiv.org/abs/2312.10997)

- **A Comprehensive Survey of Retrieval-Augmented Generation (RAG)** (2024). Extended coverage of recent advances including multimodal and agentic RAG.
  - [arXiv:2410.12837](https://arxiv.org/abs/2410.12837)

- **A Systematic Review of Key Retrieval-Augmented Generation (RAG) Systems** (2025).
  - [arXiv:2507.18910](https://arxiv.org/html/2507.18910v1)

- **Retrieval-Augmented Generation (RAG) in Healthcare: A Comprehensive Review** (2025). MDPI AI. Domain-specific lessons applicable to scientific publishing context.
  - [MDPI](https://www.mdpi.com/2673-2688/6/9/226)

- **Retrieval-Augmented Generation** — Springer Business & Information Systems (2025). Academic overview.
  - [Springer](https://link.springer.com/article/10.1007/s12599-025-00945-3)

- **Building a Retrieval-Augmented Generation (RAG) System for Academic Papers** — Graahand (2024). Practical walkthrough for academic paper RAG pipeline.
  - [Medium](https://graahand.medium.com/building-a-retrieval-augmented-generation-rag-system-for-academic-papers-an-in-depth-research-b8c34963b7d9)

---

## Hybrid Search & Graph-Augmented Retrieval

- **Graph-Augmented Hybrid Retrieval and Multi-Stage Re-ranking** — Dev.to. Framework combining BM25 + dense semantic + graph relationships for high-fidelity chunk retrieval.
  - [Dev.to](https://dev.to/lucash_ribeiro_dev/graph-augmented-hybrid-retrieval-and-multi-stage-re-ranking-a-framework-for-high-fidelity-chunk-retrieval-in-rag-systems-50ca)

- **Research on the Construction and Application of RAG Model Based on Knowledge Graph** (2025). Nature / Scientific Reports. Citation graph integration with RAG retrieval.
  - [Nature](https://www.nature.com/articles/s41598-025-21222-z)

- **An Advanced Retrieval-Augmented Generation System for Manufacturing Quality Control** (2024). ScienceDirect. Hybrid BM25 + embedding retrieval with metadata filtering — cross-domain reference for scientific publishing.
  - [ScienceDirect](https://www.sciencedirect.com/science/article/pii/S147403462400658X)

- **Key Strategies for Smart Retrieval Augmented Generation (RAG)** — Zilliz.
  - [Zilliz Blog](https://zilliz.com/blog/exploring-rag-chunking-llms-and-evaluations)

---

## Additional Practitioner Resources

- **The Ultimate Guide to Chunking Strategies for RAG Applications with Databricks** — Databricks Community Blog.
  - [Databricks Community](https://community.databricks.com/t5/technical-blog/the-ultimate-guide-to-chunking-strategies-for-rag-applications/ba-p/113089)

- **A Visual Exploration of Semantic Text Chunking** — Towards Data Science.
  - [TDS](https://towardsdatascience.com/a-visual-exploration-of-semantic-text-chunking-6bb46f728e30/)

- **9 Chunking Strategies to Improve RAG Performance** — NB Data.
  - [NB Data](https://www.nb.data.com/p/9-chunking-strategis-to-improve-rag)

- **7 Chunking Strategies for RAG Systems** — F22 Labs.
  - [F22 Labs](https://www.f22labs.com/blogs/7-chunking-strategies-in-rag-you-need-to-know/)

- **Chunking Methods in RAG: Comparison** — Bitpeak.
  - [Bitpeak](https://bitpeak.com/chunking-methods-in-rag-methods-comparison/)

- **Advanced RAG Techniques** — addaxis.ai.
  - [Addaxis](https://addaxis.ai/advanced-chunking-strategies-for-rag/)
