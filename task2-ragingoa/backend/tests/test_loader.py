import pytest

from app.data.loader import MSMARCOXILoader


def test_loader_rejects_invalid_split():
    with pytest.raises(ValueError):
        MSMARCOXILoader(split="test")


def test_loader_accepts_train():
    loader = MSMARCOXILoader(split="train")

    assert loader.split == "train"


def test_loader_accepts_validation():
    loader = MSMARCOXILoader(split="validation")

    assert loader.split == "validation"