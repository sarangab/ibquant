import os
from pathlib import Path

import hydra

from ibtrader.callbacks.returns import ProfitAndLoss
from ibtrader.core import Contract, Strategy, Trader
from ibtrader.loggers.returns import ReturnsLogger

# SET PATHS
filepath = Path(__file__)
PROJECTPATH = os.getcwd()


@hydra.main(
    config_path=filepath.parent,
    config_name="agent",
    version_base=hydra.__version__,
)
def main(cfg):
    # SET LOGGER
    logspath = os.path.join(PROJECTPATH, "logs")
    logger = ReturnsLogger(logspath, name="returns")
    # SET EARLYSTOPPING CALLBACK
    pnlcallback = ProfitAndLoss(monitor="gain")
    # SET CALLBACKS
    callbacks = [pnlcallback]
    #  SET STRATEGY
    strategy = Strategy()
    #  SET MARKET CONTRACT
    contract = Contract(**cfg.contract)
    # SET TRADER
    trainer = Trader()
    # TRAIN MODEL
    trainer.fit(strategy=strategy, contract=contract, callbacks=callbacks, logger=logger)


if __name__ == "__main__":
    main()
