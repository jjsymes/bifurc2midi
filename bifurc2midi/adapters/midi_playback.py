from collections.abc import Sequence

from mido import MidiFile, get_output_names, open_output


class MidiOutputError(Exception):
    """The requested MIDI output cannot be used."""


def available_output_names() -> list[str]:
    return list(get_output_names())


def resolve_output_name(requested: str, available: Sequence[str]) -> str:
    """Resolve ``default`` to the first output, or require an exact device name."""
    if not available:
        raise MidiOutputError("No MIDI output devices found")
    if requested == "default":
        return available[0]
    if requested not in available:
        names = ", ".join(available)
        raise MidiOutputError(
            f"MIDI output {requested!r} was not found. Available outputs: {names}"
        )
    return requested


def play(midi: MidiFile, output_name: str) -> None:
    with open_output(output_name) as port:
        for message in midi.play():
            port.send(message)
