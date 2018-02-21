#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#
# Copyright © 2018 Dell Inc. or its subsidiaries. All rights reserved.
# Dell, EMC, and other trademarks are trademarks of Dell Inc. or its subsidiaries.
# Other trademarks may be trademarks of their respective owners.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# Authors: Karthik Prabhu
#
import os
import sys
import json
import yaml
import logging.config
import tempfile
from logging import StreamHandler, Formatter
from logging.handlers import TimedRotatingFileHandler
from enum import Enum

DEFAULT_LOGGER_CONFIG_FILE = os.path.join(os.path.dirname(__file__), "config", "logging.json")

DEFAULT_LOGGER_LOG_FILE = os.path.join(tempfile.gettempdir(), "omsdk-logs", "omsdk-logs.log")
DEFAULT_LOGGER_FORMAT = "%(asctime)s - %(levelname)-5s - %(name)s:%(lineno)d - %(message)s"
DEFAULT_LOGGER_LEVEL = logging.DEBUG

logger = logging.getLogger(__name__)


# Logger Configuration Types
class LoggerConfigTypeEnum(Enum):
    BASIC = 1  # Basic Configuration
    CONFIG_FILE = 2  # Configuration File based Configuration


class LoggerConfiguration:
    @staticmethod
    def __load_config(file_type, path):
        try:
            with open(path, 'rt') as f:
                if file_type == "json":
                    config = json.load(f)
                elif file_type == "yaml":
                    config = yaml.safe_load(f.read())
                logging.config.dictConfig(config)

        except IOError as e:
            logger.error("I/O error({0}): {1}".format(e.errno, e.strerror))

    def setup_logging(self, logger_config_type=LoggerConfigTypeEnum.BASIC,
                      logger_config_file=DEFAULT_LOGGER_CONFIG_FILE,
                      logger_log_file=DEFAULT_LOGGER_LOG_FILE,
                      logger_format=DEFAULT_LOGGER_FORMAT,
                      logger_level=DEFAULT_LOGGER_LEVEL):
        logger.info("Setting up Logging -- STARTED")

        # Basic Configuration
        if logger_config_type == LoggerConfigTypeEnum.BASIC:
            logger_log_directory = os.path.dirname(logger_log_file)

            # create log directory if doesn't exist
            if not os.path.exists(logger_log_directory):
                os.makedirs(logger_log_directory)

            # Configure basic logging
            root = logging.getLogger()
            root.setLevel(logger_level)

            # Create a Logging Formatter
            formatter = Formatter(logger_format)

            # set up logging to console
            console_handler = StreamHandler(sys.stdout)
            console_handler.setLevel(logger_level)
            console_handler.setFormatter(formatter)
            root.addHandler(console_handler)

            # set up logging to file
            file_handler = TimedRotatingFileHandler(logger_log_file, when='S', interval=10, backupCount=5,
                                                    encoding="utf8")
            file_handler.setLevel(logger_level)
            file_handler.setFormatter(formatter)
            root.addHandler(file_handler)

        # Logging from Configuration File
        elif logger_config_type == LoggerConfigTypeEnum.CONFIG_FILE:
            path = logger_config_file

            # Check if file exists
            if os.path.exists(path):
                file_type = path.split(os.sep)[-1].split(".")[-1].lower()

                # JSON-Based Configuration
                if file_type == "json":
                    self.__load_config(file_type, path)

                # CONF/INI-based Configuration
                elif file_type == "conf" or file_type == "ini":
                    logging.config.fileConfig(path)

                # YAML-based Configuration
                elif file_type == "yaml":
                    self.__load_config(file_type, path)

                # Unsupported Configuration
                else:
                    logger.error("Unsupported configuration")
            else:
                logger.error("No Logger Configuration Specified")
        else:
            logger.error("Invalid Logger Configuration.")
        logger.info("Setting up Logging -- FINISHED")


LogManager = LoggerConfiguration()
