# Copyright (c) 2023 Lincoln D. Stein and the InvokeAI Development Team
"""
Implementation of ModelConfigStore using a YAML file.

Typical usage:

  from invokeai.backend.model_management2.storage.yaml import ModelConfigStoreYAML
  store = ModelConfigStoreYAML("./configs/models.yaml")
  config = dict(
        path='/tmp/pokemon.bin',
        name='old name',
        base_model='sd-1',
        model_type='embedding',
        model_format='embedding_file',
        author='Anonymous',
     )

   # adding
   store.add_model('key1', config)

   # updating
   config.name='new name'
   store.update_model('key1', config)

   # checking for existence
   if store.exists('key1'):
      print("yes")

   # fetching config
   new_config = store.get_model('key1')
   print(new_config.name, new_config.base_model)

  # deleting
  store.del_model('key1')
"""

import threading
import yaml
from pathlib import Path
from typing import Union
from omegaconf import OmegaConf
from omegaconf.dictconfig import DictConfig

from ..model_config import (
    ModelConfigBase,
    ModelConfigFactory,
)

from .base import (
    DuplicateModelException,
    UnknownModelException,
    ModelConfigStore,
)

# should match the InvokeAI version when this is first released.
CONFIG_FILE_VERSION = "3.1.0"


class ModelConfigStoreYAML(ModelConfigStore):
    """Implementation of the ModelConfigStore ABC using a YAML file."""

    _filename: Path
    _config: DictConfig
    _lock: threading.Lock

    def __init__(self, config_file: Path):
        """Initialize ModelConfigStore object with a .yaml file."""
        super().__init__()
        self._filename = Path(config_file).absolute()  # don't let chdir mess us up!
        self._lock = threading.RLock()
        if not self._filename.exists():
            self._initialize_yaml()
        self._config = OmegaConf.load(self._filename)

    def _initialize_yaml(self):
        try:
            self._lock.acquire()
            self._filename.parent.mkdir(parents=True, exist_ok=True)
            with open(self._filename, "w") as yaml_file:
                yaml_file.write(yaml.dump({"__metadata__": {"version": CONFIG_FILE_VERSION}}))
        finally:
            self._lock.release()

    def _commit(self):
        try:
            self._lock.acquire()
            newfile = Path(str(self._filename) + ".new")
            yaml_str = OmegaConf.to_yaml(self._config)
            with open(newfile, "w", encoding="utf-8") as outfile:
                outfile.write(yaml_str)
            newfile.replace(self._filename)
        finally:
            self._lock.release()

    def add_model(self, key: str, config: Union[dict, ModelConfigBase]) -> None:
        """
        Add a model to the database.

        :param key: Unique key for the model
        :param config: Model configuration record, either a dict with the
         required fields or a ModelConfigBase instance.

        Can raise DuplicateModelException and InvalidModelConfig exceptions.
        """
        record = ModelConfigFactory.make_config(config)  # ensure it is a valid config obect
        dict_fields = record.dict()  # and back to a dict with valid fields
        try:
            self._lock.acquire()
            if key in self._config:
                raise DuplicateModelException(f"Duplicate key {key} for model named '{record.name}'")
            self._config[key] = dict_fields
            self._commit()
        finally:
            self._lock.release()

    def del_model(self, key: str) -> None:
        """
        Delete a model.

        :param key: Unique key for the model to be deleted

        Can raise an UnknownModelException
        """
        try:
            self._lock.acquire()
            if key not in self._config:
                raise UnknownModelException(f"Unknown key '{key}' for model config")
            self._config.pop(key)
            self._commit()
        finally:
            self._lock.release()

    def update_model(self, key: str, config: Union[dict, ModelConfigBase]) -> ModelConfigBase:
        """
        Update the model, returning the updated version.

        :param key: Unique key for the model to be updated
        :param config: Model configuration record. Either a dict with the
         required fields, or a ModelConfigBase instance.
        """
        record = ModelConfigFactory.make_config(config)  # ensure it is a valid config obect
        dict_fields = record.dict()  # and back to a dict with valid fields
        try:
            self._lock.acquire()
            if key not in self._config:
                raise UnknownModelException(f"Unknown key '{key}' for model config")
            self._config[key] = dict_fields
            self._commit()
        finally:
            self._lock.release()

    def get_model(self, key: str) -> ModelConfigBase:
        """
        Retrieve the ModelConfigBase instance for the indicated model.

        :param key: Key of model config to be fetched.

        Exceptions: UnknownModelException
        """
        try:
            record = self._config[key]
            return ModelConfigFactory.make_config(record)
        except KeyError as e:
            raise UnknownModelException(f"Unknown key '{key}' for model config") from e

    def exists(self, key: str) -> bool:
        """
        Return True if a model with the indicated key exists in the databse.

        :param key: Unique key for the model to be deleted
        """
        return key in self._config
