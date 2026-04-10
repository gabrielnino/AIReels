#!/usr/bin/env python3
"""Simple test to verify pytest works."""
import pytest

def test_simple():
    """Simple passing test."""
    assert 1 + 1 == 2

def test_another():
    """Another simple test."""
    assert "hello".upper() == "HELLO"

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
