"""
The main entry point of the application.
"""
# pylint: disable=no-value-for-parameter
import hydra
from omegaconf import DictConfig


@hydra.main(config_path="conf", config_name="config", version_base=None)
def main(cfg: DictConfig) -> None:
    # pylint: disable=missing-function-docstring
    # pylint: disable=unused-argument
    print(hydra.compose("config"))


if __name__ == "__main__":
    main()
