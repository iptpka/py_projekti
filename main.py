# Example file showing a circle moving on screen
import pygame as pg
from classes.curves import Curve, Curve_point
from classes.path import Path
from classes.vector import Vector_layer


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
    selected_layer = layer_1
    layers = [layer_1]
    for point in selected_object.get_points():
        print(point)

    #state = None

    while running:
        # poll for events
        # pg.QUIT event means the user clicked X to close your window
        for event in pg.event.get():

            if event.type == pg.QUIT:
                running = False
            if event.type == pg.MOUSEBUTTONDOWN and selected_point == None:
                if event.button == 1:
                    selected_object = None
                    for obj in selected_layer.objects:
                        if obj.large_bounding_box().collidepoint((event.pos[0] - viewport_x_offset - obj.position.x,
                                                event.pos[1] - viewport_y_offset - obj.position.y)):
                            selected_object = obj
                            break

                if selected_object != None: 
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
                    if event.button == 3 and selected_object == None:
                        pass
                else:
                    #logic for adding a new path when clicking somewhere with right button with no object selected
                    #FIX THIS
                    if event.button == 3:
                        new_path = (Path(position=(event.pos[0] - viewport_x_offset, event.pos[1] - viewport_y_offset)))
                        selected_layer.add_object(new_path)
                        selected_object = new_path

            if event.type == pg.MOUSEBUTTONUP:
                if event.button == 1:
                    selected_point = None

        if selected_point != None:

            original_x = selected_point.x
            original_y = selected_point.y
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
            
            if not selected_point.is_control:
                if selected_point.controls[0] != None:
                    selected_point.controls[0].x -= original_x - selected_point.x
                    selected_point.controls[0].y -= original_y - selected_point.y
                if selected_point.controls[1] != None:
                    selected_point.controls[1].x -= original_x - selected_point.x
                    selected_point.controls[1].y -= original_y - selected_point.y

            selected_object.update_point_colliders()

        # fill the screen with a color to wipe away anything from last frame
        screen.fill("grey")
        layer_1.clear()
        editor_viewport.fill((255, 255, 255))
        if selected_object != None:
            selected_object.draw_controls(editor_viewport)
        layer_1.draw()
        editor_viewport.blit(layer_1.surface, (0, 0))

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