"""RAG pipeline for peer-reviewed scientific articles.

This package implements a retrieval-augmented generation pipeline targeting
Elsevier/ScienceDirect scale document collections across diverse scientific domains.

Modules:
    pdf_reader: PDF ingestion using pluggable parsing backends (pymupdf, docling).
    main: Entry point — loads config and runs the ingestion pipeline.
"""
