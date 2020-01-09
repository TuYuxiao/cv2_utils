from .layers import Layer


class Sequential(Layer):
    def __init__(self, layers=[]):
        Layer.__init__(self)

        for layer in layers:
            self.add(layer)

        self._layers = []

    @property
    def layers(self):
        return self._layers

    def add(self, layer):
        assert isinstance(layer, Layer)

        self._layers.append(layer)

    def forward(self, img):
        for layer in self._layers:
            img = layer.forward(img)
        return img
