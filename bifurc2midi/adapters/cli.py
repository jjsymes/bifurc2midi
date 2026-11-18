import importlib.metadata

import click

from bifurc2midi.adapters.midi_file import save, score_to_midi
from bifurc2midi.adapters.midi_playback import (
    MidiOutputError,
    available_output_names,
    play,
    resolve_output_name,
)
from bifurc2midi.adapters.plot import plot
from bifurc2midi.application.perform import Performance, PerformanceRequest, perform
from bifurc2midi.domain.diagram import InitialXBehaviour
from bifurc2midi.domain.music import NoteValue

_BEHAVIOURS = {behaviour.value: behaviour for behaviour in InitialXBehaviour}
_NOTE_VALUES = [note_value.name.lower() for note_value in NoteValue]


@click.version_option(package_name="bifurc2midi")
@click.command()
@click.option(
    "--r-start",
    type=float,
    default=2.9,
    show_default=True,
    help="Start of the r interval.",
)
@click.option(
    "--r-end",
    type=float,
    default=4,
    show_default=True,
    help="End of the r interval.",
)
@click.option(
    "--r-step-size",
    type=float,
    default=0.001,
    show_default=True,
    help="Distance between successive r values.",
)
@click.option(
    "--number-of-iterations-per-r-value",
    type=int,
    default=1000,
    show_default=True,
    help="Logistic-map iterations to run for each r value.",
)
@click.option(
    "--burn-in",
    type=int,
    default=990,
    show_default=True,
    help="Iterations to discard at the start of each r value.",
)
@click.option(
    "--x-initial-value-behaviour",
    type=click.Choice(list(_BEHAVIOURS), case_sensitive=False),
    default=InitialXBehaviour.STATIC.value,
    show_default=True,
    help="How each orbit chooses its starting x.",
)
@click.option("-o", "--out", type=str, default="out.mid", help="Output MIDI file.")
@click.option(
    "-p",
    "--plot-diagram",
    is_flag=True,
    help="Plot the logistic-map diagram.",
)
@click.option(
    "-d",
    "--midi-out-device",
    type=str,
    default=None,
    help="MIDI output device. Use 'default' for the first available device.",
)
@click.option(
    "--arpeggiate/--no-arpeggiate",
    default=True,
    show_default=True,
    help="Play each pitch in turn. Otherwise the pitches of an r value sound together.",
)
@click.option(
    "--pedal/--no-pedal",
    default=True,
    show_default=True,
    help="Hold the sustain pedal for the whole piece.",
)
@click.option("--bpm", type=int, default=120, show_default=True, help="Tempo.")
@click.option(
    "--note-value",
    type=click.Choice(_NOTE_VALUES, case_sensitive=False),
    default=NoteValue.SIXTEENTH.name.lower(),
    show_default=True,
    help="Duration of each sounding event.",
)
def cli(
    r_start: float,
    r_end: float,
    r_step_size: float,
    number_of_iterations_per_r_value: int,
    burn_in: int,
    x_initial_value_behaviour: str,
    out: str,
    plot_diagram: bool,
    midi_out_device: str | None,
    arpeggiate: bool,
    pedal: bool,
    bpm: int,
    note_value: str,
) -> None:
    """Generate MIDI from a logistic-map bifurcation diagram."""
    _echo_banner()
    request = _request(
        r_start=r_start,
        r_end=r_end,
        r_step_size=r_step_size,
        iterations=number_of_iterations_per_r_value,
        burn_in=burn_in,
        initial_x_behaviour=x_initial_value_behaviour,
        arpeggiate=arpeggiate,
        pedal=pedal,
        bpm=bpm,
        note_value=note_value,
    )
    _echo_request(request, out, plot_diagram, midi_out_device)
    _deliver(_performance(request), out, midi_out_device, plot_diagram)


def _echo_banner() -> None:
    version = importlib.metadata.version("bifurc2midi")
    click.echo(f"bifurc2midi v{version}\n")


def _request(
    *,
    r_start: float,
    r_end: float,
    r_step_size: float,
    iterations: int,
    burn_in: int,
    initial_x_behaviour: str,
    arpeggiate: bool,
    pedal: bool,
    bpm: int,
    note_value: str,
) -> PerformanceRequest:
    return PerformanceRequest(
        r_start=r_start,
        r_end=r_end,
        r_step_size=r_step_size,
        iterations=iterations,
        burn_in=burn_in,
        initial_x_behaviour=_BEHAVIOURS[initial_x_behaviour],
        initial_x=None,
        arpeggiate=arpeggiate,
        pedal_on=pedal,
        bpm=bpm,
        note_value=NoteValue[note_value.upper()],
    )


def _echo_request(
    request: PerformanceRequest,
    out: str,
    plot_diagram: bool,
    midi_out_device: str | None,
) -> None:
    click.echo(
        "Running with options:\n"
        f"\tr interval: ({request.r_start}, {request.r_end})\n"
        f"\tr step size: {request.r_step_size}\n"
        f"\tNumber of iterations per r value: {request.iterations}\n"
        f"\tBurn in: {request.burn_in}\n"
        f"\tx value initial behaviour: {request.initial_x_behaviour.value}\n"
        f"\tMidi out filename: {out}\n"
        f"\tPlot diagram: {plot_diagram}\n"
        f"\tMidi out device: {midi_out_device}\n"
        f"\tArpeggiate: {request.arpeggiate}\n"
        f"\tPedal on: {request.pedal_on}\n"
        f"\tBPM: {request.bpm}\n"
        f"\tNote value: {request.note_value.name.title()}\n"
    )


def _performance(request: PerformanceRequest) -> Performance:
    try:
        return perform(request)
    except ValueError as error:
        raise click.ClickException(str(error)) from error


def _deliver(
    performance: Performance,
    out: str,
    midi_out_device: str | None,
    plot_diagram: bool,
) -> None:
    output_name = _output_name(midi_out_device)
    if out or output_name is not None:
        _write_and_play(performance, out, output_name)
    if plot_diagram:
        plot(performance.diagram)


def _output_name(midi_out_device: str | None) -> str | None:
    if midi_out_device is None:
        return None
    try:
        return resolve_output_name(midi_out_device, available_output_names())
    except MidiOutputError as error:
        raise click.ClickException(str(error)) from error


def _write_and_play(
    performance: Performance,
    out: str,
    output_name: str | None,
) -> None:
    midi = score_to_midi(performance.score)
    if out:
        save(midi, out)
        click.echo(f"Saved midi file to: {out}")
    if output_name is not None:
        click.echo(f"Playing midi on device: {output_name}")
        play(midi, output_name)
