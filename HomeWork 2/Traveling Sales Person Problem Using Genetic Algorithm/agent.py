import math
import random
from copy import deepcopy

class TSPAgentGeneticAlgorithm:
    def __init__(self, cities, population_size=100, mutation_rate=0.01, elitism_ratio=0.1, tournament_size=5):
        """
        cities: List of (x, y) tuples representing city positions
        population_size: Number of individuals in each generation
        mutation_rate: Probability of mutation for each gene
        elitism_ratio: Percentage of top individuals to carry over to next generation
        tournament_size: Size of tournament selection pool
        """
        self.cities = cities[:]
        self.N = len(cities)
        self.population_size = population_size
        self.mutation_rate = mutation_rate
        self.elitism_ratio = elitism_ratio
        self.tournament_size = tournament_size
        self.iteration = 0
        
        # Initialize population with random permutations
        self.population = []
        for _ in range(population_size):
            individual = cities[:]
            random.shuffle(individual)
            self.population.append(individual)
        
        # Track best solution
        self.best_individual = None
        self.best_distance = float('inf')
        self.update_best_solution()
    
    def total_distance(self, route):
        """Compute the total distance of the cyclic route"""
        d = 0
        for i in range(len(route)):
            d += math.hypot(route[(i+1) % self.N][0] - route[i][0],
                            route[(i+1) % self.N][1] - route[i][1])
        return d
    
    def fitness(self, individual):
        """Fitness is inverse of distance (higher is better)"""
        return 1 / (self.total_distance(individual) + 1e-6)
    
    def update_best_solution(self):
        """Update the best solution found so far"""
        for individual in self.population:
            dist = self.total_distance(individual)
            if dist < self.best_distance:
                self.best_distance = dist
                self.best_individual = individual[:]
    
    def tournament_selection(self):
        """Select an individual using tournament selection"""
        tournament = random.sample(self.population, self.tournament_size)
        return max(tournament, key=lambda x: self.fitness(x))
    
    def ordered_crossover(self, parent1, parent2):
        """Perform ordered crossover (OX) between two parents"""
        size = len(parent1)
        child = [None] * size
        
        # Choose two random cut points
        a, b = sorted(random.sample(range(size), 2))
        
        # Copy segment from parent1 to child
        child[a:b] = parent1[a:b]
        
        # Fill remaining positions with cities from parent2 in order
        ptr = b
        for city in parent2[b:] + parent2[:b]:
            if city not in child[a:b]:
                if ptr >= size:
                    ptr = 0
                child[ptr] = city
                ptr += 1
        
        return child
    
    def mutate(self, individual):
        """Apply swap mutation to an individual"""
        if random.random() < self.mutation_rate:
            i, j = random.sample(range(self.N), 2)
            individual[i], individual[j] = individual[j], individual[i]
    
    def update(self):
        """Create a new generation"""
        new_population = []
        
        # Elitism: carry over top individuals
        elite_size = int(self.population_size * self.elitism_ratio)
        elite = sorted(self.population, key=lambda x: self.total_distance(x))[:elite_size]
        new_population.extend(elite)
        
        # Generate offspring
        while len(new_population) < self.population_size:
            parent1 = self.tournament_selection()
            parent2 = self.tournament_selection()
            
            # Crossover
            child = self.ordered_crossover(parent1, parent2)
            
            # Mutation
            self.mutate(child)
            
            new_population.append(child)
        
        self.population = new_population
        self.update_best_solution()
        self.iteration += 1
    
    def get_state(self):
        """Return current state of the algorithm"""
        avg_distance = sum(self.total_distance(ind) for ind in self.population) / self.population_size
        return {
            "iteration": self.iteration,
            "best_distance": self.best_distance,
            "avg_distance": avg_distance,
            "current_distance": self.total_distance(self.population[0]),  # Just show first individual
        }
    
    def is_finished(self):
        """Define stopping condition (could be based on iterations)"""
        return self.iteration >= 1000  # Or other stopping condition
