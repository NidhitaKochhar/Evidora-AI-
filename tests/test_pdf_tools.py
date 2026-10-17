import pytest
from evidora.pdf_tools import parse_pdf

def test_rejects_non_pdf():
    with pytest.raises(ValueError):
        parse_pdf(b"not pdf", "sample.pdf")
