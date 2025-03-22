# agent.py
import pygame
from collections import deque

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

    def move(self):
        """Move the agent along the path."""
        if self.path:
            next_position = self.path.pop(0)
            self.position = list(next_position)
            self.rect.topleft = (self.position[0] * self.grid_size, self.position[1] * self.grid_size)
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

    def find_nearest_task(self):
        """Find the nearest task based on the shortest path length using BFS."""
        nearest_task = None
        shortest_path = None
        for task_position in self.environment.task_locations.keys():
            path = self.find_path_to(task_position)
            if path:
                if not shortest_path or len(path) < len(shortest_path):
                    shortest_path = path
                    nearest_task = task_position
        if shortest_path:
            self.path = shortest_path[1:] 
            self.moving = True

    def find_path_to(self, target):
        """Find a path to the target position using BFS."""
        start = tuple(self.position)
        goal = target
        queue = deque()
        queue.append([start])
        visited = set()
        visited.add(start)

        while queue:
            path = queue.popleft()
            x, y = path[-1]

            if (x, y) == goal:
                return path

            neighbors = self.get_neighbors(x, y)
            for neighbor in neighbors:
                if neighbor not in visited:
                    visited.add(neighbor)
                    new_path = list(path)
                    new_path.append(neighbor)
                    queue.append(new_path)
        return None 

    def get_neighbors(self, x, y):
        """Get walkable neighboring positions."""
        neighbors = []
        directions = [("up", (0, -1)), ("down", (0, 1)), ("left", (-1, 0)), ("right", (1, 0))]
        for _, (dx, dy) in directions:
            nx, ny = x + dx, y + dy
            if self.environment.is_within_bounds(nx, ny) and not self.environment.is_barrier(nx, ny):
                neighbors.append((nx, ny))
        return neighbors
