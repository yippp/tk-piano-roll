def find_indices(list, *elements):
    return [i for i, x in enumerate(list) if x in elements]