import pygame
import sys
import math
import random
import subprocess

# Initialize pygame
pygame.init()

# Screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
LIGHT_GRAY = (230, 230, 230)

# Fonts
FONT = pygame.font.SysFont('Arial', 24)
TITLE_FONT = pygame.font.SysFont('Arial', 48)

class UIManager:
    def __init__(self, screen):
        self.screen = screen
        self.current_screen = None
        self.screens = {}

    def add_screen(self, name, screen):
        self.screens[name] = screen

    def set_screen(self, name):
        self.current_screen = self.screens.get(name)

    def update(self):
        if self.current_screen:
            self.current_screen.update()

    def render(self):
        if self.current_screen:
            self.current_screen.render()

class Screen:
    def __init__(self, ui_manager):
        self.ui_manager = ui_manager
        self.triangles = self.create_triangles()

    def create_triangles(self):
        triangles = []
        for _ in range(10):
            x = random.uniform(0, SCREEN_WIDTH)
            y = random.uniform(0, SCREEN_HEIGHT)
            size = random.uniform(100, 200)
            speed = random.uniform(0.001, 0.01)
            angle = random.uniform(0, 2 * math.pi)
            direction = pygame.math.Vector2(random.uniform(-1, 1), random.uniform(-1, 1)).normalize() * random.uniform(0.1, 0.5)
            triangles.append({'pos': pygame.math.Vector2(x, y), 'size': size, 'angle': angle, 'speed': speed, 'direction': direction})
        return triangles

    def update_triangles(self):
        for triangle in self.triangles:
            triangle['angle'] += triangle['speed']
            triangle['pos'] += triangle['direction']
            if triangle['pos'].x < -triangle['size'] or triangle['pos'].x > SCREEN_WIDTH + triangle['size'] or triangle['pos'].y < -triangle['size'] or triangle['pos'].y > SCREEN_HEIGHT + triangle['size']:
                triangle['pos'] = pygame.math.Vector2(random.uniform(0, SCREEN_WIDTH), random.uniform(0, SCREEN_HEIGHT))

    def draw_triangles(self):
        for triangle in self.triangles:
            points = []
            for i in range(3):
                angle = triangle['angle'] + i * 2 * math.pi / 3
                point = triangle['pos'] + pygame.math.Vector2(math.cos(angle), math.sin(angle)) * triangle['size']
                points.append((point.x, point.y))
            pygame.draw.polygon(self.ui_manager.screen, LIGHT_GRAY, points, width=0)

    def update(self):
        self.update_triangles()

    def render(self):
        self.ui_manager.screen.fill(WHITE)
        self.draw_triangles()

class MainMenu(Screen):
    def __init__(self, ui_manager):
        super().__init__(ui_manager)
        self.buttons = [
            Button("Start Game", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2, self.start_game),
            Button("Tutorial", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 60, self.show_tutorial)
        ]

    def update(self):
        super().update()
        for button in self.buttons:
            button.update()

    def render(self):
        super().render()
        title_surface = TITLE_FONT.render("Main Menu", True, BLACK)
        self.ui_manager.screen.blit(title_surface, (SCREEN_WIDTH // 2 - title_surface.get_width() // 2, 50))
        for button in self.buttons:
            button.render(self.ui_manager.screen)

    def start_game(self):
        self.ui_manager.set_screen('main_game')

    def show_tutorial(self):
        self.ui_manager.set_screen('tutorial')

class Tutorial(Screen):
    def __init__(self, ui_manager):
        super().__init__(ui_manager)
        self.text = "This is the tutorial. Scroll to read more."
        #self.images = [pygame.image.load('example.png')]  # Replace with your own images
        self.scroll_offset = 0
        self.back_button = Button("Back", 60, 30, self.go_back)

    def update(self):
        super().update()
        keys = pygame.key.get_pressed()
        if keys[pygame.K_UP]:
            self.scroll_offset += 5
        if keys[pygame.K_DOWN]:
            self.scroll_offset -= 5
        self.back_button.update()

    def render(self):
        super().render()
        y_offset = self.scroll_offset
        for image in self.images:
            self.ui_manager.screen.blit(image, (50, y_offset))
            y_offset += image.get_height() + 10
        text_surface = FONT.render(self.text, True, BLACK)
        self.ui_manager.screen.blit(text_surface, (50, y_offset))
        self.back_button.render(self.ui_manager.screen)

    def go_back(self):
        self.ui_manager.set_screen('main_menu')

class MainGame(Screen):
    def __init__(self, ui_manager):
        super().__init__(ui_manager)

    def update(self):
        super().update()
        keys = pygame.key.get_pressed()
        if keys[pygame.K_ESCAPE]:
            self.ui_manager.set_screen('main_menu')

    def render(self):
        super().render()
        text_surface = FONT.render("Main Game - Press ESC to return to menu", True, WHITE)
        self.ui_manager.screen.blit(text_surface, (50, SCREEN_HEIGHT // 2))

class Button:
    def __init__(self, text, x, y, action):
        self.text = text
        self.x = x
        self.y = y
        self.action = action
        self.rect = pygame.Rect(x - 100, y - 25, 200, 50)
        self.hovered = False

    def update(self):
        mouse_pos = pygame.mouse.get_pos()
        self.hovered = self.rect.collidepoint(mouse_pos)
        if self.hovered and pygame.mouse.get_pressed()[0]:
            self.action()

    def render(self, screen):
        color = (200, 200, 200) if self.hovered else (100, 100, 100)
        pygame.draw.rect(screen, color, self.rect)
        text_surface = FONT.render(self.text, True, BLACK)
        screen.blit(text_surface, (self.x - text_surface.get_width() // 2, self.y - text_surface.get_height() // 2))

def main():
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption('UI Engine Example')
    ui_manager = UIManager(screen)

    # Create and add screens
    ui_manager.add_screen('main_menu', MainMenu(ui_manager))
    ui_manager.add_screen('tutorial', Tutorial(ui_manager))
    ui_manager.add_screen('main_game', MainGame(ui_manager))

    # Set the initial screen
    ui_manager.set_screen('main_menu')

    clock = pygame.time.Clock()
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        ui_manager.update()
        ui_manager.render()

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
