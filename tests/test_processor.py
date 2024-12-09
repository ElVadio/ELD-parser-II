import pytest
from src.ml.document_processor import DocumentProcessor

def test_pdf_processing():
    processor = DocumentProcessor()
    result = processor.process_pdf('tests/data/sample.pdf')
    assert result is not None
    # Add more assertions