from const import *

def dummy(*args, **kwargs):
    pass

def make_title(name, dirty):
    return "{0}{1} - Piano Roll".format(
        "*" if dirty else "", name)

def isint(string):
    try:
        int(string)
        return True
    except ValueError:
        return False

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

def save_song(filename, song_data):
    f = open(filename, 'w')

    notes = song_data['notes']
    length = song_data['length']
    timesig = song_data['timesig']

    f.write("{0} {1} {2};\n".format(*[str(x) for x in length]))
    f.write("{0} {1};\n".format(*timesig))

    for note in notes:
        onset = to_notedur(note.onset, *timesig)
        onset[0] += 1
        onset[1] += 1

        dur = to_notedur(note.duration, *timesig)
        f.write("{0} | {1} | {2} {3} {4} | {5} {6} {7};\n".format(
            note.midinumber, note.velocity, onset[0], onset[1],
            onset[2], dur[0], dur[1], dur[2]))

def load_song(filename):
    from note import Note

    with open(filename, 'r') as f:
        try:
            length = map(
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

                notes.append(Note(midinumber, velocity, onset, dur))

            return {
                'notes': notes,
                'length': length,
                'timesig': timesig
            }

        except IOError:
            print "Could not read file '{0}'".format(filename)