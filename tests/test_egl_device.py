import logging
import os
from typing import TYPE_CHECKING

from opengeodeweb_viewer import egl_device
from opengeodeweb_viewer.egl_device import (
    EGL_DEVICE_INDEX_ENV,
    SOFTWARE_FALLBACK_WARNING,
    EglDevice,
    choose_egl_device_index,
    select_egl_device,
)

if TYPE_CHECKING:
    import pytest

NOUVEAU = EglDevice(drm_file="/dev/dri/card2", driver="nouveau")
INTEL = EglDevice(drm_file="/dev/dri/card1", driver="i915")
NVIDIA = EglDevice(drm_file="/dev/dri/card0", driver="nvidia")
SOFTWARE = EglDevice(drm_file=None, driver=None)


def test_skips_nouveau_for_another_gpu() -> None:
    assert choose_egl_device_index([NOUVEAU, INTEL, SOFTWARE]) == 1


def test_keeps_first_device_without_nouveau() -> None:
    assert choose_egl_device_index([INTEL, NOUVEAU, SOFTWARE]) == 0
    assert choose_egl_device_index([NVIDIA, INTEL, SOFTWARE]) == 0


def test_falls_back_to_software_when_only_nouveau() -> None:
    assert choose_egl_device_index([NOUVEAU, SOFTWARE]) == 1


def test_no_choice_when_nothing_better() -> None:
    assert choose_egl_device_index([NOUVEAU]) is None
    assert choose_egl_device_index([]) is None


def test_select_respects_user_override(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv(EGL_DEVICE_INDEX_ENV, "2")
    select_egl_device(lambda: [NOUVEAU, INTEL])
    assert os.environ[EGL_DEVICE_INDEX_ENV] == "2"


def test_select_sets_index(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv(EGL_DEVICE_INDEX_ENV, raising=False)
    select_egl_device(lambda: [NOUVEAU, INTEL])
    assert os.environ[EGL_DEVICE_INDEX_ENV] == "1"


def test_select_ignores_enumeration_failure(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv(EGL_DEVICE_INDEX_ENV, raising=False)

    def failing() -> list[EglDevice]:
        msg = "libEGL.so.1: cannot open shared object file"
        raise OSError(msg)

    select_egl_device(failing)
    assert EGL_DEVICE_INDEX_ENV not in os.environ


def test_select_warns_on_software_fallback(
    monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
) -> None:
    monkeypatch.delenv(EGL_DEVICE_INDEX_ENV, raising=False)
    monkeypatch.setattr(egl_device, "rendering_warnings", [])
    with caplog.at_level(logging.WARNING, logger="opengeodeweb_viewer.egl_device"):
        select_egl_device(lambda: [NOUVEAU, SOFTWARE])
    assert os.environ[EGL_DEVICE_INDEX_ENV] == "1"
    assert "nouveau" in caplog.text
    assert egl_device.rendering_warnings == [SOFTWARE_FALLBACK_WARNING]


def test_select_does_not_warn_on_gpu(
    monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
) -> None:
    monkeypatch.delenv(EGL_DEVICE_INDEX_ENV, raising=False)
    monkeypatch.setattr(egl_device, "rendering_warnings", [])
    with caplog.at_level(logging.WARNING, logger="opengeodeweb_viewer.egl_device"):
        select_egl_device(lambda: [NOUVEAU, INTEL, SOFTWARE])
    assert not caplog.records
    assert egl_device.rendering_warnings == []
