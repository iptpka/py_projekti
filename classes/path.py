import pygame as pg
import classes.curves as curves


class Path:
    def __init__(self, start_segment=None, position=(0, 0)):
        self.segments = [start_segment] if not start_segment is None else []
        self.position = pg.Vector2(position)
        self.first_point = start_segment.start_point() if not start_segment is None else None
        self.last_point = start_segment.end_point() if not start_segment is None else None
        self.closed = False

    def add_segment_to_point(self, point):
        if self.closed:
            return
        if self.last_point is None:
            print("adding segment to point for empty path. Point at: " + str(point.get_position()))
            print("creating first point at: ", self.position)
            self.first_point = curves.CurvePoint((0, 0))
            print("first point created at: ", self.first_point.get_position())
            self.last_point = self.first_point
        distance = self.last_point.get_position().distance_to(point.get_position())
        start = self.last_point
        first_control = curves.CurvePoint(start.get_position().move_towards(point.get_position(), distance/3))
        second_control = curves.CurvePoint(point.get_position().move_towards(start.get_position(), distance/3))
        start.controls[1] = first_control
        point.controls[0] = second_control
        self.segments.append(curves.Curve(start, first_control, second_control, point))
        self.last_point = point
        print("First point: ", self.first_point.get_position(), "Last point:", self.last_point.get_position())

    def close_path(self):
        if not self.first_point is None and not self.last_point is None and not self.closed:
            distance = self.last_point.get_position().distance_to(self.first_point.get_position())
            start = self.last_point
            first_control = curves.CurvePoint(start.get_position().move_towards(self.first_point.get_position(), distance/3))
            second_control = curves.CurvePoint(self.first_point.get_position().move_towards(start.get_position(), distance/3))
            self.segments.append(curves.Curve(start, first_control, second_control, self.first_point))
            self.last_point = self.first_point
            self.closed = True

    def draw(self, surface):
        if len(self.segments) == 0:
            pg.draw.circle(surface, (0, 0, 0), self.position, 5)
        for segment in self.segments:
            segment.draw(surface, self.position)

    def draw_controls(self, surface):
        for segment in self.segments:
            segment.draw_controls(surface, self.position)

    def update_point_colliders(self):
        for segment in self.segments:
            segment.update_point_colliders(self.position)

    def get_points(self):
        if len(self.segments) == 0:
            return [curves.CurvePoint(self.position)]
        points = []
        for segment in self.segments:
            for point in segment.points:
                points.append(point)
        return points

    def draw_bounding_box(self, surface):
        pg.draw.rect(surface, (0, 0, 0), self.large_bounding_box().move(self.position.x, self.position.y), width=1)

    def large_bounding_box(self):
        if len(self.segments) == 0:
            return pg.Rect(-10, -10, 20, 20)
        bounding_box = pg.Rect(self.segments[0].large_bounding_box())
        for segment in self.segments[1:]:
            bounding_box.union_ip(segment.large_bounding_box())
        return bounding_box