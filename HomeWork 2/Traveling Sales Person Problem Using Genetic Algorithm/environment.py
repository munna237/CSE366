import random

class TSPEnvironment:
    def __init__(self, width, height, num_cities=20):
        """
        Initializes the TSP environment.
         - width, height: Dimensions of the simulation area.
         - num_cities: Number of cities to generate.
        """
        self.width = width
        self.height = height
        self.num_cities = num_cities
        self.cities = self.generate_cities()

    def generate_cities(self):
        """Generate random city coordinates within screen margins."""
        cities = []
        margin = 50
        for _ in range(self.num_cities):
            x = random.randint(margin, self.width - margin)
            y = random.randint(margin, self.height - margin)
            cities.append((x, y))
        return cities
