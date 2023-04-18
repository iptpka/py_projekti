# Example file showing a circle moving on screen
import pygame as pg
import pygame.gfxdraw as gfx


# A single point on a curve
class Curve_point:
    def __init__(self, position):
        self.x = position[0]
        self.y = position[1]
        self.collider = pg.Rect(self.x - 5, self.y - 5, 10, 10)

    def position(self):
        return (self.x, self.y)


# A single curve segment
class Curve:
    def __init__(self, start, first_control, second_control, end, steps=100, color=(0, 0, 0)):
        self.points = [start, first_control, second_control, end]
        self.steps = steps
        self.color = color

    def draw(self, surface, position):
        gfx.bezier(surface, [(p.x + position[0], p.y + position[1])
                   for p in self.points], self.steps, self.color)

    def draw_controls(self, surface, offset_position):
        pg.draw.line(surface, (0, 0, 0), (self.points[0].x + offset_position[0], self.points[0].y +
                     offset_position[1]), (self.points[1].x + offset_position[0], self.points[1].y + offset_position[1]))
        pg.draw.line(surface, (0, 0, 0), (self.points[2].x + offset_position[0], self.points[2].y +
                     offset_position[1]), (self.points[3].x + offset_position[0], self.points[3].y + offset_position[1]))
        for point in [self.points[0], self.points[3]]:
            pg.draw.circle(surface, (0, 0, 0), (point.x +
                           offset_position[0], point.y + offset_position[1]), 5)
        for point in [self.points[1], self.points[2]]:
            pg.draw.circle(surface, (0, 200, 0), (point.x +
                           offset_position[0], point.y + offset_position[1]), 5)

    def update_point_colliders(self, offset_position):
        for point in self.points:
            point.collider.center = (
                point.x + offset_position[0], point.y + offset_position[1])

    def bounding_box(self):
        x_min = min([p.x for p in self.points])
        x_max = max([p.x for p in self.points])
        y_min = min([p.y for p in self.points])
        y_max = max([p.y for p in self.points])
        return pg.Rect(x_min, y_min, x_max - x_min, y_max - y_min)

    def get_points(self):
        return self.points

# A composite of multiple curves


class Path:
    def __init__(self, start_segment=None, position=(0, 0)):
        self.segments = [start_segment] if not start_segment is None else []
        self.position = position
        self.first_point = start_segment.get_points(
        )[0] if not start_segment is None else None
        self.last_point = start_segment.get_points(
        )[3] if not start_segment is None else None

    def add_segment_to_point(self, point):
        if self.last_point is None:
            self.first_point = point
            self.last_point = point
        else:
            self.segments.append(Curve(self.last_point, Curve_point(
                self.last_point.position()), Curve_point(point.position()), point))
            self.last_point = point

    def draw(self, surface):
        for segment in self.segments:
            segment.draw(surface, self.position)

    def draw_controls(self, surface):
        for segment in self.segments:
            segment.draw_controls(surface, self.position)

    def update_point_colliders(self):
        for segment in self.segments:
            segment.update_point_colliders(self.position)

    def get_points(self):
        points = []
        for segment in self.segments:
            for point in segment.points:
                points.append(point)
        return points

    def bounding_box(self):
        bounding_boxes = [segment.bounding_box() for segment in self.segments]
        bounding_box = pg.rect.unionall(bounding_boxes)
        return bounding_box


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


# pyg setup
pg.init()
screen = pg.display.set_mode((1280, 720))
clock = pg.time.Clock()
running = True
dt = 0

viewport_width_percent = 0.8
viewport_height_percent = 0.9
editor_viewport = pg.Surface((screen.get_width(
)*viewport_width_percent, screen.get_height()*viewport_height_percent))
editor_viewport.set_colorkey((0, 255, 255))
viewport_x_offset = screen.get_width() * (1 - viewport_width_percent) / 4
viewport_y_offset = screen.get_height() * (1 - viewport_height_percent) / 2


layer_1 = Vector_layer(1, 1, editor_viewport)
test_curve = Curve(*[Curve_point(position) for position in ((0, 0),
                   (200, 200), (300, 100), (300, 0))], 100, (0, 0, 0))
test_path = Path(test_curve, (100, 100))
layer_1.add_object(test_path)
selected_object = test_path
selected_point = None
selected_object.update_point_colliders()
for point in selected_object.get_points():
    print(point)
while running:
    # poll for events
    # pg.QUIT event means the user clicked X to close your window
    for event in pg.event.get():
        if event.type == pg.QUIT:
            running = False
        if event.type == pg.MOUSEBUTTONDOWN and selected_point == None:
            if event.button == 1:
                for point in selected_object.get_points():
                    if point.collider.collidepoint((event.pos[0] - viewport_x_offset,
                                                     event.pos[1] - viewport_y_offset)):
                        selected_point = point
                        break
            if event.button == 3:
                selected_object.add_segment_to_point(Curve_point(
                    (event.pos[0] - viewport_x_offset - selected_object.position[0],
                      event.pos[1] - viewport_y_offset - selected_object.position[1])))
                selected_object.update_point_colliders()
        if event.type == pg.MOUSEBUTTONUP:
            if event.button == 1:
                selected_point = None

    if selected_point != None:
        if pg.mouse.get_pos()[0] - viewport_x_offset < 0:
            selected_point.x = 0 - selected_object.position[0]
        elif pg.mouse.get_pos()[0] - viewport_x_offset > editor_viewport.get_width():
            selected_point.x = editor_viewport.get_width() - \
                selected_object.position[0]
        else:
            selected_point.x = pg.mouse.get_pos(
            )[0] - viewport_x_offset - selected_object.position[0]
        if pg.mouse.get_pos()[1] - viewport_y_offset < 0:
            selected_point.y = 0 - selected_object.position[1]
        elif pg.mouse.get_pos()[1] - viewport_y_offset > editor_viewport.get_height():
            selected_point.y = editor_viewport.get_height() - \
                selected_object.position[1]
        else:
            selected_point.y = pg.mouse.get_pos(
            )[1] - viewport_y_offset - selected_object.position[1]
        selected_object.update_point_colliders()

    # fill the screen with a color to wipe away anything from last frame
    screen.fill("grey")
    layer_1.clear()
    editor_viewport.fill((255, 255, 255))
    layer_1.draw()
    editor_viewport.blit(layer_1.surface, (0, 0))
    test_path.draw_controls(editor_viewport)
    screen.blit(editor_viewport, (viewport_x_offset, viewport_y_offset))

    # flip() the display to put your work on screen
    pg.display.flip()

    # limits FPS to 60
    # dt is delta time in seconds since last frame, used for framerate-
    # independent physics.
    dt = clock.tick(60) / 1000

pg.quit()
