# PDF Parsing Module Observations

> **About this document**: This is a living document tracking real-world observations, quirks, and performance notes about different PDF parsing libraries tested during the RAG system development. Updated as new findings emerge.

---

## Table of Contents

- [Overview](#overview)
- [Testing Methodology](#testing-methodology)
- [Library Performance](#library-performance)
  - [PyMuPDF (pymupdf)](#pymupdf-pymupdf)
  - [Docling](#docling)
  - [GROBID](#grobid)
  - [Nougat](#nougat)
- [Comparative Analysis](#comparative-analysis)
  - [Speed Benchmarks](#speed-benchmarks)
  - [Accuracy & Quality](#accuracy--quality)
  - [Edge Cases](#edge-cases)
- [Recommendations](#recommendations)
- [Raw Notes & Discoveries](#raw-notes--discoveries)

---

## Overview

**Purpose**: Document hands-on testing results for PDF parsing libraries being evaluated for the scientific article RAG pipeline.

**Test Corpus**: Sample peer-reviewed papers from `docs/example_input_docs/`

**Evaluation Criteria**:
- ✅ Text extraction accuracy
- ✅ Equation/formula preservation
- ✅ Table handling
- ✅ Figure caption extraction
- ✅ Reading order correctness
- ✅ Processing speed
- ✅ Setup complexity

---

## Testing Methodology

**Hardware**: MacBook (Apple Silicon / Intel)
**Sample Size**: [To be filled]
**Document Types**: [To be filled]

---

## Library Performance

### PyMuPDF (pymupdf)

**Version**: `1.27.2.2`
**Implementation Status**: ✅ Integrated
**Output Format**: Plain text (`.txt`)

#### Implementation Code

```python
import pymupdf
doc = pymupdf.open(pdf_file)
text = page.get_text().encode("utf8")
```

**Method**: `page.get_text()`

#### Observations

##### `get_text()` Method Behavior

**Document Structure Recognition**:
- ❌ The system is not able to differentiate between header, footer, text body, figures, tables, images.
- ✅ Reading order is preserved

**Visual Elements**:
- ❌ Images/plots/any visual element placeholder is not maintained
- ❌ Embedded hyperlinks are not being conserved in any form

#### Pros & Cons

**Pros**:
- ✅ Preserves reading order
- ✅ Fast processing
- ✅ Simple API

**Cons**:
- ❌ No semantic structure detection (headers, footers, body text)
- ❌ No visual element placeholders
- ❌ Hyperlinks lost
- ❌ No table/figure differentiation

---

### Docling

**Version**: `2.84.0`
**Implementation Status**: ✅ Integrated
**Output Format**: Markdown (`.md`)

#### Implementation Code

```python
from docling.document_converter import DocumentConverter
converter = DocumentConverter()
result = converter.convert(str(pdf_file))
markdown = result.document.export_to_markdown()
```

**Method**: `DocumentConverter().convert()`

#### Observations

##### `convert()` Method Behavior

**Document Structure Recognition**:
- ✅ Reading order preserved, almost
- ✅ Headings, subheading, section limits preserved.

**Visual Elements**:
- ⚠️ Visual elements placeholder maintained at times (doc_1, 5, 6), mostly not (doc 2, 3, 4)
- ❌ Embedded hyperlinks not conserved

#### Pros & Cons

**Pros**:
- ✅ Preserves document structure (headings, sections)
- ✅ Reading order mostly maintained
- ✅ Markdown output for better formatting
- ⚠️ Some visual element placeholders

**Cons**:
- ⚠️ Inconsistent visual element placeholder handling
- ❌ Hyperlinks lost

---

### PyMuPDF4LLM (pymupdf4llm)

**Version**: `1.27.2.2`
**Implementation Status**: ✅ Integrated
**Output Format**: Markdown (`.md`)

#### Implementation Code

```python
import pymupdf4llm
md_text = pymupdf4llm.to_markdown(str(pdf_file))
```

**Method**: `to_markdown()`

#### Observations

##### `to_markdown()` Method Behavior

**Document Structure Recognition**:
- ✅ Reading order is preserved
- ⚠️ Footer are not recognised as such and included into text body (doc 2, 6) or they are recognised (doc 1)
- ❌ Header are not recognised and included in text body
- ✅ Headings, subheading, section limits preserved.

**Visual Elements**:
- ⚠️ Visual elements placeholder maintained at times (doc 1, 5), mostly not (doc 2, 6)
- ❌ Embedded hyperlinks not conserved
- ❌ Special chars (Eg. mu, micro) are not recognised.

#### Pros & Cons

**Pros**:
- ✅ Reading order preserved
- ✅ Headings and section structure maintained
- ✅ LLM-optimized markdown output

**Cons**:
- ⚠️ Inconsistent header/footer detection
- ⚠️ Inconsistent visual element placeholders
- ❌ Headers not recognized, included in body
- ❌ Hyperlinks lost
- ❌ Special character encoding issues (Greek letters, symbols)

---

### GROBID

**Version**: [To be filled]
**Implementation Status**: ⏳ Planned
**Output Format**: TEI XML

#### Observations

*[Your observations will go here]*

---

### Nougat

**Version**: [To be filled]
**Implementation Status**: ⏳ Planned
**Output Format**: LaTeX/Markdown

#### Observations

*[Your observations will go here]*

---

## Comparative Analysis

### Speed Benchmarks

| Library | Pages/Second | Total Time (10 docs) | Notes |
|---------|--------------|----------------------|-------|
| PyMuPDF | [TBD] | [TBD] | |
| Docling | [TBD] | [TBD] | |
| GROBID | [TBD] | [TBD] | |
| Nougat | [TBD] | [TBD] | |

---

### Accuracy & Quality

#### Text Extraction

*[Comparative notes on text extraction quality across libraries]*

#### Equation Handling

*[How well each library preserves mathematical formulas]*

#### Table Extraction

*[Table detection and structure preservation]*

#### Figure Captions

*[Caption extraction accuracy]*

---

### Edge Cases

#### Multi-Column Layouts

*[Observations on reading order in multi-column papers]*

#### Scanned PDFs

*[OCR capabilities or limitations]*

#### Non-English Text

*[Unicode/multilingual support]*

---

## Recommendations

### Current Leading Choice

**Library**: [To be determined based on testing]

**Rationale**:
- [To be filled after testing]

### Fallback Strategy

*[Secondary choice if primary fails]*

---

## Raw Notes & Discoveries

*This section contains unedited observations, timestamps, and immediate reactions during testing. Preserved for authenticity.*

---

### [Date: TBD]

*[Your raw observations will go here as you discover them]*

---

### [Date: TBD]

*[Additional observations]*

---

## Document Metadata

**Created**: 2026-04-07
**Last Updated**: 2026-04-07
**Author**: User observations, structured by Claude
**Related Files**:
- [claude_code_plan.md](../claude_code_plan.md) - Architecture decisions
- [pdf_reader.py](../src/pdf_reader.py) - Implementation code
- [Example PDFs](example_input_docs/) - Test corpus
