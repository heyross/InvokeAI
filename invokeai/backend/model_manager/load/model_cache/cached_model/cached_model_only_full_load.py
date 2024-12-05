from typing import Any

import torch


class CachedModelOnlyFullLoad:
    """A wrapper around a PyTorch model to handle full loads and unloads between the CPU and the compute device.

    Note: "VRAM" is used throughout this class to refer to the memory on the compute device. It could be CUDA memory,
    MPS memory, etc.
    """

    def __init__(self, model: torch.nn.Module | Any, compute_device: torch.device, total_bytes: int):
        """Initialize a CachedModelOnlyFullLoad.

        Args:
            model (torch.nn.Module | Any): The model to wrap. Should be on the CPU.
            compute_device (torch.device): The compute device to move the model to.
            total_bytes (int): The total size (in bytes) of all the weights in the model.
        """
        # model is often a torch.nn.Module, but could be any model type. Throughout this class, we handle both cases.
        self._model = model
        self._compute_device = compute_device
        self._total_bytes = total_bytes
        self._is_in_vram = False

    @property
    def model(self) -> torch.nn.Module:
        return self._model

    def total_bytes(self) -> int:
        """Get the total size (in bytes) of all the weights in the model."""
        return self._total_bytes

    def is_in_vram(self) -> bool:
        """Return true if the model is currently in VRAM."""
        return self._is_in_vram

    def full_load_to_vram(self) -> int:
        """Load all weights into VRAM (if supported by the model).

        Returns:
            The number of bytes loaded into VRAM.
        """
        if self._is_in_vram:
            # Already in VRAM.
            return 0

        if not hasattr(self._model, "to"):
            # Model doesn't support moving to a device.
            return 0

        self._model.to(self._compute_device)
        self._is_in_vram = True
        return self._total_bytes

    def full_unload_from_vram(self) -> int:
        """Unload all weights from VRAM.

        Returns:
            The number of bytes unloaded from VRAM.
        """
        if not self._is_in_vram:
            # Already in RAM.
            return 0

        self._model.to("cpu")
        self._is_in_vram = False
        return self._total_bytes
