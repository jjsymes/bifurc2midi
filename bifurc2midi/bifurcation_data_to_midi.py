from math import ceil, floor

from mido import Message, MetaMessage, MidiFile, MidiTrack, bpm2tempo

from bifurc2midi.bifurcation_data import BifurcationData
from bifurc2midi.music import NoteValue


def bifurcation_data_to_midi(
    bifurcation_data: BifurcationData,
    arpeggiate: bool = True,
    pedal_on: bool = True,
    bpm: int = 120,
    note_value: NoteValue = NoteValue.SIXTEENTH,
    note_blend: float = 0.0,
) -> MidiFile:
    number_of_pitch_levels = 88
    ticks_per_beat = 960
    tempo = bpm2tempo(bpm)

    bifurcation_data.transform_x_values(lambda x: x * number_of_pitch_levels)
    bifurcation_data.transform_x_values(lambda x: round(x, 2))
    bifurcation_data.remove_duplicate_x_values()

    # https://mido.readthedocs.io/en/latest/midi_files.html -> A beat is the same as a quarter note.
    ticks_per_note_value_mapping = {
        NoteValue.WHOLE: ticks_per_beat * 4,
        NoteValue.HALF: ticks_per_beat * 2,
        NoteValue.QUARTER: ticks_per_beat,
        NoteValue.EIGHTH: ticks_per_beat // 2,
        NoteValue.SIXTEENTH: ticks_per_beat // 4,
        NoteValue.THIRTYSECOND: ticks_per_beat // 8,
        NoteValue.SIXTYFOURTH: ticks_per_beat // 16,
    }

    mid = MidiFile(ticks_per_beat=ticks_per_beat)
    track = MidiTrack()
    mid.tracks.append(track)

    track.append(MetaMessage("set_tempo", tempo=tempo))

    if pedal_on:
        pedal_on_msg = Message("control_change", control=64, value=127, time=0)
        track.append(pedal_on_msg)

    for i, _ in enumerate(bifurcation_data.x_values):
        if note_blend == 0.0:
            notes = {int(note) for note in bifurcation_data.x_values[i]}
        else:
            notes = {note for note in bifurcation_data.x_values[i]}
            notes_with_blend = set()
            for note in notes:
                decimal_part = note % 1
                if decimal_part > 0.5 - (note_blend / 2) and decimal_part < 0.5 + (
                    note_blend / 2
                ):
                    notes_with_blend.add(floor(note))
                    notes_with_blend.add(ceil(note))
                else:
                    notes_with_blend.add(round(note))
            notes = {int(note) for note in notes_with_blend}

        notes_list = list(notes)
        notes_list.sort()
        if arpeggiate:
            notes_list = [notes_list[i % len(notes_list)]]

        for note in notes_list:
            track.append(Message("note_on", note=note, velocity=64, time=0))

        for i, note in enumerate(notes_list):
            if i == 0:
                track.append(
                    Message(
                        "note_off",
                        note=note,
                        velocity=127,
                        time=ticks_per_note_value_mapping[note_value],
                    )
                )
            else:
                track.append(Message("note_off", note=note, velocity=127, time=0))

    return mid
