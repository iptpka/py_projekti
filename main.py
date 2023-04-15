# Example file showing a circle moving on screen
import pygame as pg
import pygame.gfxdraw as gfx

class curve:
    def __init__(self, points, steps = 100, color = (0, 0, 0)):
        self.points = points
        self.steps = steps
        self.color = color

    def draw(self, surface):
        gfx.bezier(surface, self.points, self.steps, self.color)
        


    


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
test_curve = curve([(0, 0), (200, 200), (300, 100), (400, 200)], 100, (0, 0, 0))

player_pos = pg.Vector2(editor_viewport.get_width() / 2, editor_viewport.get_height() / 2)

while running:
    # poll for events
    # pg.QUIT event means the user clicked X to close your window
    for event in pg.event.get():
        if event.type == pg.QUIT:
            running = False

    # fill the screen with a color to wipe away anything from last frame
    screen.fill("grey")
    vector_surface.fill((255, 255, 255))
    editor_viewport.fill((255, 255, 255))
    test_curve.draw(vector_surface)
    editor_viewport.blit(vector_surface, player_pos)
    screen.blit(editor_viewport, (viewport_x_offset, viewport_y_offset))


    keys = pg.key.get_pressed()
    if keys[pg.K_w]:
        player_pos.y -= 300 * dt
    if keys[pg.K_s]:
        player_pos.y += 300 * dt
    if keys[pg.K_a]:
        player_pos.x -= 300 * dt
    if keys[pg.K_d]:
        player_pos.x += 300 * dt
    
    # flip() the display to put your work on screen
    pg.display.flip()

    # limits FPS to 60
    # dt is delta time in seconds since last frame, used for framerate-
    # independent physics.
    dt = clock.tick(60) / 1000

pg.quit()




