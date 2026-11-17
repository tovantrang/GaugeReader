import argparse
import json
from pathlib import Path

from src.app import App
from src.display import Display


ROOT = Path(__file__).resolve().parent
EXAMPLE_CONFIGS = {
    "training": ROOT / "configs/examples/training_gauge.json",
    "second": ROOT / "configs/examples/second_gauge.json",
}


def main():
    parser = argparse.ArgumentParser(description="Explore a gauge-reading CV pipeline.")
    parser.add_argument("--example", choices=EXAMPLE_CONFIGS, default="training")
    parser.add_argument(
        "--image", help="Use a different image instead of the selected example"
    )
    args = parser.parse_args()

    config_path = EXAMPLE_CONFIGS[args.example]
    with config_path.open(encoding="utf-8") as file:
        config = json.load(file)
    if args.image:
        config["image_path"] = args.image
    app = App(config, config_path="config.json")
    Display(app)


if __name__ == "__main__":
    main()
