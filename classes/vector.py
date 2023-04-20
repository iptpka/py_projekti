import pygame as pg

# A layer of vector objects
class Vector_layer:
    def __init__(self, id, depth, viewport, colorkey=(0, 255, 255)):
        self.id = id
        self.depth = depth
        self.width = viewport.get_width()
        self.height = viewport.get_height()
        self.surface = pg.Surface((self.width, self.height))
        self.surface.set_colorkey(colorkey)
        self.objects = []

    def add_object(self, obj):
        self.objects.append(obj)

    def draw(self):
        for obj in self.objects:
            obj.draw(self.surface)

    def clear(self):
        self.surface.fill((0, 255, 255))