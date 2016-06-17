from const import *

def isint(string):
    try:
        int(string)
        return True
    except ValueError:
        return False

def to_ticks(bars=1, beats=0, ticks=0, bpb=4,
    tpq=TICKS_PER_QUARTER_NOTE):
    ticks_per_bar = bpb * tpq
    return (bars * ticks_per_bar + beats * tpq + ticks)

def to_notedur(ticks, bpb=4, tpq=TICKS_PER_QUARTER_NOTE):
    ticks_per_bar = bpb * tpq
    bars = int(ticks / ticks_per_bar)
    beat = int((ticks / tpq) % bpb)
    ticks_ = int(ticks % tpq)
    return [bars, beat, ticks_]

def save_song(filename, song_data):
    f = open(filename, 'w')

    note_list = song_data['note_list']
    beat_count = song_data['beat_count']
    length = song_data['length']

    f.write("{0} {1} {2};\n".format(*[str(x) for x in length]))

    for note in note_list:
        note_left = note.rect[0]
        note_top = note.rect[1]
        note_width = note.rect[2]

        grid_height = CELL_HEIGHT_IN_PX * 128
        midinumber = int((grid_height - note_top) / CELL_HEIGHT_IN_PX) - 1

        ticks = note_left * TICKS_PER_QUARTER_NOTE / QUARTER_NOTE_WIDTH
        pos = to_notedur(ticks, beat_count)
        pos[0] += 1
        pos[1] += 1

        ticks = note_width * TICKS_PER_QUARTER_NOTE / QUARTER_NOTE_WIDTH
        dur = to_notedur(ticks, beat_count)
        f.write("{0} | 100 | {1} {2} {3} | {4} {5} {6};\n".format(
            midinumber, pos[0], pos[1], pos[2], dur[0], dur[1],
            dur[2]))