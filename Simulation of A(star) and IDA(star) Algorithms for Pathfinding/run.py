import pygame
import sys
import math
import random
import heapq
from collections import deque

WINDOW_WIDTH, WINDOW_HEIGHT = 800, 600
GRID_SIZE = 40
STATUS_WIDTH = 200
BACKGROUND_COLOR = (255, 255, 255)
BARRIER_COLOR = (0, 0, 0)      
TASK_COLOR = (255, 0, 0)    
TEXT_COLOR = (0, 0, 0)
BUTTON_COLOR = (0, 200, 0)
BUTTON_HOVER_COLOR = (0, 255, 0)
BUTTON_TEXT_COLOR = (255, 255, 255)
MOVEMENT_DELAY = 200  

class Environment:
    def __init__(self, width, height, grid_size, num_tasks, num_barriers):
        self.width = width
        self.height = height
        self.grid_size = grid_size
        self.columns = width // grid_size
        self.rows = height // grid_size
        self.task_locations = self.generate_tasks(num_tasks)
        self.barrier_locations = self.generate_random_locations(num_barriers, exclude=set(self.task_locations.keys()))

    def generate_tasks(self, count):
        """Generate task locations with unique task numbers."""
        tasks = {}
        for task_number in range(1, count + 1):
            while True:
                location = (random.randint(0, self.columns - 1), random.randint(0, self.rows - 1))
                if location not in tasks:
                    tasks[location] = task_number
                    break
        return tasks

    def generate_random_locations(self, count, exclude=set()):
        """Generate unique random locations that are not in the exclude set."""
        locations = set()
        while len(locations) < count:
            location = (random.randint(0, self.columns - 1), random.randint(0, self.rows - 1))
            if location not in exclude:
                locations.add(location)
        return locations

    def is_within_bounds(self, x, y):
        """Check if (x, y) is within the grid boundaries."""
        return 0 <= x < self.columns and 0 <= y < self.rows

    def is_barrier(self, x, y):
        """Check if (x, y) is a barrier."""
        return (x, y) in self.barrier_locations

class Agent(pygame.sprite.Sprite):
    def __init__(self, environment, grid_size):
        super().__init__()
        self.image = pygame.Surface((grid_size, grid_size))
        self.image.fill((0, 0, 255))  
        self.rect = self.image.get_rect()
        self.grid_size = grid_size
        self.environment = environment
        self.position = [0, 0]  
        self.rect.topleft = (0, 0)
        self.task_completed = 0
        self.completed_tasks = []
        self.path = [] 
        self.moving = False  
        self.cumulative_cost = 0 

    def move(self):
        """Move the agent along the path."""
        if self.path:
            next_position = self.path.pop(0)
            self.position = list(next_position)
            self.rect.topleft = (self.position[0] * self.grid_size, self.position[1] * self.grid_size)
            self.cumulative_cost += 1  
            self.check_task_completion()
        else:
            self.moving = False  

    def check_task_completion(self):
        """Check if the agent has reached a task location."""
        position_tuple = tuple(self.position)
        if position_tuple in self.environment.task_locations:
            task_number = self.environment.task_locations.pop(position_tuple)
            self.task_completed += 1
            self.completed_tasks.append(task_number)

    def find_nearest_task(self, algorithm="A*"):
        """Find the nearest task using the specified algorithm."""
        nearest_task = None
        shortest_path = None
        for task_position in self.environment.task_locations.keys():
            if algorithm == "A*":
                path = self.a_star_search(task_position)
            elif algorithm == "IDA*":
                path = self.ida_star_search(task_position)
            if path:
                if not shortest_path or len(path) < len(shortest_path):
                    shortest_path = path
                    nearest_task = task_position
        if shortest_path:
            self.path = shortest_path[1:] 
            self.moving = True

    def a_star_search(self, target):
        """A* algorithm to find the shortest path to the target."""
        start = tuple(self.position)
        goal = target
        open_set = []
        heapq.heappush(open_set, (0, start))
        came_from = {}
        g_score = {start: 0}
        f_score = {start: self.heuristic(start, goal)}

        while open_set:
            _, current = heapq.heappop(open_set)

            if current == goal:
                return self.reconstruct_path(came_from, current)

            for neighbor in self.get_neighbors(*current):
                tentative_g_score = g_score[current] + 1
                if neighbor not in g_score or tentative_g_score < g_score[neighbor]:
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g_score
                    f_score[neighbor] = tentative_g_score + self.heuristic(neighbor, goal)
                    heapq.heappush(open_set, (f_score[neighbor], neighbor))
        return None  

    def ida_star_search(self, target):
        """IDA* algorithm to find the shortest path to the target."""
        start = tuple(self.position)
        goal = target

        def search(path, g, threshold):
            """Recursive search function for IDA*."""
            current = path[-1]
            f = g + self.heuristic(current, goal)
            if f > threshold:
                return f  
            if current == goal:
                return "FOUND"  
            min_cost = float('inf')
            for neighbor in self.get_neighbors(*current):
                if neighbor not in path:
                    path.append(neighbor)
                    result = search(path, g + 1, threshold)
                    if result == "FOUND":
                        return "FOUND"
                    if result < min_cost:
                        min_cost = result
                    path.pop()
            return min_cost

        threshold = self.heuristic(start, goal)
        path = [start]

        while True:
            result = search(path, 0, threshold)
            if result == "FOUND":
                return path 
            if result == float('inf'):
                return None 
            threshold = result  

    def heuristic(self, a, b):
        """Manhattan distance heuristic."""
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def reconstruct_path(self, came_from, current):
        """Reconstruct the path from the came_from dictionary."""
        path = []
        while current in came_from:
            path.append(current)
            current = came_from[current]
        path.append(current)
        path.reverse()
        return path

    def get_neighbors(self, x, y):
        """Get walkable neighboring positions."""
        neighbors = []
        directions = [("up", (0, -1)), ("down", (0, 1)), ("left", (-1, 0)), ("right", (1, 0))]
        for _, (dx, dy) in directions:
            nx, ny = x + dx, y + dy
            if self.environment.is_within_bounds(nx, ny) and not self.environment.is_barrier(nx, ny):
                neighbors.append((nx, ny))
        return neighbors

def main():
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH + STATUS_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Pygame AI Grid Simulation")
    clock = pygame.time.Clock()
    font = pygame.font.Font(None, 24)
    environment = Environment(WINDOW_WIDTH, WINDOW_HEIGHT, GRID_SIZE, num_tasks=5, num_barriers=15)
    agent = Agent(environment, GRID_SIZE)
    all_sprites = pygame.sprite.Group()
    all_sprites.add(agent)
    button_width, button_height = 100, 50
    button_x = WINDOW_WIDTH + (STATUS_WIDTH - button_width) // 2
    button_y = WINDOW_HEIGHT // 2 - button_height - 10
    a_star_button_rect = pygame.Rect(button_x, button_y, button_width, button_height)
    ida_star_button_rect = pygame.Rect(button_x, button_y + button_height + 10, button_width, button_height)
    simulation_started = False
    current_algorithm = None

    last_move_time = pygame.time.get_ticks()

  
    running = True
    while running:
        clock.tick(60)  

    
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if not simulation_started and event.type == pygame.MOUSEBUTTONDOWN:
                if a_star_button_rect.collidepoint(event.pos):
                    simulation_started = True
                    current_algorithm = "A*"
                    if environment.task_locations:
                        agent.find_nearest_task(current_algorithm)
                elif ida_star_button_rect.collidepoint(event.pos):
                    simulation_started = True
                    current_algorithm = "IDA*"
                    if environment.task_locations:
                        agent.find_nearest_task(current_algorithm)

    
        screen.fill(BACKGROUND_COLOR)

     
        for x in range(environment.columns):
            for y in range(environment.rows):
                rect = pygame.Rect(x * GRID_SIZE, y * GRID_SIZE, GRID_SIZE, GRID_SIZE)
                pygame.draw.rect(screen, (200, 200, 200), rect, 1)  # Draw grid lines

   
        for (bx, by) in environment.barrier_locations:
            barrier_rect = pygame.Rect(bx * GRID_SIZE, by * GRID_SIZE, GRID_SIZE, GRID_SIZE)
            pygame.draw.rect(screen, BARRIER_COLOR, barrier_rect)

  
        for (tx, ty), task_number in environment.task_locations.items():
            task_rect = pygame.Rect(tx * GRID_SIZE, ty * GRID_SIZE, GRID_SIZE, GRID_SIZE)
            pygame.draw.rect(screen, TASK_COLOR, task_rect)
          
            task_num_surface = font.render(str(task_number), True, (255, 255, 255))
            task_num_rect = task_num_surface.get_rect(center=task_rect.center)
            screen.blit(task_num_surface, task_num_rect)

        all_sprites.draw(screen)

 
        status_x = WINDOW_WIDTH + 10
        task_status_text = f"Tasks Completed: {agent.task_completed}"
        position_text = f"Position: {agent.position}"
        completed_tasks_text = f"Completed Tasks: {agent.completed_tasks}"
        cumulative_cost_text = f"Cumulative Cost: {agent.cumulative_cost}"
        algorithm_text = f"Algorithm: {current_algorithm}"
        status_surface = font.render(task_status_text, True, TEXT_COLOR)
        position_surface = font.render(position_text, True, TEXT_COLOR)
        completed_tasks_surface = font.render(completed_tasks_text, True, TEXT_COLOR)
        cumulative_cost_surface = font.render(cumulative_cost_text, True, TEXT_COLOR)
        algorithm_surface = font.render(algorithm_text, True, TEXT_COLOR)

        screen.blit(status_surface, (status_x, 20))
        screen.blit(position_surface, (status_x, 50))
        screen.blit(completed_tasks_surface, (status_x, 80))
        screen.blit(cumulative_cost_surface, (status_x, 110))
        screen.blit(algorithm_surface, (status_x, 140))

        
        if not simulation_started:
            mouse_pos = pygame.mouse.get_pos()
            
            if a_star_button_rect.collidepoint(mouse_pos):
                a_star_button_color = BUTTON_HOVER_COLOR
            else:
                a_star_button_color = BUTTON_COLOR
            pygame.draw.rect(screen, a_star_button_color, a_star_button_rect)
            a_star_button_text = font.render("A*", True, BUTTON_TEXT_COLOR)
            a_star_text_rect = a_star_button_text.get_rect(center=a_star_button_rect.center)
            screen.blit(a_star_button_text, a_star_text_rect)

            if ida_star_button_rect.collidepoint(mouse_pos):
                ida_star_button_color = BUTTON_HOVER_COLOR
            else:
                ida_star_button_color = BUTTON_COLOR
            pygame.draw.rect(screen, ida_star_button_color, ida_star_button_rect)
            ida_star_button_text = font.render("IDA*", True, BUTTON_TEXT_COLOR)
            ida_star_text_rect = ida_star_button_text.get_rect(center=ida_star_button_rect.center)
            screen.blit(ida_star_button_text, ida_star_text_rect)
        else:
            
            current_time = pygame.time.get_ticks()
            if current_time - last_move_time > MOVEMENT_DELAY:
                if not agent.moving and environment.task_locations:
                    
                    agent.find_nearest_task(current_algorithm)
                elif agent.moving:
                    agent.move()
                last_move_time = current_time


        pygame.draw.line(screen, (0, 0, 0), (WINDOW_WIDTH, 0), (WINDOW_WIDTH, WINDOW_HEIGHT))

     
        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()