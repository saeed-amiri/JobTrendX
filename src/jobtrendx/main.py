"""
The main entry point of the application.
To run:
python -m jobtrendx.main
or set a new dir containing emails:
PYTHONPATH=src python -m jobtrendx.main defaults.paths.emails="<NEW_DIR>"
"""
# pylint: disable=no-value-for-parameter

import typing

import hydra
import pandas as pd
from omegaconf import DictConfig

from . import logger
from . import email_processor
from . import analysis

if typing.TYPE_CHECKING:
    from pathlib import Path
    import email


LOG: logger.logging.Logger = logger.setup_logger('jobtrendx.log')


@hydra.main(config_path="conf", config_name="config", version_base=None)
def main(cfg: DictConfig) -> None:
    # pylint: disable=missing-function-docstring
    # pylint: disable=unused-argument
    src: str = cfg.defaults.paths.emails
    email_prc = email_processor.EmailProcessor(eml_dir=src, log=LOG)
    email_prc.execute()
    eml_dict: dict[Path, "email.message.EmailMessage"] = \
        email_prc.eml_dict
    anlaz = analysis.AnalysisEmails(eml_dict=eml_dict, cfg=cfg)
    anlaz.analyzing(log=LOG)
    df_info: pd.DataFrame = anlaz.df_info


if __name__ == "__main__":
    main()
