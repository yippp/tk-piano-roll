def find_indices(list, *elements):
    return [i for i, x in enumerate(list) if x in elements]

def make_vcmd(instance, func):
    from Tkinter import Widget
    return (Widget.register(instance, func), '%d', '%i', '%P', '%s',
        '%S', '%v', '%V', '%W')