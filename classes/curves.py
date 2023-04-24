import pygame as pg
import pygame.gfxdraw as gfx

# A single point on a curve
class Curve_point:
    def __init__(self, position, is_control=False, controls=None):
        position = pg.math.Vector2(position)
        self.x = position.x
        self.y = position.y
        self.is_control = is_control
        self.collider = pg.Rect(self.x - 5, self.y - 5, 10, 10)
        self.controls = controls if controls != None else [None, None] 

    def get_position(self):
        return pg.Vector2(self.x, self.y)
    
# A single curve segment
class Curve:
    def __init__(self, start, first_control, second_control, end, steps=100, color=(0, 0, 0)):
        start.controls[1] = first_control
        first_control.is_control = True
        second_control.is_control = True
        end.controls[0] = second_control
        self.points = [start, first_control, second_control, end]
        self.steps = steps
        self.color = color

    def draw(self, surface, position):
        gfx.bezier(surface, [(p.x + position.x, p.y + position.y)
                   for p in self.points], self.steps, self.color)

    def draw_controls(self, surface, position):
        pg.draw.line(surface, "darkgray", (self.points[0].x + position.x, self.points[0].y +
                    position.y), (self.points[1].x + position.x, self.points[1].y + position.y))
        pg.draw.line(surface, "darkgray", (self.points[2].x + position.x, self.points[2].y +
                    position.y), (self.points[3].x + position.x, self.points[3].y + position.y))
        for point in self.points:
            if point.x + position.x < 0 or point.x + position.x > surface.get_width() or point.y + position.y < 0 or point.y + position.y > surface.get_height():
                continue
            color = "cadetblue" if point.is_control else "black"
            pg.draw.circle(surface, color, (point.x +
                           position.x, point.y + position.y), 5)

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