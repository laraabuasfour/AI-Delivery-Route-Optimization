import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext, Canvas
import project as core # Import the logic module
import copy
import math 

class DeliveryOptimizerApp:
    def __init__(self, master):
        self.master = master
        master.title("Package Delivery Optimizer (ENCS3340 Project#1)")
        master.geometry("950x700")

        self.packages = [] # Will hold package objects loaded via core.load_data
        self.vehicles = [] # Will hold vehicle objects loaded via core.load_data
        self.all_packages_original = [] # Keep original list loaded

        # --- Styling ---
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("TLabel", padding=5, font=('Helvetica', 10))
        style.configure("TButton", padding=5, font=('Helvetica', 10, 'bold'))
        style.configure("TRadiobutton", padding=5, font=('Helvetica', 10))
        style.configure("TEntry", padding=5, font=('Helvetica', 10))
        style.configure("TFrame", padding=10)
        style.configure("Input.TFrame", relief="groove", borderwidth=2)
        style.configure("Output.TFrame", relief="groove", borderwidth=2)


        # --- Main Layout Frames ---
        input_frame = ttk.Frame(master, style="Input.TFrame")
        input_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        output_frame = ttk.Frame(master, style="Output.TFrame")
        output_frame.grid(row=0, column=1, rowspan=2, padx=10, pady=10, sticky="nsew")
        progress_frame = ttk.Frame(master)
        progress_frame.grid(row=1, column=0, padx=10, pady=5, sticky="nsew")
        master.grid_columnconfigure(0, weight=1)
        master.grid_columnconfigure(1, weight=3)
        master.grid_rowconfigure(0, weight=1)
        master.grid_rowconfigure(1, weight=0)


        # --- Input Frame Widgets ---
        ttk.Label(input_frame, text="Input Data", font=('Helvetica', 12, 'bold')).grid(row=0, column=0, columnspan=3, pady=(0,10))
        self.pkg_file_var = tk.StringVar(value="package.txt")
        self.veh_file_var = tk.StringVar(value="vehicle.txt")
        ttk.Label(input_frame, text="Packages File:").grid(row=1, column=0, sticky="w")
        ttk.Entry(input_frame, textvariable=self.pkg_file_var, width=20).grid(row=1, column=1, sticky="ew")
        ttk.Button(input_frame, text="Browse...", command=lambda: self.browse_file(self.pkg_file_var)).grid(row=1, column=2, padx=(5,0))
        ttk.Label(input_frame, text="Vehicles File:").grid(row=2, column=0, sticky="w")
        ttk.Entry(input_frame, textvariable=self.veh_file_var, width=20).grid(row=2, column=1, sticky="ew")
        ttk.Button(input_frame, text="Browse...", command=lambda: self.browse_file(self.veh_file_var)).grid(row=2, column=2, padx=(5,0))
        self.load_button = ttk.Button(input_frame, text="Load Data", command=self.load_data_from_gui)
        self.load_button.grid(row=3, column=0, columnspan=3, pady=10)
        self.data_status_label = ttk.Label(input_frame, text="Status: No data loaded")
        self.data_status_label.grid(row=4, column=0, columnspan=3)
        ttk.Label(input_frame, text="Algorithm", font=('Helvetica', 11, 'bold')).grid(row=5, column=0, columnspan=3, pady=(15, 5))
        self.algo_var = tk.StringVar(value="SA")
        sa_radio = ttk.Radiobutton(input_frame, text="Simulated Annealing", variable=self.algo_var, value="SA", command=self.toggle_parameters)
        ga_radio = ttk.Radiobutton(input_frame, text="Genetic Algorithm", variable=self.algo_var, value="GA", command=self.toggle_parameters)
        sa_radio.grid(row=6, column=0, columnspan=2, sticky="w")
        ga_radio.grid(row=7, column=0, columnspan=2, sticky="w")
        self.sa_params_frame = ttk.Frame(input_frame)
        self.ga_params_frame = ttk.Frame(input_frame)
        # SA Parameters
        ttk.Label(self.sa_params_frame, text="SA Parameters:", font=('Helvetica', 10, 'bold')).grid(row=0, column=0, columnspan=2, sticky="w", pady=(5,2))
        self.sa_temp_var = tk.StringVar(value="1000"); self.sa_cool_var = tk.StringVar(value="0.95"); self.sa_stop_var = tk.StringVar(value="1"); self.sa_iter_var = tk.StringVar(value="100")
        ttk.Label(self.sa_params_frame, text="Initial Temp:").grid(row=1, column=0, sticky="w"); ttk.Entry(self.sa_params_frame, textvariable=self.sa_temp_var, width=8, state='readonly').grid(row=1, column=1, sticky="w")
        ttk.Label(self.sa_params_frame, text="Cooling Rate:").grid(row=2, column=0, sticky="w"); self.sa_cool_entry = ttk.Entry(self.sa_params_frame, textvariable=self.sa_cool_var, width=8); self.sa_cool_entry.grid(row=2, column=1, sticky="w")
        ttk.Label(self.sa_params_frame, text="Stop Temp:").grid(row=3, column=0, sticky="w"); ttk.Entry(self.sa_params_frame, textvariable=self.sa_stop_var, width=8, state='readonly').grid(row=3, column=1, sticky="w")
        ttk.Label(self.sa_params_frame, text="Iterations/Temp:").grid(row=4, column=0, sticky="w"); ttk.Entry(self.sa_params_frame, textvariable=self.sa_iter_var, width=8, state='readonly').grid(row=4, column=1, sticky="w")
        # GA Parameters
        ttk.Label(self.ga_params_frame, text="GA Parameters:", font=('Helvetica', 10, 'bold')).grid(row=0, column=0, columnspan=2, sticky="w", pady=(5,2))
        self.ga_pop_var = tk.StringVar(value="75"); self.ga_mut_var = tk.StringVar(value="0.05"); self.ga_gen_var = tk.StringVar(value="500")
        ttk.Label(self.ga_params_frame, text="Population Size:").grid(row=1, column=0, sticky="w"); self.ga_pop_entry = ttk.Entry(self.ga_params_frame, textvariable=self.ga_pop_var, width=8); self.ga_pop_entry.grid(row=1, column=1, sticky="w")
        ttk.Label(self.ga_params_frame, text="Mutation Rate:").grid(row=2, column=0, sticky="w"); self.ga_mut_entry = ttk.Entry(self.ga_params_frame, textvariable=self.ga_mut_var, width=8); self.ga_mut_entry.grid(row=2, column=1, sticky="w")
        ttk.Label(self.ga_params_frame, text="Generations:").grid(row=3, column=0, sticky="w"); ttk.Entry(self.ga_params_frame, textvariable=self.ga_gen_var, width=8, state='readonly').grid(row=3, column=1, sticky="w")
        self.sa_params_frame.grid(row=8, column=0, columnspan=3, sticky="ew", pady=5)
        self.ga_params_frame.grid(row=8, column=0, columnspan=3, sticky="ew", pady=5)
        self.toggle_parameters()
        self.run_button = ttk.Button(input_frame, text="Run Optimization", command=self.run_optimization, state='disabled')
        self.run_button.grid(row=9, column=0, columnspan=3, pady=(15, 5))

        # --- Progress Frame Widgets ---
        self.progress_label = ttk.Label(progress_frame, text="Progress:")
        self.progress_label.grid(row=0, column=0, sticky="w", padx=5)
        self.progress_bar = ttk.Progressbar(progress_frame, orient='horizontal', length=200, mode='determinate')
        self.progress_bar.grid(row=0, column=1, sticky="ew", padx=5)
        self.status_label = ttk.Label(progress_frame, text="")
        self.status_label.grid(row=1, column=0, columnspan=2, sticky="w", padx=5)
        progress_frame.grid_columnconfigure(1, weight=1)

        # --- Output Frame Widgets ---
        ttk.Label(output_frame, text="Optimization Results", font=('Helvetica', 12, 'bold')).grid(row=0, column=0, columnspan=2, pady=(0,10))
        self.output_text = scrolledtext.ScrolledText(output_frame, wrap=tk.WORD, height=15, width=60, font=('Courier New', 9))
        self.output_text.grid(row=1, column=0, sticky="nsew", padx=(0, 5))
        self.canvas_width = 350; self.canvas_height = 350
        self.canvas = Canvas(output_frame, width=self.canvas_width, height=self.canvas_height, bg='white', relief='sunken', borderwidth=1)
        self.canvas.grid(row=1, column=1, sticky="nsew", padx=(5, 0))
        self.canvas_padding = 20; self.max_coord = 100
        output_frame.grid_rowconfigure(1, weight=1)
        output_frame.grid_columnconfigure(0, weight=1)
        output_frame.grid_columnconfigure(1, weight=1)

        self.log("Optimizer Ready. Load data to begin.")
        self.draw_initial_canvas()


    def log(self, message):
        self.output_text.insert(tk.END, message + "\n")
        self.output_text.see(tk.END)
        self.master.update_idletasks()

    def draw_initial_canvas(self):
        self.canvas.delete("all") # Clear canvas
        shop_x, shop_y = self.map_coords(0, 0)
        self.canvas.create_oval(shop_x - 4, shop_y - 4, shop_x + 4, shop_y + 4, fill='red', outline='black', tags=('shop',))
        self.canvas.create_text(shop_x, shop_y + 10, text='Shop (0,0)', anchor='n', font=('Helvetica', 8))
        tl_x, tl_y = self.map_coords(0, 0)
        br_x, br_y = self.map_coords(self.max_coord, self.max_coord)
        self.canvas.create_rectangle(tl_x, tl_y, br_x, br_y, outline="lightgrey", dash=(2, 4))
        self.canvas.create_text(br_x, tl_y - 10, text=f'X={self.max_coord}', anchor='ne', font=('Helvetica', 8, 'italic'))
        self.canvas.create_text(tl_x - 10, br_y, text=f'Y={self.max_coord}', anchor='sw', font=('Helvetica', 8, 'italic'))

    def map_coords(self, x_km, y_km):
        canvas_w = self.canvas_width; canvas_h = self.canvas_height; pad = self.canvas_padding
        pixel_x = pad + (x_km / self.max_coord) * (canvas_w - 2 * pad)
        pixel_y = pad + (y_km / self.max_coord) * (canvas_h - 2 * pad)
        return int(pixel_x), int(pixel_y)


    def draw_solution(self, vehicles_solution, all_packages_list):
        self.draw_initial_canvas() # Clear and draw shop
        colors = ['blue', 'green', 'purple', 'orange', 'cyan', 'magenta', 'brown', 'grey']

        # Draw all packages 
        for pkg in all_packages_list:
            px, py = self.map_coords(pkg.x, pkg.y)
            # Default color grey, tag with ID
            fill_col = 'lightgrey'
            self.canvas.create_oval(px-2, py-2, px+2, py+2, fill=fill_col, outline='black', tags=('package', f'pkg_{pkg.id}'))

        # Draw assigned packages and routes
        shop_x, shop_y = self.map_coords(0, 0)
        for i, vehicle in enumerate(vehicles_solution):
            color = colors[i % len(colors)]
            last_x, last_y = shop_x, shop_y
            route_packages = vehicle.packages # Get the actual calculated route order

            if not route_packages: continue

            for pkg in route_packages: # Iterate in the calculated order
                 px, py = self.map_coords(pkg.x, pkg.y)
                 # Update package marker color on canvas using its tag
                 self.canvas.itemconfig(f'pkg_{pkg.id}', fill=color)
                 # Draw line from previous location
                 self.canvas.create_line(last_x, last_y, px, py, fill=color, width=1, tags=('route', f'vehicle_{vehicle.id}'))
                 # Draw package ID
                 self.canvas.create_text(px, py - 7, text=f"{pkg.id}", anchor='s', font=('Helvetica', 7), fill=color)
                 last_x, last_y = px, py

            # Draw line back to shop
            self.canvas.create_line(last_x, last_y, shop_x, shop_y, fill=color, width=1, dash=(2,2), tags=('route', f'vehicle_{vehicle.id}'))


    def browse_file(self, file_var):
        filename = filedialog.askopenfilename(
            title="Select Data File",
            filetypes=(("Text files", "*.txt"), ("CSV files", "*.csv"), ("All files", "*.*"))
        )
        if filename:
            file_var.set(filename)

    def load_data_from_gui(self):
        """Loads data using the core logic function."""
        pkg_file = self.pkg_file_var.get()
        veh_file = self.veh_file_var.get()

        if not pkg_file or not veh_file:
            messagebox.showerror("Error", "Please specify both package and vehicle files.")
            return

        self.log(f"Loading packages from: {pkg_file}")
        # Use core.load_data
        loaded_packages = core.load_data(pkg_file, 'package')
        if loaded_packages is None: # Error handled by core.load_data via messagebox
             self.data_status_label.config(text="Status: Error loading packages")
             self.run_button.config(state='disabled')
             return
        # Make a deep copy for the algorithms to modify, keep original list clean
        self.packages = loaded_packages # Store the loaded objects
        self.all_packages_original = copy.deepcopy(self.packages) # Keep pristine copy


        self.log(f"Loading vehicles from: {veh_file}")
        # Use core.load_data
        self.vehicles = core.load_data(veh_file, 'vehicle')
        if self.vehicles is None: # Error handled by core.load_data via messagebox
             self.data_status_label.config(text="Status: Error loading vehicles")
             self.run_button.config(state='disabled')
             return

        status_msg = f"Status: Loaded {len(self.packages)} packages, {len(self.vehicles)} vehicles."
        self.data_status_label.config(text=status_msg)
        self.log(status_msg)
        if self.packages and self.vehicles:
            self.run_button.config(state='normal') # Enable run only if both loaded successfully
        else:
            self.run_button.config(state='disabled')

        # Draw initial package locations using the original loaded list
        self.draw_solution([], self.all_packages_original)


    def toggle_parameters(self):
        algo = self.algo_var.get()
        if algo == "SA":
            self.sa_params_frame.grid()
            self.ga_params_frame.grid_remove()
        elif algo == "GA":
            self.sa_params_frame.grid_remove()
            self.ga_params_frame.grid()

    def get_parameters(self):
        params = {}
        try:
            algo = self.algo_var.get()
            params['algorithm'] = algo

            if algo == "SA":
                params['initial_temp'] = float(self.sa_temp_var.get()) # Fixed
                cool_rate = float(self.sa_cool_var.get())
                if not (0.90 <= cool_rate <= 0.99): raise ValueError("SA Cooling Rate must be between 0.90 and 0.99.")
                params['cooling_rate'] = cool_rate
                params['stop_temp'] = float(self.sa_stop_var.get()) # Fixed
                params['iter_per_temp'] = int(self.sa_iter_var.get()) # Fixed
            elif algo == "GA":
                pop_size = int(self.ga_pop_var.get())
                if not (50 <= pop_size <= 100): raise ValueError("GA Population Size must be between 50 and 100.")
                params['pop_size'] = pop_size
                mut_rate = float(self.ga_mut_var.get())
                if not (0.01 <= mut_rate <= 0.1): raise ValueError("GA Mutation Rate must be between 0.01 and 0.1.")
                params['mutation_rate'] = mut_rate
                params['generations'] = int(self.ga_gen_var.get()) # Fixed
            return params

        except ValueError as e:
            messagebox.showerror("Parameter Error", f"Invalid parameter input: {e}")
            return None

    def update_progress(self, current_step, total_steps, metric1, metric2=None):
        percentage = 0
        status_text = "Running..."
        algo = self.algo_var.get()

        if algo == "SA":
             # metric1=temp, metric2=best_cost
             # SA total steps is hard to estimate accurately beforehand with cooling
             if self.initial_sa_temp and self.sa_stop_temp and metric1 > self.sa_stop_temp:
                 # Approximate progress based on log scale of temperature
                 log_total_range = math.log(self.initial_sa_temp) - math.log(self.sa_stop_temp)
                 log_current = math.log(self.initial_sa_temp) - math.log(metric1)
                 percentage = (log_current / log_total_range) * 100 if log_total_range > 0 else 0
             elif metric1 <= self.sa_stop_temp :
                 percentage = 100 # Reached stop temp
             self.progress_bar['value'] = max(0, min(100, percentage))
             status_text = f"SA: Temp={metric1:.2f}, BestCost={metric2:.2f}"
        else: # GA
             # current_step=gen, total_steps=generations, metric1=best_cost
             if total_steps > 0:
                 percentage = (current_step / total_steps) * 100
                 self.progress_bar['value'] = percentage
             status_text = f"GA: Gen={current_step}/{total_steps}, BestCost={metric1:.2f}"

        self.status_label.config(text=status_text)
        self.master.update_idletasks()


    def run_optimization(self):
        """Gets parameters and runs the selected optimization algorithm using core logic."""
        if not self.all_packages_original or not self.vehicles:
             messagebox.showerror("Error", "Load package and vehicle data first.")
             return

        params = self.get_parameters()
        if params is None: return

        self.log("\n" + "="*30 + f"\nStarting Optimization with {params['algorithm']}\nParameters: {params}\n" + "="*30)

        self.run_button.config(state='disabled')
        self.load_button.config(state='disabled')
        self.progress_bar['value'] = 0
        self.status_label.config(text="Initializing...")
        self.master.update_idletasks()

        best_solution = None
        best_cost = float('inf')

        # --- IMPORTANT: Use a DEEP COPY of the original data for the run ---
        # This prevents the algorithm from modifying the list displayed/used by the GUI
        packages_for_run = copy.deepcopy(self.all_packages_original)
        vehicles_for_run = copy.deepcopy(self.vehicles) # Also copy vehicles if their state might change (though less likely here)

        try:
            if params['algorithm'] == "SA":
                 # Store params needed for progress calculation
                 self.initial_sa_temp = params['initial_temp']
                 self.sa_stop_temp = params['stop_temp']
                 # Note the callback signature for SA used in logic.py
                 best_solution, best_cost = core.simulated_annealing(
                    packages_for_run, # Pass the deep copy
                    vehicles_for_run,
                    params['initial_temp'], params['cooling_rate'],
                    params['stop_temp'], params['iter_per_temp'],
                    # Lambda matches the args provided by logic's callback
                    progress_callback=lambda step, total, temp, cost: self.update_progress(step, total, temp, cost)
                 )
            elif params['algorithm'] == "GA":
                 # Note the callback signature for GA used in logic.py
                 best_solution, best_cost = core.genetic_algorithm(
                    packages_for_run, # Pass the deep copy
                    vehicles_for_run,
                    params['pop_size'], params['generations'],
                    params['mutation_rate'],
                     # Lambda matches the args provided by logic's callback
                    progress_callback=lambda gen, total, cost: self.update_progress(gen, total, cost) # Pass cost as metric1
                 )

        except Exception as e:
             messagebox.showerror("Runtime Error", f"An error occurred: {e}")
             self.log(f"ERROR: {e}")
             import traceback
             self.log(traceback.format_exc()) # Log detailed traceback
        finally: # Ensure buttons are re-enabled
             self.run_button.config(state='normal')
             self.load_button.config(state='normal')
             self.status_label.config(text=f"Optimization {'Complete' if best_solution is not None else 'Failed'}.")


        # --- Process Results ---
        if best_solution is None:
             self.log("\nOptimization failed to produce a valid solution.")
             self.draw_solution([], self.all_packages_original) # Clear previous solution if failed
        else:
             self.log("\n=== Optimization Results ===")
             self.log(f"Algorithm: {params['algorithm']}")
             self.log(f"Best Cost Found (with penalty): {best_cost:.2f}")

             # Use core logic functions to recalculate/analyze the result if needed
             # Pass the result (best_solution) and the original list used for the run
             distance_cost = core.calculate_total_cost(best_solution)
             skipped = core.get_skipped_packages(packages_for_run, best_solution)
             penalty_cost = best_cost - distance_cost

             self.log(f"  - Total Distance Cost: {distance_cost:.2f} km")
             self.log(f"  - Penalty Cost for Skipped: {penalty_cost:.2f}")

             self.log("\nVehicle Assignments:")
             for i, vehicle in enumerate(best_solution):
                 # Show the actual package order from the result
                 package_details = [f"P{p.id}(W:{p.weight:.1f},Pri:{p.priority})" for p in vehicle.packages]
                 self.log(f"  Vehicle {vehicle.id}: Cap={vehicle.maxCapacity:.1f}, Load={vehicle.current_load():.1f}")
                 self.log(f"    Packages: {', '.join(package_details) if package_details else 'None'}")
                 route_dist = core.calculate_vehicle_route_distance(vehicle)
                 self.log(f"    Route Distance: {route_dist:.2f} km")

             if skipped:
                 self.log("\nSkipped Packages:")
                 # Use the details method from the Package class 
                 for pkg in sorted(skipped, key=lambda p: p.priority):
                      self.log(f"  - {pkg.details()}")
             else:
                 self.log("\nAll packages assigned.")

             # Draw the final solution 
             self.draw_solution(best_solution, packages_for_run)