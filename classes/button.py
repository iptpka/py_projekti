import pygame



class Button():
    
    default_colors = {
        'normal': 'white',
        'hover': 'bisque',
        'pressed': 'salmon1',
    }
    
    layers = []
    
    def __init__(self, x, y, width, height, buttonText='Button', onclickFunction=None, onPress=None, colors=None):
        pygame.font.init()
        font = pygame.font.SysFont('Arial', 20)
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.on_click_function = onclickFunction
        self.on_press = onPress
        self.already_pressed = False

        self.fill_colors = Button.default_colors if colors == None else colors
        self.button_surface = pygame.Surface((self.width, self.height))
        self.button_rect = pygame.Rect(self.x, self.y, self.width, self.height)
        self.button_text = font.render(buttonText, True, (20, 20, 20))

    def process_state(self):
        mousePos = pygame.mouse.get_pos()
        self.button_surface.fill(self.fill_colors['normal'])
        if self.button_rect.collidepoint(mousePos):
            self.button_surface.fill(self.fill_colors['hover'])
            if pygame.mouse.get_pressed(num_buttons=3)[0]:
                self.button_surface.fill(self.fill_colors['pressed'])
                if self.on_press:
                    self.on_press_function()
                elif not self.already_pressed:
                    self.on_click_function()
                    self.already_pressed = True
            else:
                self.already_pressed = False

        self.button_surface.blit(self.button_text, [
            self.button_rect.width/2 - self.button_text.get_rect().width/2,
            self.button_rect.height/2 - self.button_text.get_rect().height/2])

