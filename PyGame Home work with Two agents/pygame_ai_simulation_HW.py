import pygame
import sys

pygame.init()

WINDOW_WIDTH, WINDOW_HEIGHT = 800, 600
BACKGROUND_COLOR = (255, 255, 255)
AGENT1_COLOR = (0, 128, 255)  
AGENT2_COLOR = (255, 0, 0)   
TEXT_COLOR = (0, 0, 0)

screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Pygame AI Simulation with Two Agents")

clock = pygame.time.Clock()


font = pygame.font.Font(None, 36)


class Agent(pygame.sprite.Sprite):
    def __init__(self, color, x, y, control_scheme):
        super().__init__()
        self.image = pygame.Surface((30, 30))
        self.image.fill(color)
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = x, y
        self.speed = 5
        self.control_scheme = control_scheme  

    def update(self, keys):
        """Update the agent's position based on key input."""
        if self.control_scheme == "arrow_keys":
            if keys[pygame.K_LEFT] and self.rect.left > 0:
                self.rect.x -= self.speed
            if keys[pygame.K_RIGHT] and self.rect.right < WINDOW_WIDTH:
                self.rect.x += self.speed
            if keys[pygame.K_UP] and self.rect.top > 0:
                self.rect.y -= self.speed
            if keys[pygame.K_DOWN] and self.rect.bottom < WINDOW_HEIGHT:
                self.rect.y += self.speed
        
        elif self.control_scheme == "numpad":
            if keys[pygame.K_KP4] and self.rect.left > 0:  
                self.rect.x -= self.speed
            if keys[pygame.K_KP6] and self.rect.right < WINDOW_WIDTH:  
                self.rect.x += self.speed
            if keys[pygame.K_KP8] and self.rect.top > 0:  
                self.rect.y -= self.speed
            if keys[pygame.K_KP2] and self.rect.bottom < WINDOW_HEIGHT:  
                self.rect.y += self.speed


agent1 = Agent(AGENT1_COLOR, 100, 100, "arrow_keys")  
agent2 = Agent(AGENT2_COLOR, 200, 200, "numpad")  

all_sprites = pygame.sprite.Group()
all_sprites.add(agent1)
all_sprites.add(agent2)

running = True
while running:
   
    clock.tick(60)

    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()
    
    all_sprites.update(keys)

    screen.fill(BACKGROUND_COLOR)

    all_sprites.draw(screen)

    frame_text = font.render(f"Frame: {pygame.time.get_ticks() // 1000}", True, TEXT_COLOR)
    screen.blit(frame_text, (10, 10))

    pygame.display.flip()

pygame.quit()
sys.exit()
