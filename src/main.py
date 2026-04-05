"""Entry point for the RAG ingestion pipeline.

Loads configuration from config.yaml and runs the PDF ingestion pipeline
using the configured parsing library.

Example:
    Run via uv::

        uv run rag --library pymupdf
        uv run rag --library docling
"""
import argparse
import logging
import yaml

from pdf_reader import read_pdf

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def _load_config(config_path: str = "config.yaml") -> dict:
    """Load YAML configuration from disk.

    Args:
        config_path: Path to the YAML config file.

    Returns:
        Parsed configuration as a dictionary.

    Raises:
        FileNotFoundError: If the config file does not exist.
        yaml.YAMLError: If the config file contains invalid YAML.
    """
    try:
        with open(config_path) as config_f:
            config = yaml.safe_load(config_f)
        logger.info("Loaded config from %s", config_path)
        return config
    except FileNotFoundError as e:
        logger.error("Config file not found at %s: %s", config_path, e)
        raise
    except yaml.YAMLError as e:
        logger.error("Failed to parse config file %s: %s", config_path, e)
        raise


def _parse_args() -> argparse.Namespace:
    """Parse command-line arguments.

    Returns:
        Parsed argument namespace.
    """
    parser = argparse.ArgumentParser(description="RAG PDF ingestion pipeline")
    parser.add_argument(
        "--library",
        type=str,
        default="pymupdf",
        help="PDF parsing library to use (default: pymupdf)",
    )
    return parser.parse_args()


def main() -> None:
    """Run the PDF ingestion pipeline.

    Loads config.yaml, parses CLI arguments, then reads all PDFs from the
    configured input directory and writes extracted text to the output directory.
    """
    args = _parse_args()
    config = _load_config()

    logger.info("Starting PDF ingestion pipeline with library=%s", args.library)
    read_pdf(
        file_path=config["pdf_files"]["file_path"],
        output_path=config["pdf_files"]["output_path"],
        library=args.library,
    )
    logger.info("PDF ingestion pipeline complete")


if __name__ == "__main__":
    main()
