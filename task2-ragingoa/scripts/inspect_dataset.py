from datasets import load_dataset


DATASET_NAME = "ai4bharat/MSMARCO-XI"
CONFIG_NAME = "default"


def main():
    print(f"Dataset: {DATASET_NAME}")
    print(f"Configuration: {CONFIG_NAME}")
    print()

    dataset = load_dataset(
        DATASET_NAME,
        CONFIG_NAME,
        streaming=True,
    )

    print("Dataset structure:")
    print(dataset)
    print()

    print("Available splits:")
    for split_name in dataset:
        print(f"  - {split_name}")

    print()

    train = dataset["train"]

    print("Inspecting first 3 training examples...")
    print()

    for index, example in enumerate(train.take(3)):
        print(f"========== Example {index + 1} ==========")

        for key, value in example.items():
            print(f"\n--- {key} ---")
            print(value)

        print()


if __name__ == "__main__":
    main()