"""Tests for the core module."""
import pytest

from blueprint.core import Blueprint, create_blueprint


def test_blueprint_initialization():
    """Test Blueprint class initialization."""
    bp = Blueprint("test")
    assert bp.name == "test"


def test_blueprint_run():
    """Test Blueprint run method."""
    bp = Blueprint("test")
    assert bp.run() == "Running blueprint: test"


def test_create_blueprint():
    """Test create_blueprint factory function."""
    bp = create_blueprint("factory")
    assert isinstance(bp, Blueprint)
    assert bp.name == "factory" 