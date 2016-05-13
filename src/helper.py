def calc_ticks_per_bar(sixteenth_unit_width, beat_count, beat_unit):
    from math import log
    sixteenth_units_per_beat = 2 ** (4 - log(float(beat_unit), 2))
    sixteenth_units_per_bar = beat_count * sixteenth_units_per_beat
    return sixteenth_unit_width * sixteenth_units_per_bar

def to_ticks(bars, beats, ticks, ticks_per_bar, beat_count):
    ticks_per_beat = ticks_per_bar / beat_count
    return ((bars - 1) * ticks_per_bar + (beats - 1) * ticks_per_beat + ticks)

def to_notedur(ticks, ticks_per_bar, beat_count):
    ticks_per_beat = ticks_per_bar / beat_count
    bars = int(ticks / ticks_per_bar)
    beat = int((ticks / ticks_per_beat) % beat_count)
    ticks_ = int(ticks % ticks_per_beat)
    return [bars, beat, ticks_]

def make_vcmd(instance, func):
    from Tkinter import Widget
    return (Widget.register(instance, func), '%d', '%i', '%P', '%s',
        '%S', '%v', '%V', '%W')