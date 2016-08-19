import os
from const import *


def dummy(*args, **kwargs):
    pass

def isint(string):
    try:
        int(string)
        return True
    except ValueError:
        return False

def clamp(x, minimum, maximum):
    return max(minimum, min(x, maximum))

def make_title(name, dirty):
    return "{0}{1} - Piano Roll".format(
        "*" if dirty else "", name)

def get_image_path(filename):
    this_path = os.path.dirname(os.path.abspath(__file__))
    return "{1}{0}..{0}images{0}{2}".format(
        os.sep, this_path, filename)

def to_pitchname(midinumber):
    note = PITCHNAMES[midinumber % 12]
    octave = int(midinumber / 12) - 2
    return "{0}{1}".format(note, octave)

def to_midinumber(pitchname):
    import re

    m = re.search('[-\d]', pitchname)
    if (not m or pitchname[:m.start()].upper()
        not in PITCHNAMES):
        raise ValueError("{} is not a valid pitchname".format(
            pitchname))

    pitch = pitchname[:m.start()]
    octave = int(pitchname[m.start():])
    return PITCHNAMES.index(pitch) + (octave + 2) * 12

def hex_to_rgb(value):
    value = value.lstrip('#')
    lv = len(value)
    return tuple(int(value[i:i + lv // 3], 16)
        for i in range(0, lv, lv // 3))

def rgb_to_hex(r, g, b):
    from functools import partial
    clp = partial(clamp, minimum=0, maximum=255)
    return "#{0:02x}{1:02x}{2:02x}".format(
        clp(r), clp(g), clp(b))

def velocity_to_color(velocity, maxcolor, value):
    from colorsys import rgb_to_hsv, hsv_to_rgb

    to_percentage = lambda x: x / 255.0
    from_percentage = lambda x: int(round(x * 255.0))

    r, g, b = map(to_percentage, hex_to_rgb(maxcolor))
    h, s, v = rgb_to_hsv(r, g, b)
    s = velocity * 0.007086614 + 0.30
    v *= value
    r, g, b = map(from_percentage, hsv_to_rgb(h, s, v))
    return rgb_to_hex(r, g, b)

def to_ticks(bars=1, beats=0, ticks=0, bpb=4, bu=4,
    tpq=TICKS_PER_QUARTER_NOTE):
    ticks_per_beat = tpq * 4 / bu
    ticks_per_bar = bpb * ticks_per_beat
    return (bars * ticks_per_bar +
        beats * ticks_per_beat + ticks)

def to_notedur(ticks, bpb=4, bu=4, tpq=TICKS_PER_QUARTER_NOTE):
    ticks_per_beat = tpq * 4 / bu
    ticks_per_bar = bpb * ticks_per_beat
    bars = int(ticks / ticks_per_bar)
    beat = int((ticks / ticks_per_beat) % bpb)
    ticks_ = int(ticks % ticks_per_beat)
    return [bars, beat, ticks_]

def tick_to_px(ticks, qw=QUARTER_NOTE_WIDTH, tpq=TICKS_PER_QUARTER_NOTE):
    return float(ticks) / tpq * qw

def px_to_tick(px, qw=QUARTER_NOTE_WIDTH, tpq=TICKS_PER_QUARTER_NOTE):
    return float(px) / qw * tpq

def save_composition(filename, comp_state):
    grid = comp_state.grid
    notes = comp_state.notes
    end = grid.end
    timesig = grid.timesig

    f = open(filename, 'w')
    f.write("{0} {1} {2};\n".format(*[str(x) for x in end]))
    f.write("{0} {1};\n".format(*timesig))

    for note in notes:
        onset = to_notedur(note.onset, *timesig)
        onset[0] += 1
        onset[1] += 1

        dur = to_notedur(note.duration, *timesig)
        f.write("{0} | {1} | {2} {3} {4} | {5} {6} {7};\n".format(
            note.midinumber, note.velocity, onset[0], onset[1],
            onset[2], dur[0], dur[1], dur[2]))

def load_composition(filename):
    from models.piano_roll_model import PianoRollModel
    from models.grid_model import GridModel
    from models.note_list_model import NoteListModel
    from models.note_model import NoteModel

    with open(filename, 'r') as f:
        try:
            end = map(
                lambda n: int(n),
                f.readline().strip()[:-1].split(" "))

            timesig = map(
                int, f.readline().strip()[:-1].split(" "))

            notes = []
            for line in f:
                tokens = map(str.strip, line.strip()[:-1].split("|"))

                midinumber = int(tokens[0])
                velocity = int(tokens[1])
                onset_bar, onset_beat, onset_tick = map(
                    int, tokens[2].split(" "))
                dur_bar, dur_beat, dur_tick = map(
                    int, tokens[3].split(" "))
                onset = to_ticks(
                    onset_bar - 1, onset_beat - 1,
                    onset_tick, *timesig)
                dur = to_ticks(
                    dur_bar, dur_beat, dur_tick,
                    *timesig)

                notes.append(NoteModel(midinumber, velocity, onset, dur))

            return PianoRollModel(
                GridModel(timesig=timesig, end=end),
                NoteListModel(notes)
            )

        except IOError:
            print "Could not read file '{0}'".format(filename)

