# Example file showing a circle moving on screen
import pygame as pg
import pygame.gfxdraw as gfx


class Curve_point:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.collider = pg.Rect(x - 5, y - 5, 10, 10)


class Curve_segment:
    def __init__(self, start, control, stop, steps=100, color=(0, 0, 0)):
        self.start = start
        self.control = control
        self.stop = stop
        self.steps = steps
        self.color = color
        self.points = [self.start, self.control, self.stop]

    def draw(self, surface):
        gfx.bezier(surface, [(p.x, p.y)
                   for p in self.points], self.steps, self.color)

    def draw_points(self, surface, x_offset=0, y_offset=0):
        for point in self.points:
            pg.draw.circle(surface, (0, 0, 0), (point.x +
                           x_offset, point.y + y_offset), 5)

    def update_point_colliders(self):
        for point in self.points:
            point.collider.center = (point.x, point.y)

class Curve:
    def __init__(self, segments):
        self.segments = segments

    def draw(self, surface):
        for segment in self.segments:
            segment.draw(surface)

    def draw_points(self, surface, x_offset=0, y_offset=0):
        for segment in self.segments:
            segment.draw_points(surface, x_offset, y_offset)

    def update_point_colliders(self):
        for segment in self.segments:
            segment.update_point_colliders()
    
    def get_points(self):
        points = []
        for segment in self.segments:
            for point in segment.points:
                points.append(point)
        return points


class Vector_object:
    def __init__(self, width, height, position, colorkey=(0, 255, 255)):
        self.width = width
        self.height = height
        self.surface = pg.Surface((width, height))
        self.surface.set_colorkey(colorkey)
        self.position = position

    def add_object(self, obj):
        self.segments.append(obj)

    def draw(self):
        pass

    def draw_points(self):
        for obj in self.segments:
            obj.draw_points(self.surface, self.x_offset, self.y_offset)

    def update_point_colliders(self):
        for obj in self.segments:
            obj.update_point_colliders(self.x_offset, self.y_offset)


""" class Vector_object_group:
    def __init__(self, width, height, colorkey=(0, 255, 255)):
        self.surface = pg.Surface((width, height))
        self.surface.set_colorkey(colorkey)
        self.objects = []

    def add_object(self, obj):
        self.objects.append(obj)

    def draw(self):
        for obj in self.objects:
            obj.draw()

    def draw_points(self):
        for obj in self.objects:
            obj.draw_points()

    def update_point_colliders(self):
        for obj in self.objects:
            obj.update_point_colliders() """


# pyg setup
pg.init()
screen = pg.display.set_mode((1280, 720))
clock = pg.time.Clock()
running = True
dt = 0

viewport_width_percent = 0.8
viewport_height_percent = 0.9
editor_viewport = pg.Surface((screen.get_width()*viewport_width_percent, screen.get_height()*viewport_height_percent))
editor_viewport.set_colorkey((0, 255, 255))
viewport_x_offset = screen.get_width() * (1 - viewport_width_percent) / 4
viewport_y_offset = screen.get_height() * (1 - viewport_height_percent) / 2


vector_surface = pg.Surface((1280, 720))
vector_surface.set_colorkey((255, 255, 255))
test_curve = Curve_segment(Curve_point(0, 0), Curve_point(
    200, 200), Curve_point(300, 100), 100, (0, 0, 0))
test_curve.update_point_colliders()

player_pos = pg.Vector2(editor_viewport.get_width() / 2,
                        editor_viewport.get_height() / 2)
selected_object = test_curve
selected_point = None


while running:
    # poll for events
    # pg.QUIT event means the user clicked X to close your window
    for event in pg.event.get():
        if event.type == pg.QUIT:
            running = False
        if event.type == pg.MOUSEBUTTONDOWN:
            if event.button == 1:
                for point in selected_object.points:
                    if point.collider.collidepoint((event.pos[0] - viewport_x_offset-player_pos.x, event.pos[1] - viewport_y_offset-player_pos.y)):
                        selected_point = point
                        break
            if event.button == 3:
                selected_object.points.append(Curve_point(
                    event.pos[0] - viewport_x_offset-player_pos.x, event.pos[1] - viewport_y_offset-player_pos.y))
                selected_object.update_point_colliders()
        if event.type == pg.MOUSEBUTTONUP:
            if event.button == 1:
                selected_point = None

    if selected_point != None:
        selected_point.x = pg.mouse.get_pos()[0] - viewport_x_offset-player_pos.x
        selected_point.y = pg.mouse.get_pos()[1] - viewport_y_offset-player_pos.y
        selected_object.update_point_colliders()

    # fill the screen with a color to wipe away anything from last frame
    screen.fill("grey")
    vector_surface.fill((255, 255, 255))
    editor_viewport.fill((255, 255, 255))
    test_curve.draw(vector_surface)
    editor_viewport.blit(vector_surface, player_pos)
    test_curve.draw_points(editor_viewport, int(
        player_pos.x), int(player_pos.y))
    screen.blit(editor_viewport, (viewport_x_offset, viewport_y_offset))

    # flip() the display to put your work on screen
    pg.display.flip()

    # limits FPS to 60
    # dt is delta time in seconds since last frame, used for framerate-
    # independent physics.
    dt = clock.tick(60) / 1000

pg.quit()
