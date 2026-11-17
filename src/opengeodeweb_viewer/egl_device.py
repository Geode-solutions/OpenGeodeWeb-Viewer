"""Choose which GPU VTK renders on when it uses an EGL render window.

VTK's EGL render window renders on the EGL device given by
VTK_DEFAULT_EGL_DEVICE_INDEX, and on device 0 when it is unset. On hybrid
laptops device 0 can be an NVIDIA GPU driven by nouveau, which renders meshes
with missing triangles, and the device order may change between boots.
"""

import ctypes
import logging
import os
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Callable

logger = logging.getLogger(__name__)

EGL_DEVICE_INDEX_ENV = "VTK_DEFAULT_EGL_DEVICE_INDEX"
_EGL_EXTENSIONS = 0x3055
_EGL_DRM_DEVICE_FILE_EXT = 0x3233
# Extension Mesa exposes on its software rendering device (llvmpipe)
_SOFTWARE_DEVICE_EXTENSION = "EGL_MESA_device_software"
_UNRELIABLE_DRIVERS = frozenset({"nouveau"})
SOFTWARE_FALLBACK_WARNING = (
    "The NVIDIA GPU driver (nouveau) draws meshes with missing triangles: "
    "the 3D view is rendered without the GPU, which is slower. "
    "Install the proprietary NVIDIA driver to render on the GPU."
)


@dataclass(frozen=True)
class EglDevice:
    drm_file: str | None
    driver: str | None
    is_software: bool = False


def _drm_driver(drm_file: str) -> str | None:
    driver_link = Path("/sys/class/drm", Path(drm_file).name, "device", "driver")
    if not driver_link.exists():
        return None
    return driver_link.resolve().name


def list_egl_devices() -> list[EglDevice]:
    """List EGL devices in the order VTK indexes them."""
    egl = ctypes.CDLL("libEGL.so.1")
    egl.eglGetProcAddress.restype = ctypes.c_void_p
    egl.eglGetProcAddress.argtypes = [ctypes.c_char_p]
    query_devices_address = egl.eglGetProcAddress(b"eglQueryDevicesEXT")
    query_string_address = egl.eglGetProcAddress(b"eglQueryDeviceStringEXT")
    if not query_devices_address or not query_string_address:
        return []
    query_devices = ctypes.CFUNCTYPE(
        ctypes.c_uint,
        ctypes.c_int,
        ctypes.POINTER(ctypes.c_void_p),
        ctypes.POINTER(ctypes.c_int),
    )(query_devices_address)
    query_string = ctypes.CFUNCTYPE(ctypes.c_char_p, ctypes.c_void_p, ctypes.c_int)(
        query_string_address
    )

    count = ctypes.c_int(0)
    if not query_devices(0, None, ctypes.byref(count)):
        return []
    handles = (ctypes.c_void_p * count.value)()
    if not query_devices(count.value, handles, ctypes.byref(count)):
        return []

    devices = []
    for handle in handles[: count.value]:
        raw_file = query_string(handle, _EGL_DRM_DEVICE_FILE_EXT)
        drm_file = raw_file.decode() if raw_file else None
        driver = _drm_driver(drm_file) if drm_file else None
        raw_extensions = query_string(handle, _EGL_EXTENSIONS)
        extensions = raw_extensions.decode().split() if raw_extensions else []
        devices.append(
            EglDevice(
                drm_file=drm_file,
                driver=driver,
                is_software=_SOFTWARE_DEVICE_EXTENSION in extensions,
            )
        )
    return devices


def choose_egl_device_index(devices: list[EglDevice]) -> int | None:
    """Index of the device to render on, or None to keep VTK's default.

    Prefers a GPU whose driver renders correctly, then software rendering.
    """
    reliable = [
        index for index, device in enumerate(devices) if device.driver not in _UNRELIABLE_DRIVERS
    ]
    hardware = [index for index in reliable if not devices[index].is_software]
    if hardware:
        return hardware[0]
    if reliable:
        return reliable[0]
    return None


def select_egl_device(
    list_devices: Callable[[], list[EglDevice]] = list_egl_devices,
) -> list[str]:
    """Set VTK's EGL device before the first render window is created.

    Returns the warnings about the rendering setup, to show to the user.
    """
    if not sys.platform.startswith("linux") or EGL_DEVICE_INDEX_ENV in os.environ:
        return []
    try:
        devices = list_devices()
    except (OSError, AttributeError) as error:
        logger.debug("EGL devices not enumerated: %s", error)
        return []
    index = choose_egl_device_index(devices)
    if index is None:
        return []
    os.environ[EGL_DEVICE_INDEX_ENV] = str(index)
    chosen = devices[index]
    if chosen.is_software and any(d.driver in _UNRELIABLE_DRIVERS for d in devices):
        logger.warning(SOFTWARE_FALLBACK_WARNING)
        return [SOFTWARE_FALLBACK_WARNING]
    logger.info("Rendering on EGL device %d (%s)", index, chosen.driver or "software")
    return []
