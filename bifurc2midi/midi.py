from mido import MidiFile, get_output_names, open_output


def get_available_midi_output_names():
    return get_output_names()


def get_default_midi_output_name() -> str:
    output_names = get_available_midi_output_names()
    if len(output_names) == 0:
        raise Exception("No MIDI output devices found")
    return output_names[0]


def play_midi_file(midi: MidiFile, output_name: str):
    output = open_output(output_name)
    for msg in midi.play():
        output.send(msg)


def save_midi_file(midi: MidiFile, filename: str):
    midi.save(filename)
