"""
Unit tests for document chunking and text ingestion
"""
import os
import tempfile
from backend.blob_connector import parse_document_file

def test_plain_text_parsing():
    content = "VectraBank Policy Section 1.1: Customer wire transfers must be verified."
    with tempfile.NamedTemporaryFile("w+", suffix=".txt", delete=False, encoding="utf-8") as tf:
        tf.write(content)
        tf_name = tf.name
    try:
        parsed = parse_document_file(tf_name)
        assert content in parsed
    finally:
        if os.path.exists(tf_name):
            os.remove(tf_name)
