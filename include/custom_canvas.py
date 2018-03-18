from tkinter import Canvas, ALL


class CustomCanvas(Canvas):

    def __init__(self, *args, **kwargs):
        Canvas.__init__(self, *args, **kwargs)
        self._layers = []

        if not kwargs.get('highlightthickness'):
            self.config(highlightthickness=0)

    def add_to_layer(self, layer, command, coords, **kwargs):
        layer_tag = "layer {}".format(layer)
        if layer_tag not in self._layers: self._layers.append(layer_tag)
        tags = kwargs.setdefault("tags", [])

        if (isinstance(tags, str)): tags = [tags]
        else: tags = list(tags)

        tags.append(layer_tag)
        kwargs['tags'] = tags
        item_id = command(coords, **kwargs)
        self._adjust_layers()

        return item_id

    def _adjust_layers(self):
        for layer in sorted(self._layers, reverse=True):
            self.lift(layer)

    def find_withtags(self, *args):
        itrsec = self.find_withtag(ALL)

        if all(isinstance(arg, str) for arg in args):
            for tag in args:
                matches = self.find_withtag(tag)
                itrsec = list(set(itrsec).intersection(matches))
        else:
            raise TypeError

        return itrsec
