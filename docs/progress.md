# Implementation Progress Log

Detailed record of work done per commit. Each entry uses the commit timestamp as its heading.

---

## 2026-04-05 14:11:23 +0530 — `eb4093b`
**Add pdf_reader: implement pluggable PDF parsing pipeline with pymupdf and docling**

### What was built

**`src/pdf_reader.py`** — Core PDF ingestion module using a dispatcher pattern:
- `_read_with_pymupdf`: extracts plain text page-by-page, writes `.txt` files with form-feed delimiters between pages
- `_read_with_docling`: uses Docling's `DocumentConverter` to extract structured content, writes `.md` files via `export_to_markdown()`
- `_LIBRARY_HANDLERS` dict maps library name strings to their handler functions — adding a new parser requires only a new private function + one dict entry
- `read_pdf()` public dispatcher: validates library, creates output dir, globs input PDFs, delegates to handler
- `DocumentConverter` is instantiated once outside the per-file loop (expensive to construct per file)
- Imports for each library are lazy (inside the private function) so only the chosen backend is loaded

**`src/main.py`** — Entry point refactored significantly:
- Added `argparse` with `--library` named CLI flag (defaults to `pymupdf`)
- Config loading extracted into `_load_config()` with specific exception handling (`FileNotFoundError`, `yaml.YAMLError`)
- Removed all dead commented-out code (genai client)
- Full logging replacing all `print()` calls
- Module and function docstrings added throughout

**`tests/test_pdf_reader.py`** — 6 tests covering:
- Invalid library raises `ValueError`
- Output directory auto-created when missing
- Correct number of `.txt` output files produced for pymupdf
- Output files are non-empty
- Empty input directory completes without error and produces no output
- Non-existent input directory raises `FileNotFoundError`

**`tests/test_main.py`** — 7 tests covering:
- Config loads and returns expected top-level keys (`gcp`, `pdf_files`)
- GCP section has `project_id`, `location`, `model`
- `pdf_files` section has `file_path`, `output_path`
- Missing config raises `FileNotFoundError`
- Malformed YAML raises `yaml.YAMLError`
- `main()` runs end-to-end without error
- `main()` accepts `--library` flag

### Package setup
- Added `[tool.uv] package = true` and `[tool.hatch.build.targets.wheel] packages = ["src"]` to `pyproject.toml`
- Entry point changed from `src.main:main` to `main:main` — hatchling adds `src/` to `sys.path`, so modules are imported without the `src.` prefix
- `uv pip install -e .` required for `uv run rag` to work
- Added `pytest` as a dev dependency

### Config changes
- Added `gcp.location`, `gcp.model` fields
- Added `pdf_files.output_path` field
- All active config sections uncommented and structured

### Other
- Sample PDFs renamed from long descriptive filenames to `doc1.pdf` – `doc6.pdf`
- `docs/output/` added to `.gitignore`
- `CLAUDE.md` updated with full development guidelines: git commit format, code style (named args, type hints, imports), documentation standards, logging & error handling rules, testing structure
- All 13 tests passing at commit time

### Verified
- `uv run rag --library pymupdf` — processed 6 PDFs successfully
- `uv run rag --library docling` — processed 6 PDFs successfully (~68s first run for model download, ~8–12s per doc after)
- `uv run pytest tests/ -v` — 13/13 passed
