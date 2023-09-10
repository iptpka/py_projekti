# Example file showing a circle moving on screen
import pygame as pg
from classes.curves import Curve, CurvePoint
from classes.path import Path
from classes.vector import VectorLayer
from classes.button import Button

global editing
editing = True
global moving
moving = False

def move_point(point, object, viewport, x_offset, y_offset, position):
    original_x = point.x
    original_y = point.y
    if position.x - x_offset < 0:
        point.x = 0 - object.position.x
    elif position.x - x_offset > viewport.get_width():
        point.x = viewport.get_width() - object.position.x
    else:
        point.x = position.x - x_offset - object.position.x
    if position.y - y_offset < 0:
        point.y = 0 - object.position.y
    elif position.y - y_offset > viewport.get_height():
        point.y = viewport.get_height() - object.position.y
    else:
        point.y = position.y - y_offset - object.position.y
    
    #keep controls in place relative to point
    if not point.is_control:
        if point.controls[0] != None:
            point.controls[0].x -= original_x - point.x
            point.controls[0].y -= original_y - point.y
        if point.controls[1] != None:
            point.controls[1].x -= original_x - point.x
            point.controls[1].y -= original_y - point.y

    object.update_point_colliders()


def move_object(object, viewport, x_offset, y_offset, position):
    object.position.x = position.x - x_offset - object.large_bounding_box().width/2
    object.position.y = position.y - y_offset - object.large_bounding_box().height/2
    object.update_point_colliders()


def get_object_at_point(point, layer, previous_object):
    selected_object = None
    for obj in layer.objects:
        if obj.large_bounding_box().collidepoint((point.x - obj.position.x, point.y - obj.position.y)):
            if obj == previous_object:
                selected_object = previous_object
            if obj != previous_object:
                return obj
    return selected_object


def get_curve_point_at_point(point, object):
    for curve_point in object.get_points():
        if curve_point.collider.collidepoint((point.x, point.y)):
            return curve_point
    return None


def draw_drop_shadow(surface, object, color, offset, width=4):
    pg.draw.line(surface, color,
                     (offset.x + object.get_width() + width/3, offset.y + width),
                     (offset.x + object.get_width() + width/3, offset.y + object.get_height() + width -1), width)
    pg.draw.line(surface, color,
                     (offset.x + width, offset.y + object.get_height() + width/2 -1),
                     (offset.x + object.get_width() + width/2, offset.y + object.get_height() + width/2 -1), width)

def set_editing():
    global editing
    global moving
    editing = True
    moving = False

def set_moving():
    global moving
    global editing
    moving = True
    editing = False

def main():
    # pyg setup
    pg.init()
    
    screen = pg.display.set_mode((1280, 976))
    clock = pg.time.Clock()
    running = True
    
    colors = {
        'background': 'mistyrose2',
        'viewport': 'white',
        'drop_shadow': 'skyblue2'
    }
    
    viewport_width_percent = 0.9
    viewport_height_percent = 0.8
    editor_viewport = pg.Surface((screen.get_width()*viewport_width_percent,
                                  screen.get_height()*viewport_height_percent))
    editor_viewport.set_colorkey((0, 255, 255))
    viewport_x_offset = screen.get_width() * (1 - viewport_width_percent) / 2
    viewport_y_offset = screen.get_height() * (1 - viewport_height_percent) / 6

    layers = []
    layer1 = VectorLayer(1, 1, editor_viewport)
    layers.append(layer1)

    test_curve = Curve(*[CurvePoint(position) for position in ((0, 0),
                    (150, 0), (150, 300), (300, 300))], 20, (0, 0, 0))

    test_path = Path(test_curve, (100, 100))
    
    layer1.add_object(test_path)
    selected_object = test_path
    selected_point = None
    selected_object.update_point_colliders()
    selected_layer = layer1
 

    Button.layers = layers
    buttons = []
    button_width = 100
    button_height = 50
    button_margin = 10
    buttons.append(Button(viewport_x_offset, editor_viewport.get_height() + viewport_y_offset*2, button_width, button_height, 'clear', lambda: layer1.objects.clear()))
    buttons.append(Button(viewport_x_offset + button_width + button_margin, editor_viewport.get_height() + viewport_y_offset*2, button_width, button_height, 'move', lambda: set_moving()))
    buttons.append(Button(viewport_x_offset + button_width*2 + button_margin*2, editor_viewport.get_height() + viewport_y_offset*2, button_width, button_height, 'edit', lambda: set_editing()))

    while running:
        
        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False
                return
            if event.type == pg.MOUSEBUTTONUP:
                if event.button == 1:
                    selected_point = None
                break
            if event.type == pg.MOUSEBUTTONDOWN and selected_point == None:
                viewport_event_position = pg.Vector2(event.pos[0] - viewport_x_offset, event.pos[1] - viewport_y_offset)
                if viewport_event_position.x < 0 or viewport_event_position.x > editor_viewport.get_width() or viewport_event_position.y < 0 or viewport_event_position.y > editor_viewport.get_height():
                    break
                if selected_object != None and editing: 
                    point_at_mouse = get_curve_point_at_point(viewport_event_position, selected_object)
                    if event.button == 1: 
                        selected_point = point_at_mouse
                    elif event.button == 3:
                        #adding a new curve segment to current path when clicking somewhere with right button
                        if point_at_mouse != None and selected_object.first_point == None:
                            break
                        if point_at_mouse != None and point_at_mouse == selected_object.first_point:
                            selected_object.close_path()
                        else:
                            selected_object.add_segment_to_point(CurvePoint(
                                (viewport_event_position.x - selected_object.position.x,
                                viewport_event_position.y - selected_object.position.y)))
                        selected_object.update_point_colliders()
                else:
                    #adding a new path when clicking somewhere with right button with no object selected
                    if event.button == 3:
                        set_editing()
                        new_path = (Path(position=viewport_event_position))
                        selected_layer.add_object(new_path)
                        selected_object = new_path
                if event.button == 1 and selected_point == None:
                    selected_object = get_object_at_point(viewport_event_position, selected_layer, selected_object)
                if selected_object != None and moving:
                    move_object(selected_object, editor_viewport, viewport_x_offset, viewport_y_offset, pg.Vector2(pg.mouse.get_pos()))
        if selected_point != None and editing:
            #moving a point to the mouse position
            move_point(selected_point, selected_object, editor_viewport, viewport_x_offset, viewport_y_offset, pg.Vector2(pg.mouse.get_pos()))

        screen.fill(colors['background'])
        layer1.clear()
        editor_viewport.fill(colors['viewport'])



        for layer in layers:
            layer.draw()

        editor_viewport.blit(layer1.surface, (0, 0))
        
        if selected_object != None and editing:
            selected_object.draw_controls(editor_viewport)
            #selected_object.draw_bounding_box(editor_viewport)
        
        if selected_object != None and moving:
            selected_object.draw_bounding_box(editor_viewport)
            
        screen.blit(editor_viewport, (viewport_x_offset, viewport_y_offset))
        
        for button in buttons:
            button.process_state()
            screen.blit(button.button_surface, (button.x, button.y))
            draw_drop_shadow(screen, button.button_surface, colors['drop_shadow'], pg.Vector2(button.x, button.y), 8)

        draw_drop_shadow(screen, editor_viewport, colors['drop_shadow'], pg.Vector2(viewport_x_offset, viewport_y_offset), 10)

        # flip() the display to put your work on screen
        pg.display.flip()

        # limits FPS to 60
        # dt is delta time in seconds since last frame, used for framerate-
        # independent physics.
        clock.tick(60) / 1000

    pg.quit()


main()