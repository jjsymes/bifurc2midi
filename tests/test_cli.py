from click.testing import CliRunner
from mido import MidiFile

import bifurc2midi.adapters.cli as cli_module
from bifurc2midi.adapters.cli import cli
from bifurc2midi.application.perform import Performance
from bifurc2midi.domain.diagram import BifurcationDiagram, InitialXBehaviour, Orbit
from bifurc2midi.domain.music import MusicalEvent, NoteValue, Score

_PERFORMANCE = Performance(
    diagram=BifurcationDiagram((Orbit(2.0, (0.25,)),)),
    score=Score(
        ticks_per_beat=960,
        tempo_bpm=120,
        pedal_down=True,
        events=(MusicalEvent((60,), 240),),
    ),
)


def _install_boundaries(monkeypatch, available=None):
    captured = {}

    def perform(request):
        captured["request"] = request
        return _PERFORMANCE

    def save(midi, filename):
        captured["saved"] = (midi, filename)

    def play(midi, output_name):
        captured["played"] = (midi, output_name)

    def plot(diagram):
        captured["plotted"] = diagram

    monkeypatch.setattr(cli_module, "perform", perform)
    monkeypatch.setattr(cli_module, "save", save)
    monkeypatch.setattr(cli_module, "play", play)
    monkeypatch.setattr(cli_module, "plot", plot)
    monkeypatch.setattr(
        cli_module,
        "available_output_names",
        lambda: [] if available is None else available,
    )
    return captured


def test_defaults_request_a_static_sixteenth_note_performance(monkeypatch):
    captured = _install_boundaries(monkeypatch)

    result = CliRunner().invoke(cli, [])

    request = captured["request"]
    assert result.exit_code == 0
    assert "bifurc2midi v0.0.1" in result.output
    assert request.r_start == 2.9
    assert request.r_end == 4
    assert request.r_step_size == 0.001
    assert request.iterations == 1000
    assert request.burn_in == 990
    assert request.initial_x is None
    assert request.initial_x_behaviour is InitialXBehaviour.STATIC
    assert request.arpeggiate is True
    assert request.pedal_on is True
    assert request.bpm == 120
    assert request.note_value is NoteValue.SIXTEENTH
    midi, filename = captured["saved"]
    assert filename == "out.mid"
    assert isinstance(midi, MidiFile)
    assert "played" not in captured
    assert "plotted" not in captured


def test_negative_flags_turn_arpeggio_and_pedal_off(monkeypatch):
    captured = _install_boundaries(monkeypatch)

    result = CliRunner().invoke(cli, ["--no-arpeggiate", "--no-pedal"])

    assert result.exit_code == 0
    assert captured["request"].arpeggiate is False
    assert captured["request"].pedal_on is False


def test_note_value_and_behaviour_accept_the_cli_names(monkeypatch):
    captured = _install_boundaries(monkeypatch)

    result = CliRunner().invoke(
        cli,
        [
            "--note-value",
            "EIGHTH",
            "--x-initial-value-behaviour",
            "last_logistic_map_x",
        ],
    )

    assert result.exit_code == 0
    assert captured["request"].note_value is NoteValue.EIGHTH
    assert (
        captured["request"].initial_x_behaviour is InitialXBehaviour.LAST_LOGISTIC_MAP_X
    )


def test_plot_receives_the_diagram_perform_returned(monkeypatch):
    captured = _install_boundaries(monkeypatch)

    result = CliRunner().invoke(cli, ["--plot-diagram"])

    assert result.exit_code == 0
    assert captured["plotted"] is _PERFORMANCE.diagram


def test_default_device_plays_the_saved_file(monkeypatch):
    captured = _install_boundaries(monkeypatch, available=["IAC", "default"])

    result = CliRunner().invoke(cli, ["--midi-out-device", "default"])

    assert result.exit_code == 0
    saved_midi, filename = captured["saved"]
    played_midi, output_name = captured["played"]
    assert filename == "out.mid"
    assert output_name == "IAC"
    assert played_midi is saved_midi
    assert "Playing midi on device: IAC" in result.output


def test_missing_device_exits_without_a_traceback(monkeypatch):
    captured = _install_boundaries(monkeypatch, available=[])

    result = CliRunner().invoke(cli, ["--midi-out-device", "default"])

    assert result.exit_code != 0
    assert "No MIDI output devices found" in result.output
    assert "Traceback" not in result.output
    assert "saved" not in captured


def test_unknown_device_lists_the_available_names(monkeypatch):
    _install_boundaries(monkeypatch, available=["IAC"])

    result = CliRunner().invoke(cli, ["--midi-out-device", "missing"])

    assert result.exit_code != 0
    assert "IAC" in result.output
    assert "Traceback" not in result.output


def test_reversed_r_range_is_a_clean_error():
    result = CliRunner().invoke(cli, ["--r-start", "3", "--r-end", "1"])

    assert result.exit_code != 0
    assert "r end" in result.output
    assert "Traceback" not in result.output


def test_version_option_prints_the_package_version():
    result = CliRunner().invoke(cli, ["--version"])

    assert result.exit_code == 0
    assert "0.0.1" in result.output


def test_main_invokes_the_command(monkeypatch):
    from bifurc2midi.__main__ import main

    called = {"value": False}
    monkeypatch.setattr(
        "bifurc2midi.__main__.cli",
        lambda: called.__setitem__("value", True),
    )

    main()

    assert called["value"] is True


def test_help_documents_the_negative_flags():
    result = CliRunner().invoke(cli, ["--help"])

    assert result.exit_code == 0
    assert "--no-arpeggiate" in result.output
    assert "--no-pedal" in result.output


def test_empty_output_path_skips_saving(monkeypatch):
    captured = _install_boundaries(monkeypatch)

    result = CliRunner().invoke(cli, ["-o", ""])

    assert result.exit_code == 0
    assert "saved" not in captured


def test_empty_output_path_can_still_play(monkeypatch):
    captured = _install_boundaries(monkeypatch, available=["IAC"])

    result = CliRunner().invoke(cli, ["-o", "", "--midi-out-device", "IAC"])

    assert result.exit_code == 0
    assert "saved" not in captured
    assert captured["played"][1] == "IAC"
