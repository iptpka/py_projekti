import pygame as pg

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