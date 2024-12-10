from dataclasses import dataclass

from invokeai.backend.model_manager.load.model_cache.cached_model.cached_model_only_full_load import (
    CachedModelOnlyFullLoad,
)
from invokeai.backend.model_manager.load.model_cache.cached_model.cached_model_with_partial_load import (
    CachedModelWithPartialLoad,
)


@dataclass
class CacheRecord:
    """A class that represents a model in the model cache."""

    # Cache key.
    key: str
    # Model in memory.
    cached_model: CachedModelWithPartialLoad | CachedModelOnlyFullLoad
    # If locks > 0, the model is actively being used, so we should do our best to keep it on the compute device.
    _locks: int = 0

    def lock(self) -> None:
        self._locks += 1

    def unlock(self) -> None:
        self._locks -= 1
        assert self._locks >= 0

    @property
    def is_locked(self) -> bool:
        return self._locks > 0