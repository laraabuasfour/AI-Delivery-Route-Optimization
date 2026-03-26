import math
import random
import copy
from tkinter import messagebox 

class Package:
    def __init__(self, id, x, y, weight, priority):
        self.id = int(id)
        self.x = float(x)
        self.y = float(y)
        self.weight = float(weight)
        self.priority = int(priority)
        self.assigned_vehicle = None 

    def __repr__(self):
        return f"Pkg(ID={self.id}, W={self.weight:.1f}, P={self.priority})"

    def details(self):
         return f"Package(ID={self.id}, Loc=({self.x:.1f},{self.y:.1f}), Weight={self.weight:.1f}, Priority={self.priority})"

class Vehicle:
    def __init__(self, id, maxCapacity):
        self.id = int(id)
        self.maxCapacity = float(maxCapacity)
        self.packages = []

    def current_load(self):
        return sum(p.weight for p in self.packages)

    def can_add_package(self, package):
        return self.current_load() + package.weight <= self.maxCapacity

    def add_package(self, package):
        if self.can_add_package(package):
            self.packages.append(package)
            package.assigned_vehicle = self.id
            return True
        return False

    def remove_package(self, package):
        # Find package by ID to ensure correct object removal if copies exist
        package_to_remove = next((p for p in self.packages if p.id == package.id), None)
        if package_to_remove:
            self.packages.remove(package_to_remove)
            package.assigned_vehicle = None 
            original_pkg_ref = package 
            original_pkg_ref.assigned_vehicle = None
            return True
        return False

    def __repr__(self):
        package_ids = sorted([p.id for p in self.packages])
        return (f"Vehicle(ID={self.id}, Cap={self.maxCapacity:.1f}, "
                f"Load={self.current_load():.1f}, Pkgs={package_ids})")


def load_data(filename, data_type):
    items = []
    try:
        with open(filename, 'r') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                parts = line.split(',')
                try:
                    if data_type == 'package' and len(parts) == 5:
                        id_, x, y, w, priority = parts
                        items.append(Package(int(id_), float(x), float(y), float(w), int(priority)))
                    elif data_type == 'vehicle' and len(parts) == 2:
                        id_, capacity = parts
                        items.append(Vehicle(int(id_), float(capacity)))
                    else:
                        raise ValueError(f"Incorrect number of columns ({len(parts)})")
                except (ValueError, TypeError) as e:
                    messagebox.showerror("Data Loading Error", f"Error in {filename} line {line_num}: {e}\nLine: '{line}'")
                    return None 
    except FileNotFoundError:
        messagebox.showerror("File Error", f"File not found: {filename}")
        return None 
    except Exception as e:
        messagebox.showerror("Error", f"An unexpected error occurred loading {filename}: {e}")
        return None 

    if not items:
        messagebox.showwarning("Data Loading Warning", f"No valid data found in {filename}.")
        return [] 
    
    if data_type == 'package':
        for pkg in items:
            pkg.assigned_vehicle = None
    return items

def euclidean(p1_coords, p2_coords):
    return math.sqrt((p1_coords[0] - p2_coords[0])**2 + (p1_coords[1] - p2_coords[1])**2)

def calculate_vehicle_route_distance(vehicle):
    if not vehicle.packages:
        return 0.0
    shop_location = (0, 0)
    current_location = shop_location
    total_distance = 0.0
    route_packages = vehicle.packages # Use the actual order
    first_package_loc = (route_packages[0].x, route_packages[0].y)
    total_distance += euclidean(current_location, first_package_loc)
    current_location = first_package_loc
    for i in range(len(route_packages) - 1):
        next_package_loc = (route_packages[i+1].x, route_packages[i+1].y)
        total_distance += euclidean(current_location, next_package_loc)
        current_location = next_package_loc
    total_distance += euclidean(current_location, shop_location)
    return total_distance

def calculate_total_cost(vehicles_solution):
     return sum(calculate_vehicle_route_distance(vehicle) for vehicle in vehicles_solution)

def get_skipped_packages(all_packages, vehicles_solution):
    delivered_package_ids = set()
    for v in vehicles_solution:
        for pkg in v.packages:
            delivered_package_ids.add(pkg.id)
    skipped = [pkg for pkg in all_packages if pkg.id not in delivered_package_ids]
    return skipped

def calculate_total_cost_with_penalty(vehicles_solution, all_packages, penalty_per_priority_point=50.0):
    base_cost = calculate_total_cost(vehicles_solution)
    skipped_packages = get_skipped_packages(all_packages, vehicles_solution)
    penalty = sum(penalty_per_priority_point * (6 - pkg.priority) for pkg in skipped_packages)
    return base_cost + penalty

# --- Simulated Annealing ---
def generate_random_initial_solution(packages, base_vehicles):
    vehicles = [Vehicle(v.id, v.maxCapacity) for v in base_vehicles] # Deep copy structure
    packages_to_assign = packages[:]
    random.shuffle(packages_to_assign)
    for pkg in packages_to_assign:
        assigned = False
        vehicle_indices = list(range(len(vehicles)))
        random.shuffle(vehicle_indices)
        for i in vehicle_indices:
            if vehicles[i].add_package(pkg): # add_package now updates pkg.assigned_vehicle
                assigned = True
                break
    return vehicles

def get_sa_neighbor(current_vehicles, all_packages):
    neighbor = [Vehicle(v.id, v.maxCapacity) for v in current_vehicles]
    original_pkg_map = {p.id: p for p in all_packages} # Map ID to original package object

    # Create neighbor package 
    for i, v_orig in enumerate(current_vehicles):
        neighbor[i].packages = [] # Start empty
        for pkg_orig in v_orig.packages:
            # Add original package object reference to neighbor
             neighbor[i].packages.append(original_pkg_map[pkg_orig.id])

    move_type = random.random()

    if move_type < 0.7 and len(neighbor) > 1: # Move package
        non_empty_vehicles = [v for v in neighbor if v.packages]
        if not non_empty_vehicles: return neighbor

        v1_neighbor = random.choice(non_empty_vehicles)
        pkg_to_move_ref = random.choice(v1_neighbor.packages) 

        possible_v2 = [v for v in neighbor if v.id != v1_neighbor.id]
        if not possible_v2: return neighbor

        v2_neighbor = random.choice(possible_v2)

        if v2_neighbor.can_add_package(pkg_to_move_ref):
            if v1_neighbor.remove_package(pkg_to_move_ref):
                 v2_neighbor.add_package(pkg_to_move_ref)

    elif len(neighbor) > 1: # Swap packages
        v1_neighbor, v2_neighbor = random.sample(neighbor, 2)

        if v1_neighbor.packages and v2_neighbor.packages:
            pkg1_ref = random.choice(v1_neighbor.packages)
            pkg2_ref = random.choice(v2_neighbor.packages)

            load1_after_swap = v1_neighbor.current_load() - pkg1_ref.weight + pkg2_ref.weight
            load2_after_swap = v2_neighbor.current_load() - pkg2_ref.weight + pkg1_ref.weight

            if load1_after_swap <= v1_neighbor.maxCapacity and load2_after_swap <= v2_neighbor.maxCapacity:
                 # Perform swap using add/remove on the neighbor vehicles
                 if v1_neighbor.remove_package(pkg1_ref) and v2_neighbor.remove_package(pkg2_ref):
                      v1_neighbor.add_package(pkg2_ref)
                      v2_neighbor.add_package(pkg1_ref)
    return neighbor

def simulated_annealing(all_packages, base_vehicles, initial_temp, cooling_rate, stop_temp, iter_per_temp, progress_callback=None):
    for pkg in all_packages: pkg.assigned_vehicle = None 

    current_solution = generate_random_initial_solution(all_packages, base_vehicles)
    current_cost = calculate_total_cost_with_penalty(current_solution, all_packages)
    # Correct deep copy for best solution
    best_solution = [Vehicle(v.id, v.maxCapacity) for v in current_solution]
    original_pkg_map = {p.id: p for p in all_packages}
    for i, v_curr in enumerate(current_solution):
        best_solution[i].packages = [original_pkg_map[p.id] for p in v_curr.packages]

    best_cost = current_cost
    temperature = initial_temp
    total_iterations = int(math.log(stop_temp / initial_temp) / math.log(cooling_rate)) * iter_per_temp if 0 < cooling_rate < 1 else iter_per_temp
    iter_count = 0

    while temperature > stop_temp:
        for i in range(iter_per_temp):
            iter_count += 1
            # Pass the current solution to get_neighbor
            neighbor_solution = get_sa_neighbor(current_solution, all_packages)
            neighbor_cost = calculate_total_cost_with_penalty(neighbor_solution, all_packages)

            cost_delta = neighbor_cost - current_cost

            if cost_delta < 0 or random.uniform(0, 1) < math.exp(-cost_delta / temperature):
                current_solution = neighbor_solution 
                current_cost = neighbor_cost

                if current_cost < best_cost:
                    # Deep copy the structure and package references for best_solution
                    best_solution = [Vehicle(v.id, v.maxCapacity) for v in current_solution]
                    for j, v_curr in enumerate(current_solution):
                         best_solution[j].packages = [original_pkg_map[p.id] for p in v_curr.packages]
                    best_cost = current_cost

            if progress_callback and iter_count % 50 == 0:
                 progress_callback(iter_count, total_iterations, temperature, best_cost)

        temperature *= cooling_rate
        if temperature <= stop_temp: break
        if cooling_rate >= 1.0 or cooling_rate <= 0:
            print("Warning: Invalid Cooling rate. Stopping SA.")
            break # Prevent infinite loop

    if progress_callback: progress_callback(iter_count, total_iterations, temperature, best_cost)

    return best_solution, best_cost

# --- Genetic Algorithm ---
def generate_ga_individual(all_packages, base_vehicles):
    return generate_random_initial_solution(all_packages, base_vehicles)

def calculate_fitness(individual, all_packages):
    cost = calculate_total_cost_with_penalty(individual, all_packages)
    return 1.0 / (cost + 1e-9)


def select_parents(population_with_fitness, num_parents):
    parents = []
    tournament_size = 3
    population = [ind for fitness, ind in population_with_fitness]
    if not population: return [] # Handle empty population case

    for _ in range(num_parents):
        # Ensure enough contenders for sample size
        actual_tournament_size = min(tournament_size, len(population_with_fitness))
        if actual_tournament_size == 0: continue

        tournament_contenders = random.sample(population_with_fitness, actual_tournament_size)
        tournament_contenders.sort(key=lambda x: x[0], reverse=True)
        parents.append(tournament_contenders[0][1]) # Append the individual

    return parents

def crossover(parent1, parent2, all_packages, base_vehicles):
    child_vehicles = [Vehicle(v.id, v.maxCapacity) for v in base_vehicles]
    num_vehicles = len(base_vehicles)
    original_pkg_map = {p.id: p for p in all_packages}

    # Ensure parents are lists of vehicles
    if not isinstance(parent1, list) or not isinstance(parent2, list):
        print("Error: Crossover parents are not lists.")
        return generate_ga_individual(all_packages, base_vehicles) # Return a random one

    parent1_map = {v.id: v for v in parent1}
    parent2_map = {v.id: v for v in parent2}
    child_map = {v.id: v for v in child_vehicles}

    assigned_package_ids = set()

    for v_base in base_vehicles:
        child_vehicle = child_map[v_base.id]
        chosen_parent_map = parent1_map if random.random() < 0.5 else parent2_map

        parent_vehicle = chosen_parent_map.get(v_base.id) 
        if parent_vehicle:
            for pkg_in_parent in parent_vehicle.packages:
                original_pkg = original_pkg_map.get(pkg_in_parent.id) 
                if original_pkg and original_pkg.id not in assigned_package_ids:
                    if child_vehicle.add_package(original_pkg): 
                        assigned_package_ids.add(original_pkg.id)

    # Re-assign remaining unassigned packages
    unassigned_packages = [p for p in all_packages if p.id not in assigned_package_ids]
    random.shuffle(unassigned_packages)
    for pkg in unassigned_packages:
         vehicle_indices = list(range(len(child_vehicles)))
         random.shuffle(vehicle_indices)
         for i in vehicle_indices:
              if child_vehicles[i].add_package(pkg):
                   assigned_package_ids.add(pkg.id)
                   break

    return child_vehicles


def mutate(individual, all_packages, mutation_rate):
    mutated_individual = [Vehicle(v.id, v.maxCapacity) for v in individual]
    original_pkg_map = {p.id: p for p in all_packages}
    vehicle_map = {v.id: v for v in mutated_individual} # Map for the new structure

    # Populate the new structure with package references from the original individual
    for i, v_orig in enumerate(individual):
         mutated_individual[i].packages = [original_pkg_map[p.id] for p in v_orig.packages]

    # Get all package objects currently in the mutated individual
    packages_in_individual = [p for v in mutated_individual for p in v.packages]

    for pkg_ref in packages_in_individual: # pkg_ref is a reference to an original package
        if random.random() < mutation_rate:
            current_vehicle_id = pkg_ref.assigned_vehicle
            current_vehicle = vehicle_map.get(current_vehicle_id) if current_vehicle_id else None

            possible_target_vehicles = [v for v in mutated_individual if v.id != current_vehicle_id]
            if not possible_target_vehicles: continue

            target_vehicle = random.choice(possible_target_vehicles)

            # Attempt to move using add/remove which updates pkg_ref.assigned_vehicle
            if target_vehicle.can_add_package(pkg_ref):
                moved = False
                if current_vehicle:
                    if current_vehicle.remove_package(pkg_ref):
                        moved = target_vehicle.add_package(pkg_ref)
                else: 
                    moved = target_vehicle.add_package(pkg_ref)

    current_assigned_ids = {p.id for v in mutated_individual for p in v.packages}
    unassigned_originals = [p for p in all_packages if p.id not in current_assigned_ids]
    if unassigned_originals:
        random.shuffle(unassigned_originals)
        for pkg in unassigned_originals:
            vehicle_indices = list(range(len(mutated_individual)))
            random.shuffle(vehicle_indices)
            for i in vehicle_indices:
                if mutated_individual[i].add_package(pkg):
                    break

    return mutated_individual

def genetic_algorithm(all_packages, base_vehicles, pop_size, generations, mutation_rate, progress_callback=None):
    for pkg in all_packages: pkg.assigned_vehicle = None # Reset assignments

    population = [generate_ga_individual(all_packages, base_vehicles) for _ in range(pop_size)]
    best_solution_structure = None # Holds the best Vehicle list structure
    best_fitness = -1.0
    original_pkg_map = {p.id: p for p in all_packages}

    for gen in range(generations):
        population_with_fitness = []
        for individual in population:
             fitness = calculate_fitness(individual, all_packages)
             population_with_fitness.append((fitness, individual))

        if not population_with_fitness: 
             print("Error: Population became empty during GA.")
             break

        population_with_fitness.sort(key=lambda x: x[0], reverse=True)

        current_best_fitness, current_best_individual = population_with_fitness[0]
        if current_best_fitness > best_fitness:
            best_fitness = current_best_fitness
            best_solution_structure = [Vehicle(v.id, v.maxCapacity) for v in current_best_individual]
            for i, v_curr in enumerate(current_best_individual):
                 best_solution_structure[i].packages = [original_pkg_map[p.id] for p in v_curr.packages] 

        # Selection
        num_elite = 1 # Keep the best one
        next_generation = []
        if best_solution_structure: 
            elite_copy = [Vehicle(v.id, v.maxCapacity) for v in best_solution_structure]
            for i, v_best in enumerate(best_solution_structure):
                elite_copy[i].packages = [original_pkg_map[p.id] for p in v_best.packages]
            next_generation.append(elite_copy)

        parents = select_parents(population_with_fitness, pop_size - num_elite)
        if not parents: # Handle case where selection fails
             while len(next_generation) < pop_size:
                  next_generation.append(generate_ga_individual(all_packages, base_vehicles))
        else:
             while len(next_generation) < pop_size:
                  parent1, parent2 = random.sample(parents, 2)
                  child = crossover(parent1, parent2, all_packages, base_vehicles)
                  mutated_child = mutate(child, all_packages, mutation_rate)
                  next_generation.append(mutated_child)

        population = next_generation

        current_best_cost = calculate_total_cost_with_penalty(best_solution_structure if best_solution_structure else [], all_packages)

        if progress_callback:
             progress_callback(gen + 1, generations, current_best_cost)

    if best_solution_structure is None:
         print("Warning: GA finished without finding a valid solution structure.")
         return [], float('inf')

    final_best_cost = calculate_total_cost_with_penalty(best_solution_structure, all_packages)
    return best_solution_structure, final_best_cost