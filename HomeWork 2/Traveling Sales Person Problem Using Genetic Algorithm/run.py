import pygame
import math
from agent import TSPAgentGeneticAlgorithm 
from environment import TSPEnvironment

pygame.init()

# Window dimensions
sim_width = 600          # Left area (for SA process and tour simulation)
panel_width = 300        # Right panel (for SA metrics & description)
height = 600
total_width = sim_width + panel_width

screen = pygame.display.set_mode((total_width, height))
pygame.display.set_caption("TSP Simulation with Simulated Annealing")
clock = pygame.time.Clock()
font = pygame.font.SysFont("Arial", 16)

# Create TSP environment and GA agent
env = TSPEnvironment(sim_width, height, num_cities=25)
ga_agent = TSPAgentGeneticAlgorithm(env.cities, population_size=10000)

# Simulation control flags
simulate = False           # Flag to run SA process
vehicle_simulation_started = False  # Flag to animate final tour
generation = 0

# Define maximum iterations (for example, we run until SA is finished)
# In this simulation, SA runs until temperature falls below threshold.

# Buttons (for top area: "Solve TSP", and bottom area: "Start Simulation")
button_rect = pygame.Rect(10, 10, 150, 40)      # "Solve TSP" button
button_color = (0, 128, 255)
button_sim_rect = pygame.Rect(10, 410, 150, 40)   # "Start Simulation" button

# Layout: left side divided into Top (SA Process) and Bottom (Tour Animation)
top_area_height = 400
bottom_area_height = height - top_area_height

# TSP Vehicle: simulates the traveling salesman moving along the best route
class TSPVehicle:
    def __init__(self, route, speed=2.0):
        """
        route: List of cities representing the best TSP tour.
        speed: Pixels per frame.
        """
        self.route = route
        self.speed = speed
        self.current_index = 0  # current segment index
        self.position = route[0]
        self.finished = False
        self.segment_progress = 0.0

    def update(self):
        if self.finished:
            return
        if self.current_index >= len(self.route) - 1:
            self.finished = True
            return
        start = self.route[self.current_index]
        end = self.route[self.current_index + 1]
        dx = end[0] - start[0]
        dy = end[1] - start[1]
        seg_length = math.hypot(dx, dy)
        if seg_length == 0:
            self.current_index += 1
            self.segment_progress = 0.0
            return
        self.segment_progress += self.speed
        if self.segment_progress >= seg_length:
            self.current_index += 1
            self.segment_progress = 0.0
            if self.current_index >= len(self.route) - 1:
                self.position = end
                self.finished = True
                return
            start = self.route[self.current_index]
            end = self.route[self.current_index + 1]
            dx = end[0] - start[0]
            dy = end[1] - start[1]
            seg_length = math.hypot(dx, dy)
        t = self.segment_progress / seg_length
        new_x = start[0] + dx * t
        new_y = start[1] + dy * t
        self.position = (new_x, new_y)

# We'll use the same colors for TSP: use a single color (white) for the tour and vehicle.
tsp_color = (255, 255, 255)
vehicle = None

# Base explanation text for the right panel with fitness calculation details.
base_explanation = [
    "Traveling Salesman Problem (TSP)",
    "--------------------------------",
    "Description:",
    "Find the shortest possible route that",
    "visits each city exactly once and returns",
    "to the origin.",
    "",
    "Genetic Algorithm Approach:",
    "1. Initialize population of random tours",
    "2. Select parents using tournament selection",
    "3. Create offspring using ordered crossover",
    "4. Apply swap mutation with small probability",
    "5. Keep best solutions (elitism)",
    "",
    "Fitness Function Calculation:",
    "  - Total Distance: Sum of distances between",
    "    consecutive cities (cyclic).",
    "  - Fitness = 1 / (Total Distance + 1e-6)",
    "    (Higher fitness means a shorter tour.)",
    "",
    "GA Metrics:",
    "Iteration, Best Distance, Avg Distance",
]

# Helper functions for coordinate transformation
def compute_scale_offsets(area_width, area_height, env_width, env_height):
    scale = min(area_width / env_width, area_height / env_height)
    offset_x = (area_width - (env_width * scale)) / 2
    return scale, offset_x

def transform_point(point, offset_y, area_width, area_height):
    scale, offset_x = compute_scale_offsets(area_width, area_height, sim_width, height)
    x, y = point
    new_x = offset_x + x * scale
    new_y = offset_y + y * scale
    return (int(new_x), int(new_y))

running = True
while running:
    clock.tick(60)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            # "Solve TSP" button in top area: start SA process
            if event.button == 1 and button_rect.collidepoint(event.pos) and not simulate:
                simulate = True
                generation = 0
                vehicle = None
            # "Start Simulation" button in bottom area (after SA completes)
            if event.button == 1 and button_sim_rect.collidepoint(event.pos) and vehicle and not vehicle_simulation_started:
                vehicle_simulation_started = True

    # Run SA process if simulation is active and SA is not finished
    if simulate and not sa_agent.is_finished():
        sa_agent.update()
        generation += 1
    elif simulate and sa_agent.is_finished():
        simulate = False
        # Create a vehicle to animate the final tour (make tour cyclic)
        final_route = sa_agent.best_route[:] + [sa_agent.best_route[0]]
        vehicle = TSPVehicle(final_route, speed=2.0)

    # Update vehicle if simulation has started
    if vehicle and vehicle_simulation_started:
        vehicle.update()

    # Clear screen
    screen.fill((0, 0, 0))
    # Draw divider between simulation area (left) and right panel
    pygame.draw.line(screen, (100, 100, 100), (sim_width, 0), (sim_width, height), 2)

    # --- Draw Top Area (SA Process Visualization) ---
    top_area_rect = pygame.Rect(0, 0, sim_width, top_area_height)
    pygame.draw.rect(screen, (30, 30, 30), top_area_rect)
    # Draw cities in top area
    for city in env.cities:
        pygame.draw.circle(screen, (255, 0, 0), city, 6)
    # Draw current SA tour (cyclic) in top area (using best route so far)
    current_route = sa_agent.current_route[:] + [sa_agent.current_route[0]]
    for i in range(len(current_route) - 1):
        pygame.draw.line(screen, tsp_color, current_route[i], current_route[i+1], 2)
    # Draw "Solve TSP" button if SA hasn't started
    if not simulate and vehicle is None:
        pygame.draw.rect(screen, button_color, button_rect)
        btn_text = font.render("Solve TSP", True, (255,255,255))
        screen.blit(btn_text, (button_rect.x+10, button_rect.y+10))

    # --- Draw Bottom Area (Tour Simulation) ---
    bottom_area_rect = pygame.Rect(0, top_area_height, sim_width, bottom_area_height)
    pygame.draw.rect(screen, (20, 20, 20), bottom_area_rect)
    # Draw cities in bottom area
    for city in env.cities:
        pygame.draw.circle(screen, (255, 0, 0), city, 6)
    # Draw final tour if available
    if vehicle:
        final_route = sa_agent.best_route[:] + [sa_agent.best_route[0]]
        for i in range(len(final_route) - 1):
            pygame.draw.line(screen, tsp_color, final_route[i], final_route[i+1], 2)
        # Draw the moving salesman (vehicle)
        pygame.draw.circle(screen, tsp_color, (int(vehicle.position[0]), int(vehicle.position[1])), 8)
        # Show "Start Simulation" button if simulation hasn't begun
        if not vehicle_simulation_started:
            pygame.draw.rect(screen, button_color, button_sim_rect)
            sim_btn_text = font.render("Start Simulation", True, (255,255,255))
            screen.blit(sim_btn_text, (button_sim_rect.x+10, button_sim_rect.y+10))

    # --- Draw Right Panel (GA Metrics & Explanation) ---
    panel_rect = pygame.Rect(sim_width, 0, panel_width, height)
    pygame.draw.rect(screen, (50, 50, 50), panel_rect)
    # Prepare explanation text with GA metrics
    state = sa_agent.get_state()
    explanation_lines = base_explanation[:] + [
    "",
    f"Iteration: {state['iteration']}",
    f"Best Dist: {state['best_distance']:.2f}",
    f"Avg Dist: {state['avg_distance']:.2f}",
    f"Current Dist: {state['current_distance']:.2f}"
    ]
    y_offset = 10
    for line in explanation_lines:
        txt = font.render(line, True, (255, 255, 255))
        screen.blit(txt, (sim_width + 10, y_offset))
        y_offset += 20

    pygame.display.flip()

pygame.quit()
