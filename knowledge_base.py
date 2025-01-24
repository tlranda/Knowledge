import argparse
import configparser
import json
import os
import pathlib
from typing import List, Tuple, Optional, Union

from knowledge_enum import DebugLevels
from knowledge_logger import KnowledgeLogger

class KnowledgeBase():
    def __init__(self,
                 arguments: argparse.Namespace,
                 logger: KnowledgeLogger,
                 ):
        self.logger = logger
        if not arguments.configuration[0].exists():
            self.logger.info(f"No default config @ {arguments.configuration[0]}; create default")
            self.make_default_configuration(arguments.configuration[0])
        self.configuration = configparser.ConfigParser(
                interpolation=configparser.ExtendedInterpolation(),
            )
        self.configuration.read(arguments.configuration)

        self.logger.debug(f"Loaded configuration from: {[str(_) for _ in arguments.configuration]}")
        for section in self.configuration:
            for key, value in self.configuration[section].items():
                self.logger.debug(f"{section}: {key} --> {value}")

        # Load components
        gk = pathlib.Path(self.configuration['knowledge.sources']['global'])
        if not gk.exists():
            with open(gk, 'w') as f:
                f.write('{}')
        with open(gk, 'r') as f:
            global_knowledge = json.load(f)
        class SampleWinner():
            def __str__(self):
                return "Oooh I won? Nice"
        #self.components = [SampleWinner(), 'sample string','who knows','who cares']
        if len(global_knowledge) > 0:
            self.components = [global_knowledge]
        else:
            self.components = []
        self.logger.info('KnowledgeBase initialized')

    def make_default_configuration(self,
                                   config_path: pathlib.Path,
                                   existing_config: Optional[configparser.ConfigParser] = None,
                                   ) -> None:
        if existing_config is None:
            existing_config = configparser.ConfigParser(
                interpolation=configparser.ExtendedInterpolation(),
            )
        existing_config['knowledge.sources'] = {
                    'global': pathlib.Path(os.environ['HOME']) /
                                ".pyknowledge" /
                                "information.json",
                }
        existing_config['knowledge.tools'] = {
                    'global': pathlib.Path(os.environ['HOME']) /
                                ".pyknowledge" /
                                "tools",
                }
        existing_config['knowledge.extensions'] = {}
        config_path.parents[0].mkdir(exist_ok=True, parents=True)
        with open(config_path, 'w') as configfile:
            existing_config.write(configfile)

    def __iter__(self):
        for knowledge in self.components:
            yield knowledge

    def __len__(self):
        return len(self.components)

    def __getitem__(self, arg):
        return self.configuration[arg]

