# Example file showing a circle moving on screen
import pygame as pg
import pygame.gfxdraw as gfx


#A single point on a curve
class Curve_point:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.collider = pg.Rect(x - 5, y - 5, 10, 10)


#A single curve segment
class Curve:
    def __init__(self, start, first_control, second_control, end, steps=100, color=(0, 0, 0)):
        self.points = [Curve_point(*start), Curve_point(*first_control), Curve_point(*second_control), Curve_point(*end)]
        self.steps = steps
        self.color = color

    def draw(self, surface, x_offset=0, y_offset=0):
        gfx.bezier(surface, [(p.x + x_offset, p.y + y_offset)
                   for p in self.points], self.steps, self.color)

    def draw_controls(self, surface, x_offset=0, y_offset=0):
        pg.draw.line(surface, (0, 0, 0), (self.points[0].x + x_offset, self.points[0].y + y_offset), (self.points[1].x + x_offset, self.points[1].y + y_offset))
        pg.draw.line(surface, (0, 0, 0), (self.points[2].x + x_offset, self.points[2].y + y_offset), (self.points[3].x + x_offset, self.points[3].y + y_offset))
        for point in [self.points[0], self.points[3]]:
            pg.draw.circle(surface, (0, 0, 0), (point.x +
                           x_offset, point.y + y_offset), 5)
        for point in [self.points[1], self.points[2]]:
            pg.draw.circle(surface, (0, 200, 0), (point.x +
                           x_offset, point.y + y_offset), 5)

    def update_point_colliders(self):
        for point in self.points:
            point.collider.center = (point.x, point.y)

    def bounding_box(self):
        x_min = min([p.x for p in self.points])
        x_max = max([p.x for p in self.points])
        y_min = min([p.y for p in self.points])
        y_max = max([p.y for p in self.points])
        return pg.Rect(x_min, y_min, x_max - x_min, y_max - y_min)

    def get_points(self):
        return self.points

#A composite of multiple curves
class Path:
    def __init__(self, start_segment = None, position=(0, 0)):
        self.segments = [start_segment] if not start_segment is None else []
        self.position = position
        
    def draw(self, surface):
        for segment in self.segments:
            segment.draw(surface, self.position[0], self.position[1])

    def draw_controls(self, surface, x_offset=0, y_offset=0):
        for segment in self.segments:
            segment.draw_controls(surface, x_offset, y_offset)

    def update_point_colliders(self):
        for segment in self.segments:
            segment.update_point_colliders()
    
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


#A layer of vector objects
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
editor_viewport = pg.Surface((screen.get_width()*viewport_width_percent, screen.get_height()*viewport_height_percent))
editor_viewport.set_colorkey((0, 255, 255))
viewport_x_offset = screen.get_width() * (1 - viewport_width_percent) / 4
viewport_y_offset = screen.get_height() * (1 - viewport_height_percent) / 2

"""vector_surface = pg.Surface((1280, 720))
vector_surface.set_colorkey((255, 255, 255))"""

layer_1 = Vector_layer(1, 1, editor_viewport)
test_curve = Curve((0, 0), (200, 200), (300, 100), (300, 0), 100, (0, 0, 0))
layer_1.add_object(test_curve)
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
                for point in selected_object.get_points():
                    if point.collider.collidepoint((event.pos[0] - viewport_x_offset, event.pos[1] - viewport_y_offset)):
                        selected_point = point
                        break
            if event.button == 3:
                selected_object.points.append(Curve_point(
                    event.pos[0] - viewport_x_offset, event.pos[1] - viewport_y_offset))
                selected_object.update_point_colliders()
        if event.type == pg.MOUSEBUTTONUP:
            if event.button == 1:
                selected_point = None

    if selected_point != None:
        if pg.mouse.get_pos()[0] - viewport_x_offset < 0:
            selected_point.x = 0
        elif pg.mouse.get_pos()[0] - viewport_x_offset > editor_viewport.get_width():
            selected_point.x = editor_viewport.get_width()
        else:
            selected_point.x = pg.mouse.get_pos()[0] - viewport_x_offset
        if pg.mouse.get_pos()[1] - viewport_y_offset < 0:
            selected_point.y = 0
        elif pg.mouse.get_pos()[1] - viewport_y_offset > editor_viewport.get_height():
            selected_point.y = editor_viewport.get_height()
        else:
            selected_point.y = pg.mouse.get_pos()[1] - viewport_y_offset
        selected_object.update_point_colliders()

    # fill the screen with a color to wipe away anything from last frame
    screen.fill("grey")
    layer_1.clear()
    editor_viewport.fill((255, 255, 255))
    layer_1.draw()
    editor_viewport.blit(layer_1.surface, (0, 0))
    test_curve.draw_controls(editor_viewport)
    screen.blit(editor_viewport, (viewport_x_offset, viewport_y_offset))

    # flip() the display to put your work on screen
    pg.display.flip()

    # limits FPS to 60
    # dt is delta time in seconds since last frame, used for framerate-
    # independent physics.
    dt = clock.tick(60) / 1000

pg.quit()
