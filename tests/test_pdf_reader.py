"""Tests for src/pdf_reader.py."""
import pytest
from pathlib import Path

from pdf_reader import read_pdf

SAMPLE_PDF_DIR = "docs/example_input_docs"


class TestReadPdf:
    """Tests for the read_pdf dispatcher."""

    def test_invalid_library_raises_value_error(self, tmp_path: Path) -> None:
        """read_pdf raises ValueError for an unsupported library name."""
        with pytest.raises(ValueError, match="Unsupported library"):
            read_pdf(
                file_path=SAMPLE_PDF_DIR,
                output_path=str(tmp_path),
                library="unsupported_lib",
            )

    def test_output_directory_created_if_missing(self, tmp_path: Path) -> None:
        """read_pdf creates the output directory if it does not exist."""
        out_dir = tmp_path / "nested" / "output"
        assert not out_dir.exists()
        read_pdf(
            file_path=SAMPLE_PDF_DIR,
            output_path=str(out_dir),
        )
        assert out_dir.exists()

    def test_pymupdf_produces_output_for_each_pdf(self, tmp_path: Path) -> None:
        """read_pdf with pymupdf writes a .txt file for every PDF in the input directory."""
        read_pdf(
            file_path=SAMPLE_PDF_DIR,
            output_path=str(tmp_path),
            library="pymupdf",
        )
        input_pdfs = list(Path(SAMPLE_PDF_DIR).glob("*.pdf"))
        output_txts = list(tmp_path.glob("*_output.txt"))
        assert len(output_txts) == len(input_pdfs)

    def test_pymupdf_output_files_are_non_empty(self, tmp_path: Path) -> None:
        """Output .txt files produced by pymupdf must contain text."""
        read_pdf(
            file_path=SAMPLE_PDF_DIR,
            output_path=str(tmp_path),
            library="pymupdf",
        )
        for txt_file in tmp_path.glob("*_output.txt"):
            assert txt_file.stat().st_size > 0, f"{txt_file.name} is empty"

    def test_empty_input_directory_produces_no_output(self, tmp_path: Path) -> None:
        """read_pdf on an empty directory completes without error and writes nothing."""
        empty_dir = tmp_path / "empty"
        empty_dir.mkdir()
        out_dir = tmp_path / "output"

        read_pdf(
            file_path=str(empty_dir),
            output_path=str(out_dir),
        )
        assert list(out_dir.glob("*")) == []

    def test_invalid_input_directory_raises_file_not_found(self, tmp_path: Path) -> None:
        """read_pdf raises FileNotFoundError when the input directory does not exist."""
        with pytest.raises(FileNotFoundError, match="Input directory not found"):
            read_pdf(
                file_path="/nonexistent/path",
                output_path=str(tmp_path),
            )
