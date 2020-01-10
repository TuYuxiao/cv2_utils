from .layers import Layer, SourceLayer


class Sequential(Layer):
    def __init__(self, layers=[]):
        Layer.__init__(self)

        self._layers = []

        for layer in layers:
            self.add(layer)

    @property
    def layers(self):
        if len(self._layers) > 0 and isinstance(self._layers[0], SourceLayer):
            return self._layers[1:]
        return self._layers

    def __iter__(self):
        assert len(self._layers) > 0 and isinstance(self._layers[0], SourceLayer)
        return self

    def __next__(self):
        frame = next(self._layers[0])
        return self.inference(frame)

    def add(self, layer):
        assert isinstance(layer, Layer)

        self._layers.append(layer)

    def inference(self, img):
        for layer in self.layers:
            img = layer.inference(img)
        return img
