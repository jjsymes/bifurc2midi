from unittest.mock import MagicMock

import pytest

from bifurc2midi.adapters.midi_playback import (
    MidiOutputError,
    available_output_names,
    play,
    resolve_output_name,
)


def test_default_selects_the_first_output_even_if_a_later_device_is_named_default():
    assert resolve_output_name("default", ["IAC", "default"]) == "IAC"


def test_named_output_is_used_when_it_is_available():
    assert resolve_output_name("B", ["A", "B"]) == "B"


def test_missing_output_names_the_available_devices():
    with pytest.raises(MidiOutputError, match="Available outputs: A, B"):
        resolve_output_name("missing", ["A", "B"])


def test_no_devices_raises():
    with pytest.raises(MidiOutputError, match="No MIDI output devices found"):
        resolve_output_name("default", [])


def test_available_output_names_reads_mido(monkeypatch):
    monkeypatch.setattr(
        "bifurc2midi.adapters.midi_playback.get_output_names",
        lambda: ["A", "B"],
    )

    assert available_output_names() == ["A", "B"]


def test_play_sends_every_message_and_closes_the_port(monkeypatch):
    sent: list[str] = []
    closed = {"value": False}

    class Port:
        def send(self, message: str) -> None:
            sent.append(message)

        def close(self) -> None:
            closed["value"] = True

        def __enter__(self) -> "Port":
            return self

        def __exit__(self, *args: object) -> None:
            self.close()

    opened: dict[str, str] = {}

    def open_output(name: str) -> Port:
        opened["name"] = name
        return Port()

    monkeypatch.setattr(
        "bifurc2midi.adapters.midi_playback.open_output",
        open_output,
    )
    midi = MagicMock()
    midi.play.return_value = ["one", "two"]

    play(midi, "IAC")

    assert opened["name"] == "IAC"
    assert sent == ["one", "two"]
    assert closed["value"] is True
