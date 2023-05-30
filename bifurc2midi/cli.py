import click
import pkg_resources

from bifurc2midi.bifurcation_data import (
    BifurcationData,
    LogisticMapInitialXValueBehaviour,
)
from bifurc2midi.bifurcation_data_to_midi import bifurcation_data_to_midi
from bifurc2midi.midi import (
    get_available_midi_output_names,
    get_default_midi_output_name,
    play_midi_file,
    save_midi_file,
)
from bifurc2midi.music import NoteValue


@click.version_option()
@click.command()
@click.option(
    "--r-start",
    type=float,
    default=2.9,
    help="Start of r interval range. Defaults to 2.9",
)
@click.option(
    "--r-end", type=float, default=4, help="End of r interval range. Defaults to 4"
)
@click.option(
    "--r-step-size",
    type=float,
    default=0.001,
    help="Step size of r interval range. Defaults to 0.001",
)
@click.option(
    "--number-of-iterations-per-r-value",
    type=int,
    default=1000,
    help="Number of iterations of the logistic map per r value. Defaults to 1000",
)
@click.option(
    "--burn-in",
    type=int,
    default=990,
    help="Number of iterations to discard at the start of each r value. Defaults to 990",
)
@click.option(
    "--x-initial-value-behaviour",
    type=LogisticMapInitialXValueBehaviour,
    default=LogisticMapInitialXValueBehaviour.STATIC,
    help="Initial x value for each logistic map. Defaults to static randomly generated value.",
)
@click.option("-o", "--out", type=str, default="out.mid", help="Output midi file name")
@click.option(
    "-p", "--plot-diagram", is_flag=True, help="Plot the logistic map data on a diagram"
)
@click.option(
    "-d",
    "--midi-out-device",
    type=str,
    default=None,
    help="Midi output device name. Use 'default' to use the first available device.",
)
@click.option(
    "--arpeggiate",
    type=bool,
    default=True,
    help="Arpeggiate the notes in the midi output. Defaults to True.",
)
@click.option(
    "--pedal-on",
    type=bool,
    default=True,
    help="Hold the sustain pedal. Defaults to True.",
)
@click.option(
    "--bpm",
    type=int,
    default=120,
    help="Beats per minute. Defaults to 120.",
)
@click.option(
    "--note-value",
    type=NoteValue,
    default=NoteValue.SIXTEENTH,
    help="Note value. Defaults to sixteenth.",
)
def cli(
    r_start: float,
    r_end: float,
    r_step_size: float,
    number_of_iterations_per_r_value: int,
    burn_in: int,
    x_initial_value_behaviour: LogisticMapInitialXValueBehaviour,
    out: str,
    plot_diagram: bool,
    midi_out_device: str,
    arpeggiate: bool,
    pedal_on: bool,
    bpm: int,
    note_value: NoteValue,
):
    """An application that generates midi from generated logistic map bifurcation data."""

    r_interval = (r_start, r_end)
    r_step_size = r_step_size
    number_of_iterations_per_r_value = number_of_iterations_per_r_value
    burn_in = burn_in
    x_initial_value_behaviour = x_initial_value_behaviour
    midi_out_filename = out
    plot_diagram = plot_diagram
    midi_out_device = midi_out_device

    package = "bifurc2midi"
    version = pkg_resources.require(package)[0].version
    click.echo("bifurc2midi v" + version + "\n")

    click.echo(
        "Running with options:"
        f"\tr interval: {r_interval}\n"
        f"\tr step size: {r_step_size}\n"
        f"\tNumber of iterations per r value: {number_of_iterations_per_r_value}\n"
        f"\tBurn in: {burn_in}\n"
        f"\tx value initial behaviour: {x_initial_value_behaviour}\n"
        f"\tMidi out filename: {midi_out_filename}\n"
        f"\tPlot diagram: {plot_diagram}\n"
        f"\tMidi out device: {midi_out_device}\n"
        f"\tArpeggiate: {arpeggiate}\n"
        f"\tPedal on: {pedal_on}\n"
        f"\tBPM: {bpm}\n"
        f"\tNote value: {note_value.name.title()}\n"
    )

    bifurcation_data = BifurcationData.from_data_generation_parameters(
        r_interval[0],
        r_interval[1],
        r_step_size,
        number_of_iterations_per_r_value,
        x_initial_behaviour=x_initial_value_behaviour,
        burn_in=burn_in,
    )

    midi = bifurcation_data_to_midi(
        bifurcation_data, arpeggiate, pedal_on, bpm, note_value
    )

    if out:
        save_midi_file(midi, out)
        click.echo("Saved midi file to: " + out)

    if midi_out_device:
        if (
            midi_out_device == "default"
            and midi_out_device not in get_available_midi_output_names()
        ):
            midi_out_device = get_default_midi_output_name()

        click.echo(f"Playing midi on device: {midi_out_device}")
        play_midi_file(midi, midi_out_device)

    if plot_diagram:
        bifurcation_data.plot()
