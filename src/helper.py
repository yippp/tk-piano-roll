def to_ticks(bars, beats, ticks):
    from const import DEFAULT_BAR_WIDTH_IN_PX

    return ((bars - 1) * DEFAULT_BAR_WIDTH_IN_PX +
        (beats - 1) * DEFAULT_BAR_WIDTH_IN_PX / 4 +
        ticks * DEFAULT_BAR_WIDTH_IN_PX / 256)