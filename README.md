# AI-Delivery-Route-Optimization

This project was developed for the **Artificial Intelligence course (ENCS3340)** at **Birzeit University**.

## Project Overview

The goal of this project is to optimize delivery routes for a small package delivery shop.

Each package has:
- location coordinates (x, y)
- weight
- priority level

Each vehicle has a limited capacity.

The objective is to assign packages to vehicles and determine delivery routes that **minimize the total travel distance** while considering package priorities.

## Algorithms Implemented

### Simulated Annealing (SA)
- Explores neighboring solutions
- Accepts worse solutions probabilistically
- Uses temperature cooling schedule

### Genetic Algorithm (GA)
- Population-based optimization
- Tournament selection
- Crossover and mutation operators
- Elitism for best solution preservation

## Features

- Package assignment optimization
- Route cost calculation using Euclidean distance
- Priority-based penalty system
- Graphical user interface using Tkinter
- Visualization of delivery routes

## Technologies Used

- Python
- Simulated Annealing
- Genetic Algorithm
- Tkinter GUI
- Matplotlib (for visualization)
