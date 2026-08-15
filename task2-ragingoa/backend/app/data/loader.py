
from collections.abc import Iterator
from typing import Any

import pyarrow.parquet as pq
from huggingface_hub import hf_hub_download


DATASET_REPO = "ai4bharat/MSMARCO-XI"


LANGUAGE_FILES = {
    "hi": {
        "train": "train/hintrain.parquet",
        "validation": "validation/hinval.parquet",
    },
    "bn": {
        "train": "train/bentrain.parquet",
        "validation": "validation/benval.parquet",
    },
    "ta": {
        "train": "train/tamtrain.parquet",
        "validation": "validation/tamval.parquet",
    },
    "te": {
        "train": "train/teltrain.parquet",
        "validation": "validation/telval.parquet",
    },
    "mr": {
        "train": "train/martrain.parquet",
        "validation": "validation/marval.parquet",
    },
    "gu": {
        "train": "train/gujtrain.parquet",
        "validation": "validation/gujval.parquet",
    },
    "kn": {
        "train": "train/kantrain.parquet",
        "validation": "validation/kanval.parquet",
    },
    "ml": {
        "train": "train/maltrain.parquet",
        "validation": "validation/malval.parquet",
    },
    "pa": {
        "train": "train/pantrain.parquet",
        "validation": "validation/panval.parquet",
    },
    "ne": {
        "train": "train/neptrain.parquet",
        "validation": "validation/nepval.parquet",
    },
    "or": {
        "train": "train/oritrain.parquet",
        "validation": "validation/orival.parquet",
    },
    "as": {
        "train": "train/asmtrain.parquet",
        "validation": "validation/asmval.parquet",
    },
    "ur": {
        "train": "train/urdtrain.parquet",
        "validation": "validation/urdval.parquet",
    },
    "sa": {
        "train": "train/santrain.parquet",
        "validation": "validation/sanval.parquet",
    },
}


class MSMARCOXILoader:
    """
    Reads one language/split of MSMARCO-XI from its Parquet file.

    The Parquet file is cached locally by Hugging Face Hub.
    Records are then read in small Arrow batches so we do not
    materialize the complete dataset in RAM.
    """

    def __init__(
        self,
        split: str = "validation",
        language: str = "hi",
        batch_size: int = 32,
    ) -> None:

        if split not in {"train", "validation"}:
            raise ValueError(
                "split must be 'train' or 'validation'"
            )

        if language not in LANGUAGE_FILES:
            raise ValueError(
                f"Unsupported language: {language}"
            )

        if batch_size <= 0:
            raise ValueError(
                "batch_size must be greater than 0"
            )

        self.split = split
        self.language = language
        self.batch_size = batch_size

    def _get_filename(self) -> str:
        return LANGUAGE_FILES[self.language][self.split]

    def iter_records(self) -> Iterator[dict[str, Any]]:
        """
        Yield records one at a time from bounded Arrow batches.
        """

        filename = self._get_filename()

        print(
            f"Downloading/caching MSMARCO-XI "
            f"{self.language}/{self.split}..."
        )

        local_path = hf_hub_download(
            repo_id=DATASET_REPO,
            filename=filename,
            repo_type="dataset",
        )

        print(f"Reading: {local_path}")

        parquet_file = pq.ParquetFile(local_path)

        for batch in parquet_file.iter_batches(
            batch_size=self.batch_size,
        ):
            for row in batch.to_pylist():
                yield row

