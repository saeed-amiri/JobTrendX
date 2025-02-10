"""
The main entry point of the application.
"""
# pylint: disable=no-value-for-parameter

import hydra
from omegaconf import DictConfig

from . import email_processor
from . import logger


LOG: logger.logging.Logger = logger.setup_logger('jobtrendx.log')


@hydra.main(config_path="conf", config_name="config", version_base=None)
def main(cfg: DictConfig) -> None:
    # pylint: disable=missing-function-docstring
    # pylint: disable=unused-argument
    src: str = cfg.defaults.paths.emails
    email_processor.EmailProcessor(email_dir=src, log=LOG)


if __name__ == "__main__":
    main()
