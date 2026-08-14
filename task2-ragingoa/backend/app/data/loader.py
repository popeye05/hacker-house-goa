from collections.abc import Iterator
from typing import Any

from datasets import load_dataset


DATASET_NAME = "ai4bharat/MSMARCO-XI"
CONFIG_NAME = "default"


class MSMARCOXILoader:
    """
    Streaming loader for the MSMARCO-XI dataset.

    The loader intentionally does not materialize the complete
    dataset in memory.
    """

    def __init__(
        self,
        split: str = "train",
    ) -> None:
        if split not in {"train", "validation"}:
            raise ValueError(
                "split must be 'train' or 'validation'"
            )

        self.split = split

    def iter_records(self) -> Iterator[dict[str, Any]]:
        """
        Lazily yield dataset records.
        """

        dataset = load_dataset(
            DATASET_NAME,
            CONFIG_NAME,
            split=self.split,
            streaming=True,
        )

        yield from dataset