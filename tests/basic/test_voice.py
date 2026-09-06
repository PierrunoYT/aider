import os
import queue
from pathlib import Path
from unittest.mock import MagicMock, patch

import numpy as np
import pytest

from patch.voice import SoundDeviceError, Voice


# Mock the entire sounddevice module
@pytest.fixture
def mock_sounddevice():
    mock_sd = MagicMock()
    mock_sd.query_devices.return_value = [
        {"name": "test_device", "max_input_channels": 2},
        {"name": "another_device", "max_input_channels": 1},
    ]
    with patch.dict("sys.modules", {"sounddevice": mock_sd}):
        yield mock_sd


@pytest.fixture
def mock_soundfile():
    with patch("patch.voice.sf") as mock_sf:
        yield mock_sf


def test_voice_init_default_device(mock_sounddevice):
    voice = Voice()
    assert voice.device_id is None
    assert voice.audio_format == "wav"
    assert voice.sd == mock_sounddevice


def test_voice_init_specific_device(mock_sounddevice):
    voice = Voice(device_name="test_device")
    assert voice.device_id == 0
    assert voice.sd == mock_sounddevice


def test_voice_init_invalid_device(mock_sounddevice):
    with pytest.raises(ValueError) as exc:
        Voice(device_name="nonexistent_device")
    assert "Device" in str(exc.value)
    assert "not found" in str(exc.value)


def test_voice_init_invalid_format():
    with patch("patch.voice.sf", MagicMock()):  # Need to mock sf to avoid SoundDeviceError
        with pytest.raises(ValueError) as exc:
            Voice(audio_format="invalid")
        assert "Unsupported audio format" in str(exc.value)


def test_callback_processing():
    with patch("patch.voice.sf", MagicMock()):  # Need to mock sf to avoid SoundDeviceError
        voice = Voice()
        voice.q = queue.Queue()

        # Test with silence (low amplitude)
        test_data = np.zeros((1000, 1))
        voice.callback(test_data, None, None, None)
        assert voice.pct == 0.5  # When range is too small (<=0.001), pct is set to 0.5

        # Test with loud signal (high amplitude)
        test_data = np.ones((1000, 1))
        voice.callback(test_data, None, None, None)
        assert voice.pct > 0.9

        # Verify data is queued
        assert not voice.q.empty()


def test_get_prompt():
    with patch("patch.voice.sf", MagicMock()):  # Need to mock sf to avoid SoundDeviceError
        voice = Voice()
        voice.start_time = os.times().elapsed
        voice.pct = 0.5  # 50% volume level

        prompt = voice.get_prompt()
        assert "Recording" in prompt
        assert "sec" in prompt
        assert "█" in prompt  # Should contain some filled blocks
        assert "░" in prompt  # Should contain some empty blocks


def test_record_and_transcribe_keyboard_interrupt():
    with patch("patch.voice.sf", MagicMock()):
        voice = Voice()
        with patch.object(voice, "raw_record_and_transcribe", side_effect=KeyboardInterrupt()):
            result = voice.record_and_transcribe()
            assert result is None


def test_record_and_transcribe_device_error():
    with patch("patch.voice.sf", MagicMock()):
        voice = Voice()
        with patch.object(
            voice, "raw_record_and_transcribe", side_effect=SoundDeviceError("Test error")
        ):
            result = voice.record_and_transcribe()
            assert result is None


def record_with(recording_dirs, **kwargs):
    """Run one recording, remembering the directory it used."""

    def remember(temp_dir, history, language):
        recording_dirs.append(temp_dir)
        Path(temp_dir, "recording.wav").write_bytes(b"audio")

        if "result" in kwargs:
            return kwargs["result"]

        raise kwargs["error"]

    with patch("patch.voice.sf", MagicMock()):
        voice = Voice()
        with patch.object(voice, "record_and_transcribe_in", side_effect=remember):
            return voice.raw_record_and_transcribe(None, None)


def test_the_recording_is_deleted_after_transcribing():
    dirs = []

    result = record_with(dirs, result="hello")

    assert result == "hello"
    assert dirs and not Path(dirs[0]).exists()


def test_the_recording_is_deleted_when_transcribing_fails():
    dirs = []

    with pytest.raises(RuntimeError):
        record_with(dirs, error=RuntimeError("transcription failed"))

    assert dirs and not Path(dirs[0]).exists()
