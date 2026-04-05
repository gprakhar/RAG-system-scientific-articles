"""PDF ingestion module with pluggable parsing backends.

Supports multiple PDF parsing libraries via a dispatcher pattern. Adding a new
library requires only implementing a private `_read_with_<name>` function and
registering it in `_LIBRARY_HANDLERS`.

Modules:
    _read_with_pymupdf: PyMuPDF-based text extraction, output as .txt.
    _read_with_docling: Docling-based extraction, output as .md.
"""
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


def _read_with_pymupdf(pdf_files: list[Path], out_dir: Path) -> None:
    """Extract text from PDFs using PyMuPDF and write as .txt files.

    Args:
        pdf_files: List of PDF file paths to process.
        out_dir: Directory where output .txt files are written.

    Raises:
        FileNotFoundError: If a PDF file does not exist.
        OSError: If an output file cannot be written.
    """
    import pymupdf

    for pdf_file in pdf_files:
        logger.info("Processing %s with pymupdf", pdf_file.name)
        try:
            doc = pymupdf.open(pdf_file)
            with open(out_dir / f"{pdf_file.stem}_output.txt", "wb") as out:
                for page in doc:
                    text = page.get_text().encode("utf8")
                    out.write(text)
                    out.write(bytes((12,)))  # form feed page delimiter
            logger.info("Written output for %s", pdf_file.name)
        except FileNotFoundError as e:
            logger.error("PDF file not found %s: %s", pdf_file.name, e)
            raise
        except OSError as e:
            logger.error("I/O error processing %s: %s", pdf_file.name, e)
            raise


def _read_with_docling(pdf_files: list[Path], out_dir: Path) -> None:
    """Extract text from PDFs using Docling and write as .md files.

    Args:
        pdf_files: List of PDF file paths to process.
        out_dir: Directory where output .md files are written.

    Raises:
        FileNotFoundError: If a PDF file does not exist.
        OSError: If an output file cannot be written.
    """
    from docling.document_converter import DocumentConverter

    converter = DocumentConverter()
    for pdf_file in pdf_files:
        logger.info("Processing %s with docling", pdf_file.name)
        try:
            result = converter.convert(str(pdf_file))
            with open(out_dir / f"{pdf_file.stem}_output.md", "w", encoding="utf-8") as out:
                out.write(result.document.export_to_markdown())
            logger.info("Written output for %s", pdf_file.name)
        except FileNotFoundError as e:
            logger.error("PDF file not found %s: %s", pdf_file.name, e)
            raise
        except OSError as e:
            logger.error("I/O error processing %s: %s", pdf_file.name, e)
            raise


_LIBRARY_HANDLERS = {
    "pymupdf": _read_with_pymupdf,
    "docling": _read_with_docling,
}


def read_pdf(file_path: str, output_path: str, library: str = "pymupdf") -> None:
    """Read all PDFs in a directory and write extracted text to output files.

    Args:
        file_path: Path to directory containing input PDF files.
        output_path: Path to directory where output files are written.
        library: Parsing library to use. Supported: 'pymupdf', 'docling'.

    Raises:
        ValueError: If an unsupported library is specified.
    """
    if library not in _LIBRARY_HANDLERS:
        logger.error("Unsupported library requested: %r", library)
        raise ValueError(f"Unsupported library: {library!r}. Choose from: {list(_LIBRARY_HANDLERS)}")

    pdf_dir = Path(file_path)
    if not pdf_dir.exists():
        logger.error("Input directory does not exist: %s", pdf_dir)
        raise FileNotFoundError(f"Input directory not found: {pdf_dir}")

    out_dir = Path(output_path)
    out_dir.mkdir(parents=True, exist_ok=True)

    pdf_files = list(pdf_dir.glob("*.pdf"))
    logger.info("Found %d PDF files in %s", len(pdf_files), pdf_dir)

    _LIBRARY_HANDLERS[library](pdf_files=pdf_files, out_dir=out_dir)
