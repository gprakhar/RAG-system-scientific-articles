# Docling Chart Extraction - Explained

> **Quick Answer**: `do_chart_extraction=True` enables Docling to extract the underlying **data tables** from bar charts, pie charts, and line charts, converting visual chart information into structured CSV/tabular format.

---

## What Does `do_chart_extraction` Do?

When you enable `pipeline_options.do_chart_extraction = True`, Docling:

1. **Detects charts** in your PDF (as part of picture detection)
2. **Classifies** them as bar chart, pie chart, or line chart
3. **Extracts the underlying data** from the chart visualization
4. **Converts** the visual chart into structured tabular data (CSV format)

### This is NOT just OCR
Docling doesn't just read the text labels on a chart. It **reconstructs the data** behind the chart by understanding:
- The visual structure (bars, pie slices, line points)
- Axis values and scales
- Data point relationships
- Legend mappings

---

## Supported Chart Types

Docling currently supports **3 chart types**:

| Chart Type | Supported | Example Use Case |
|------------|-----------|------------------|
| **Bar Chart** | ✅ Yes | Comparing categories, frequency distributions |
| **Pie Chart** | ✅ Yes | Showing proportions/percentages |
| **Line Chart** | ✅ Yes | Time series, trends over time |
| Scatter Plot | ❌ No | (Not currently supported) |
| Box Plot | ❌ No | (Not currently supported) |
| Heatmap | ❌ No | (Not currently supported) |

---

## How Docling Defines "Charts"

In Docling's classification system, charts are a subset of detected **pictures**. When you enable chart extraction:

1. All pictures in the PDF are detected
2. Pictures are classified into categories like:
   - `chart` (bar, pie, line)
   - `diagram`
   - `figure`
   - `photo`
3. Only items classified as **charts** (bar/pie/line) undergo data extraction

---

## Technical Implementation

### Powered by Granite Vision Model

Chart extraction uses IBM's **Granite Vision** model with specialized capabilities:
- `chart2csv` - Converts charts to CSV tabular data
- `chart2code` - Can generate code to recreate the chart
- Vision-based understanding of chart structure

### What Gets Extracted

From each detected chart, Docling extracts:

✅ **Chart metadata**:
- Chart type (bar/pie/line)
- Dimensions (rows × columns)

✅ **Data table**:
- Header row(s)
- Data rows
- Cell-by-cell text content
- Values and labels

✅ **Output format**: CSV or DataFrame structure

---

## Code Example

### Basic Setup

```python
from docling.datamodel.pipeline_options import PdfPipelineOptions
from docling.document_converter import DocumentConverter, PdfFormatOption
from docling.datamodel.base_models import InputFormat

# Enable chart extraction
pipeline_options = PdfPipelineOptions()
pipeline_options.do_chart_extraction = True
pipeline_options.generate_page_images = True      # Recommended
pipeline_options.generate_picture_images = True   # Recommended

converter = DocumentConverter(
    format_options={
        InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)
    }
)

result = converter.convert(str(pdf_file))
```

### Extracting Chart Data

```python
import pandas as pd

# Iterate through document items
for item in result.document.iterate_items():
    # Check if item is a picture
    if hasattr(item, 'prov') and item.prov:
        for prov_item in item.prov:
            # Check if classified as a chart
            if hasattr(prov_item, 'classification'):
                classification = prov_item.classification

                # If chart extraction succeeded
                if hasattr(prov_item, 'chart_data') and prov_item.chart_data:
                    chart_data = prov_item.chart_data

                    print(f"Chart Type: {classification}")
                    print(f"Dimensions: {chart_data.num_rows} rows × {chart_data.num_cols} cols")

                    # Build DataFrame from extracted cells
                    data = []
                    for cell in chart_data.table_cells:
                        data.append({
                            'row': cell.row_span[0],
                            'col': cell.col_span[0],
                            'text': cell.text
                        })

                    df = pd.DataFrame(data)
                    print(df.to_csv(index=False))
```

---

## Installation Requirements

Chart extraction requires additional dependencies:

```bash
# Install docling with granite_vision support
uv add "docling[granite_vision]"

# Also need pandas for data manipulation
uv add pandas
```

---

## When to Use Chart Extraction for Scientific Papers

### ✅ **Recommended for**:
- Papers with **data-heavy bar charts** (e.g., experimental results, comparisons)
- **Time series line charts** (e.g., growth curves, kinetics)
- **Proportion pie charts** (e.g., demographic breakdowns)
- Documents where you need to **index chart data** for retrieval
- RAG systems where users might query "What were the values in Figure 3?"

### ❌ **NOT recommended for**:
- Complex scientific plots (scatter plots, box plots, heatmaps) - not supported
- Charts with overlapping elements or 3D visualizations
- Very low-resolution or scanned charts (OCR quality issues)
- Performance-critical pipelines (adds significant processing time)

---

## Performance Considerations

⚠️ **Chart extraction is computationally expensive**:

- Requires Vision Language Model inference (Granite Vision)
- Adds significant processing time per page
- Requires more memory/GPU resources

**Recommendation for your RAG pipeline**:
- Enable only if you need to **retrieve data from charts**
- Consider disabling for initial testing/prototyping
- Use selectively based on document type

---

## Output Example

### Input: Bar Chart in PDF
```
[Visual bar chart showing:]
Category A: 45
Category B: 30
Category C: 25
```

### Extracted Output (CSV):
```csv
Category,Value
Category A,45
Category B,30
Category C,25
```

---

## Comparison: Chart Extraction vs. Image Description

| Feature | Chart Extraction | Picture Description (VLM) |
|---------|-----------------|---------------------------|
| **Output** | Structured CSV data | Natural language text |
| **Chart Types** | Bar, Pie, Line only | Any image type |
| **Use Case** | Data retrieval, analysis | General understanding |
| **Precision** | High (exact values) | Lower (approximate) |
| **Cost** | Higher (specialized model) | Medium (general VLM) |
| **Enable with** | `do_chart_extraction=True` | `do_picture_description=True` |

**You can enable both** for complementary benefits:
- Chart extraction → precise data
- Picture description → context and interpretation

---

## Recommendation for Your RAG System

Based on your scientific paper use case:

### Option 1: Enable Chart Extraction (Recommended if data queries are important)
```python
pipeline_options = PdfPipelineOptions(
    do_chart_extraction=True,
    do_table_structure=True,
    do_formula_enrichment=True,
    generate_picture_images=True,
)
```

**Pros**:
- Can answer "What are the exact values in Figure 2?"
- Structured data for analysis
- Better for quantitative research papers

**Cons**:
- Slower processing
- Only works for bar/pie/line charts
- Requires granite_vision dependency

### Option 2: Disable for Speed (Use if not needed)
```python
pipeline_options = PdfPipelineOptions(
    do_chart_extraction=False,  # Default
    do_picture_description=True,  # Get general descriptions instead
    do_table_structure=True,
    do_formula_enrichment=True,
)
```

**Pros**:
- Faster processing
- Lower resource requirements
- Still get visual context via descriptions

**Cons**:
- No precise data extraction from charts
- Can't query specific data points

---

## Related Configuration Options

These options work together with chart extraction:

```python
pipeline_options = PdfPipelineOptions(
    # Chart extraction
    do_chart_extraction=True,

    # Automatically enabled by do_chart_extraction
    do_picture_classification=True,  # Classifies as bar/pie/line

    # Recommended complementary options
    generate_picture_images=True,     # Save chart images
    generate_page_images=True,        # Page context

    # Alternative: General image understanding
    do_picture_description=True,      # VLM descriptions of all images
)
```

---

## Sources

- [Chart Extraction Example - Docling GitHub](https://github.com/docling-project/docling/blob/main/docs/examples/chart_extraction.py)
- [Hot off the news: Docling Chart Extraction - Medium](https://alain-airom.medium.com/hot-off-the-news-docling-chart-extraction-is-out-finally-an-easy-way-to-rag-your-charts-33fbc984ae25)
- [Docling Chart Extraction - DEV Community](https://dev.to/aairom/hot-off-the-news-docling-chart-extraction-is-out-finally-an-easy-way-to-rag-your-charts-13o3)
- [Information extraction - Docling](https://docling-project.github.io/docling/examples/extraction/)
- [Docling Official Documentation](https://www.docling.ai/)

---

**Document Created**: 2026-04-11
**Related Files**:
- [docling_pipeline_options_cookbook.md](docling_pipeline_options_cookbook.md) - Full configuration guide
- [pdf_parsing_observations.md](pdf_parsing_observations.md) - Testing observations
- [pdf_reader.py](../src/pdf_reader.py) - Implementation
