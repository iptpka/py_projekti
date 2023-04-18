# Example file showing a circle moving on screen
import pygame as pg
import pygame.gfxdraw as gfx


# A single point on a curve
class Curve_point:
    def __init__(self, position, is_control=False):
        position = pg.math.Vector2(position)
        self.x = position.x
        self.y = position.y
        self.is_control = is_control
        self.collider = pg.Rect(self.x - 5, self.y - 5, 10, 10)

    def get_position(self):
        return pg.Vector2(self.x, self.y)


# A single curve segment
class Curve:
    def __init__(self, start, first_control, second_control, end, steps=100, color=(0, 0, 0)):
        first_control.is_control = True
        second_control.is_control = True
        self.points = [start, first_control, second_control, end]
        self.steps = steps
        self.color = color

    def draw(self, surface, position):
        gfx.bezier(surface, [(p.x + position.x, p.y + position.y)
                   for p in self.points], self.steps, self.color)

    def draw_controls(self, surface, offset_position):
        pg.draw.line(surface, "darkgray", (self.points[0].x + offset_position.x, self.points[0].y +
                     offset_position.y), (self.points[1].x + offset_position.x, self.points[1].y + offset_position.y))
        pg.draw.line(surface, "darkgray", (self.points[2].x + offset_position.x, self.points[2].y +
                     offset_position.y), (self.points[3].x + offset_position.x, self.points[3].y + offset_position.y))
        for point in self.points:
            color = "cadetblue" if point.is_control else "black"
            pg.draw.circle(surface, color, (point.x +
                           offset_position.x, point.y + offset_position.y), 5)

    def update_point_colliders(self, offset_position):
        for point in self.points:
            point.collider.center = (
                point.x + offset_position.x, point.y + offset_position.y)

    def bounding_box(self):
        x_min = min([p.x for p in self.points])
        x_max = max([p.x for p in self.points])
        y_min = min([p.y for p in self.points])
        y_max = max([p.y for p in self.points])
        return pg.Rect(x_min, y_min, x_max - x_min, y_max - y_min)

    def get_points(self):
        return self.points
    
    def start_point(self):
        return self.points[0]
    
    def end_point(self):
        return self.points[3]

# A composite of multiple curves


class Path:
    def __init__(self, start_segment=None, position=(0, 0)):
        self.segments = [start_segment] if not start_segment is None else []
        self.position = pg.Vector2(position)
        self.first_point = start_segment.start_point() if not start_segment is None else None
        self.last_point = start_segment.end_point() if not start_segment is None else None

    def add_segment_to_point(self, point):
        if self.last_point is None:
            self.first_point = point
            self.last_point = point
        else:
            distance = self.last_point.get_position().distance_to(point.get_position())
            start = self.last_point
            first_control = Curve_point(start.get_position().move_towards(point.get_position(), distance/3))
            second_control = Curve_point(point.get_position().move_towards(start.get_position(), distance/3))
            self.segments.append(Curve(start, first_control, second_control, point))
            self.last_point = point

    def close_path(self):
        if not self.first_point is None and not self.last_point is None:
            distance = self.last_point.get_position().distance_to(self.first_point.get_position())
            start = self.last_point
            first_control = Curve_point(start.get_position().move_towards(self.first_point.get_position(), distance/3))
            second_control = Curve_point(self.first_point.get_position().move_towards(start.get_position(), distance/3))
            self.segments.append(Curve(start, first_control, second_control, self.first_point))
            self.last_point = self.first_point

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

    def large_bounding_box(self):
        bounding_box = pg.Rect(0, 0, 0, 0)
        for segment in self.segments:
            bounding_box.union_ip(segment.bounding_box())
        return bounding_box.scale_by(1.1)
    


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

def main():
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
                    (150, 0), (150, 300), (300, 300))], 100, (0, 0, 0))
    for point in test_curve.get_points():
        print(point.get_position())
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
                if event.button == 1 and selected_object != None:
                    if not selected_object.large_bounding_box().collidepoint((event.pos[0] - viewport_x_offset - selected_object.position.x,
                                                event.pos[1] - viewport_y_offset - selected_object.position.y)):
                        selected_object = None
                        break
                if event.button == 1 and selected_object == None:
                    for obj in layer_1.objects:
                        if obj.large_bounding_box().collidepoint((event.pos[0] - viewport_x_offset - obj.position.x,
                                                event.pos[1] - viewport_y_offset - obj.position.y)):
                            selected_object = obj
                            break
                if selected_object == None:
                    break
                point_at_mouse = None
                for point in selected_object.get_points():
                    if point.collider.collidepoint((event.pos[0] - viewport_x_offset,
                                                event.pos[1] - viewport_y_offset)):
                        point_at_mouse = point
                if event.button == 1:
                            selected_point = point_at_mouse
                            break
                if event.button == 3:
                    if point_at_mouse != None and point_at_mouse == selected_object.first_point:
                        selected_object.close_path()
                    else:
                        selected_object.add_segment_to_point(Curve_point(
                            (event.pos[0] - viewport_x_offset - selected_object.position.x,
                            event.pos[1] - viewport_y_offset - selected_object.position.y)))
                    selected_object.update_point_colliders()
            if event.type == pg.MOUSEBUTTONUP:
                if event.button == 1:
                    selected_point = None

        if selected_point != None:
            if pg.mouse.get_pos()[0] - viewport_x_offset < 0:
                selected_point.x = 0 - selected_object.position.x
            elif pg.mouse.get_pos()[0] - viewport_x_offset > editor_viewport.get_width():
                selected_point.x = editor_viewport.get_width() - \
                    selected_object.position.x
            else:
                selected_point.x = pg.mouse.get_pos(
                )[0] - viewport_x_offset - selected_object.position.x
            if pg.mouse.get_pos()[1] - viewport_y_offset < 0:
                selected_point.y = 0 - selected_object.position.y
            elif pg.mouse.get_pos()[1] - viewport_y_offset > editor_viewport.get_height():
                selected_point.y = editor_viewport.get_height() - \
                    selected_object.position.y
            else:
                selected_point.y = pg.mouse.get_pos(
                )[1] - viewport_y_offset - selected_object.position.y
            selected_object.update_point_colliders()

        # fill the screen with a color to wipe away anything from last frame
        screen.fill("grey")
        layer_1.clear()
        editor_viewport.fill((255, 255, 255))
        layer_1.draw()
        editor_viewport.blit(layer_1.surface, (0, 0))
        if selected_object != None:
            selected_object.draw_controls(editor_viewport)
        screen.blit(editor_viewport, (viewport_x_offset, viewport_y_offset))
        #pg.draw.rect(screen, (0, 0, 0), selected_object.large_bounding_box().move(viewport_x_offset + selected_object.position.x, viewport_y_offset + selected_object.position.y), width=1)
        # flip() the display to put your work on screen
        pg.display.flip()

        # limits FPS to 60
        # dt is delta time in seconds since last frame, used for framerate-
        # independent physics.
        dt = clock.tick(60) / 1000

    pg.quit()


main()