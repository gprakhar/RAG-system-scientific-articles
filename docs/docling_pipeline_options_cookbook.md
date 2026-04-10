# Docling Pipeline Options - Cookbook

> **Purpose**: Comprehensive guide to configuring Docling's `PdfPipelineOptions` for scientific PDF processing in the RAG pipeline.

---

## Table of Contents

- [Overview](#overview)
- [Basic Configuration](#basic-configuration)
- [OCR Configuration](#ocr-configuration)
- [Table Structure Extraction](#table-structure-extraction)
- [Layout Detection](#layout-detection)
- [Image & Visual Elements](#image--visual-elements)
- [Performance Tuning](#performance-tuning)
- [Enrichment Features](#enrichment-features)
- [Complete Examples](#complete-examples)
- [Reference](#reference)

---

## Overview

Docling provides extensive configuration through `PdfPipelineOptions` for customizing PDF parsing behavior. All options are pydantic-based for type-safe validation.

### Available Pipeline Types

- **PdfPipelineOptions** - PDF document processing (our focus)
- **VlmPipelineOptions** - Vision Language Model-based conversion
- **AsrPipelineOptions** - Automatic Speech Recognition
- **ConvertPipelineOptions** - Base configuration
- **PaginatedPipelineOptions** - Paginated formats

---

## Basic Configuration

### Minimal Setup

```python
from docling.document_converter import DocumentConverter
from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import PdfPipelineOptions
from docling.document_converter import PdfFormatOption

# Basic converter with default settings
pipeline_options = PdfPipelineOptions()

converter = DocumentConverter(
    format_options={
        InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)
    }
)

result = converter.convert(str(pdf_file))
markdown = result.document.export_to_markdown()
```

### Document Size Limits

```python
# Limit pages and file size
converter = DocumentConverter()
result = converter.convert(
    source=pdf_path,
    max_num_pages=100,
    max_file_size=20971520  # 20MB
)
```

### Page Range Selection

```python
# Process specific pages only
pipeline_options = PdfPipelineOptions(
    max_num_pages=10,
    page_range=[1, 5]  # Pages 1-5
)
```

---

## OCR Configuration

### Enable OCR for Scanned PDFs

```python
from docling.datamodel.pipeline_options import PdfPipelineOptions

pipeline_options = PdfPipelineOptions()
pipeline_options.do_ocr = True
pipeline_options.ocr_options.lang = ["en"]  # English OCR
```

### Multi-Language OCR

```python
# Support multiple languages
pipeline_options = PdfPipelineOptions()
pipeline_options.do_ocr = True
pipeline_options.ocr_options.lang = ["en", "es", "fr"]  # English, Spanish, French
```

### Available OCR Engines

```python
from docling.datamodel.pipeline_options import OcrEngine

# Available engines (enum):
# - OcrEngine.AUTO (automatic selection)
# - OcrEngine.EASYOCR
# - OcrEngine.OCRMAC
# - OcrEngine.RAPIDOCR
# - OcrEngine.TESSERACT
# - OcrEngine.TESSERACT_CLI

pipeline_options = PdfPipelineOptions()
pipeline_options.do_ocr = True
pipeline_options.ocr_engine = OcrEngine.TESSERACT
```

### OCR Performance Tuning

```python
pipeline_options = PdfPipelineOptions()
pipeline_options.do_ocr = True
pipeline_options.ocr_batch_size = 8  # Process 8 pages at once
```

---

## Table Structure Extraction

### Basic Table Extraction

```python
pipeline_options = PdfPipelineOptions(do_table_structure=True)

converter = DocumentConverter(
    format_options={
        InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)
    }
)
```

### Cell Matching Control

```python
pipeline_options = PdfPipelineOptions(do_table_structure=True)
pipeline_options.table_structure_options.do_cell_matching = False  # Faster, less accurate
```

### TableFormer Modes

```python
from docling.datamodel.pipeline_options import (
    PdfPipelineOptions,
    TableFormerMode,
    TableStructureOptions
)

# ACCURATE mode for scientific papers with complex tables
pipeline_options = PdfPipelineOptions(do_table_structure=True)
pipeline_options.table_structure_options = TableStructureOptions(
    mode=TableFormerMode.ACCURATE,  # or TableFormerMode.FAST
    do_cell_matching=True
)
```

---

## Layout Detection

### Layout Analysis Configuration

```python
from docling.datamodel.pipeline_options import PdfPipelineOptions

pipeline_options = PdfPipelineOptions()
pipeline_options.layout_batch_size = 8  # Process 8 pages at once

# Layout detection is enabled by default
```

### PDF Backend Selection

```python
from docling.datamodel.pipeline_options import PdfBackend

# Available backends:
# - PdfBackend.DLPARSE_V1
# - PdfBackend.DLPARSE_V2
# - PdfBackend.DOCLING_PARSE
# - PdfBackend.PYPDFIUM2

pipeline_options = PdfPipelineOptions()
pipeline_options.pdf_backend = PdfBackend.DOCLING_PARSE  # Default, recommended
```

---

## Image & Visual Elements

### Generate Page Images

```python
pipeline_options = PdfPipelineOptions(
    generate_page_images=True,
    images_scale=2.0  # Higher resolution (default is 1.0)
)
```

### Extract Pictures and Tables as Images

```python
pipeline_options = PdfPipelineOptions(
    generate_picture_images=True,
    generate_table_images=True,
    images_scale=2.0
)
```

### Image Classification

```python
# Classify images (requires VLM)
pipeline_options = PdfPipelineOptions()
pipeline_options.do_picture_classification = True
```

### Image Description with VLM

```python
# Generate descriptions for images using Vision Language Model
pipeline_options = PdfPipelineOptions()
pipeline_options.do_picture_description = True
```

---

## Performance Tuning

### Hardware Acceleration

```python
from docling.datamodel.accelerator_options import AcceleratorDevice, AcceleratorOptions

pipeline_options = PdfPipelineOptions()
pipeline_options.accelerator_options = AcceleratorOptions(
    num_threads=4,
    device=AcceleratorDevice.AUTO  # AUTO, CPU, CUDA, or MPS (Mac)
)
```

### Batch Size Configuration

```python
pipeline_options = PdfPipelineOptions(
    ocr_batch_size=8,         # OCR batching
    layout_batch_size=8       # Layout detection batching
)
```

### Timeout Settings

```python
pipeline_options = PdfPipelineOptions(
    document_timeout=120.0  # 2 minutes max per document
)
```

### Memory Management

```python
pipeline_options = PdfPipelineOptions(
    queue_max_size=1024  # Control internal queue size
)
```

### Parallel Processing

```python
pipeline_options = PdfPipelineOptions(
    enable_parallel_processing=True  # Process pages in parallel
)
```

### Disable Features for Speed

```python
# Minimal configuration for fast processing
pipeline_options = PdfPipelineOptions(
    generate_page_images=False,
    do_table_structure=False,
    do_code_enrichment=False,
    do_formula_enrichment=False
)
```

---

## Enrichment Features

### Formula/Equation Extraction

```python
pipeline_options = PdfPipelineOptions()
pipeline_options.do_formula_enrichment = True  # Extract LaTeX equations
```

### Code Block Detection

```python
pipeline_options = PdfPipelineOptions()
pipeline_options.do_code_enrichment = True  # Detect and extract code snippets
```

### Chart Extraction

```python
pipeline_options = PdfPipelineOptions()
pipeline_options.do_chart_extraction = True  # Extract and analyze charts
```

---

## Complete Examples

### Example 1: Scientific Paper Processing (Recommended for RAG)

```python
from docling.document_converter import DocumentConverter, PdfFormatOption
from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import (
    PdfPipelineOptions,
    TableStructureOptions,
    TableFormerMode,
)
from docling.datamodel.accelerator_options import AcceleratorDevice, AcceleratorOptions

# Optimized for scientific papers
pipeline_options = PdfPipelineOptions(
    # Core features
    do_table_structure=True,
    do_formula_enrichment=True,
    do_code_enrichment=True,

    # Images
    generate_picture_images=True,
    generate_page_images=False,  # Save memory
    images_scale=1.5,

    # Performance
    document_timeout=180.0,
    layout_batch_size=8,
    enable_parallel_processing=True,
)

# Accurate table extraction for scientific tables
pipeline_options.table_structure_options = TableStructureOptions(
    mode=TableFormerMode.ACCURATE,
    do_cell_matching=True
)

# Hardware acceleration
pipeline_options.accelerator_options = AcceleratorOptions(
    num_threads=4,
    device=AcceleratorDevice.AUTO
)

converter = DocumentConverter(
    format_options={
        InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)
    }
)

result = converter.convert(str(pdf_file))
markdown = result.document.export_to_markdown()
```

### Example 2: Scanned PDF with OCR

```python
pipeline_options = PdfPipelineOptions(
    # Enable OCR
    do_ocr=True,

    # Table extraction
    do_table_structure=True,

    # Performance
    ocr_batch_size=4,
    layout_batch_size=8,
    document_timeout=300.0  # Scanned PDFs take longer
)

# Multi-language support
pipeline_options.ocr_options.lang = ["en"]

# Accurate table mode
pipeline_options.table_structure_options = TableStructureOptions(
    mode=TableFormerMode.ACCURATE,
    do_cell_matching=True
)

converter = DocumentConverter(
    format_options={
        InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)
    }
)
```

### Example 3: Fast Processing (Speed over Accuracy)

```python
pipeline_options = PdfPipelineOptions(
    # Minimal features
    do_table_structure=True,
    generate_page_images=False,
    generate_picture_images=False,
    do_code_enrichment=False,
    do_formula_enrichment=False,

    # Fast table mode
    enable_parallel_processing=True,
)

# Fast table extraction
pipeline_options.table_structure_options = TableStructureOptions(
    mode=TableFormerMode.FAST,
    do_cell_matching=False
)

converter = DocumentConverter(
    format_options={
        InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)
    }
)
```

### Example 4: Offline Processing with Local Models

```python
# Use pre-downloaded models
artifacts_path = "/path/to/local/models"

pipeline_options = PdfPipelineOptions(
    artifacts_path=artifacts_path,
    enable_remote_services=False  # No internet required
)

converter = DocumentConverter(
    format_options={
        InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)
    }
)
```

### Example 5: Maximum Quality (All Features Enabled)

```python
pipeline_options = PdfPipelineOptions(
    # All enrichment features
    do_ocr=True,
    do_table_structure=True,
    do_code_enrichment=True,
    do_formula_enrichment=True,
    do_picture_description=True,
    do_picture_classification=True,
    do_chart_extraction=True,

    # High-quality images
    generate_page_images=True,
    generate_picture_images=True,
    generate_table_images=True,
    images_scale=2.0,

    # Accurate processing
    document_timeout=600.0,  # 10 minutes
)

pipeline_options.table_structure_options = TableStructureOptions(
    mode=TableFormerMode.ACCURATE,
    do_cell_matching=True
)

pipeline_options.ocr_options.lang = ["en"]

converter = DocumentConverter(
    format_options={
        InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)
    }
)
```

---

## Integration with Our RAG Pipeline

### Recommended Configuration for `src/pdf_reader.py`

```python
def _read_with_docling_advanced(pdf_files: list[Path], out_dir: Path) -> None:
    """Enhanced Docling extraction with scientific paper optimizations."""
    from docling.document_converter import DocumentConverter, PdfFormatOption
    from docling.datamodel.base_models import InputFormat
    from docling.datamodel.pipeline_options import (
        PdfPipelineOptions,
        TableStructureOptions,
        TableFormerMode,
    )

    # Scientific paper optimized settings
    pipeline_options = PdfPipelineOptions(
        do_table_structure=True,
        do_formula_enrichment=True,
        generate_picture_images=True,
        images_scale=1.5,
    )

    pipeline_options.table_structure_options = TableStructureOptions(
        mode=TableFormerMode.ACCURATE,
        do_cell_matching=True
    )

    converter = DocumentConverter(
        format_options={
            InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)
        }
    )

    for pdf_file in pdf_files:
        result = converter.convert(str(pdf_file))
        with open(out_dir / f"docling_adv_{pdf_file.stem}_output.md", "w") as out:
            out.write(result.document.export_to_markdown())
```

---

## Reference

### Key Options Summary

| Option | Type | Default | Purpose |
|--------|------|---------|---------|
| `do_ocr` | bool | False | Enable OCR for scanned PDFs |
| `do_table_structure` | bool | False | Extract table structure |
| `do_formula_enrichment` | bool | False | Extract LaTeX equations |
| `do_code_enrichment` | bool | False | Detect code blocks |
| `do_picture_description` | bool | False | Generate image descriptions (VLM) |
| `do_picture_classification` | bool | False | Classify images |
| `do_chart_extraction` | bool | False | Extract and analyze charts |
| `generate_page_images` | bool | False | Create page visualizations |
| `generate_picture_images` | bool | False | Extract detected images |
| `generate_table_images` | bool | False | Visualize tables |
| `images_scale` | float | 1.0 | Output image resolution |
| `document_timeout` | float | 600.0 | Max processing time (seconds) |
| `ocr_batch_size` | int | 4 | OCR batch size |
| `layout_batch_size` | int | 8 | Layout detection batch size |
| `enable_parallel_processing` | bool | False | Process pages in parallel |
| `enable_remote_services` | bool | False | Allow external API calls |

---

## Sources

- [Advanced options - Docling](https://docling-project.github.io/docling/usage/advanced_options/)
- [Pipeline options - Docling](https://docling-project.github.io/docling/reference/pipeline_options/)
- [Custom conversion - Docling](https://docling-project.github.io/docling/examples/custom_convert/)
- [Transform Any PDF into Searchable AI Data with Docling | CodeCut](https://codecut.ai/docling-pdf-rag-document-processing/)
- [Document Converter - Docling](https://docling-project.github.io/docling/reference/document_converter/)

---

**Document Created**: 2026-04-11
**Related Files**:
- [pdf_reader.py](../src/pdf_reader.py) - Implementation
- [pdf_parsing_observations.md](pdf_parsing_observations.md) - Testing observations
- [claude_code_plan.md](../claude_code_plan.md) - Architecture
