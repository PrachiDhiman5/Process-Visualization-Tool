import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
from algorithms import start_simulation  # Import the simulation function
from visualization import update_visualization, calculate_process_metrics, create_gantt_chart_in_frame, create_metrics_table_in_frame, show_process_states_in_frame  # Import visualization functions

# Simulated process data
processes = []
simulation_results = None
simulation_process_data = None
show_states_button = None

# Variables to hold the result frames
result_frame = None
gantt_frame = None
metrics_frame = None
states_frame = None
states_visible = False
notebook = None

def validate_numeric_input(value):
    """Validate if the input is numeric"""
    if value == "":
        return True
    try:
        int(value)
        return True
    except ValueError:
        return False

def add_process():
    # Get input values
    arrival_time = arrival_time_entry.get()
    burst_time = burst_time_entry.get()
    
    # Check if required fields are filled
    if not arrival_time or not burst_time:
        messagebox.showerror("Input Error", "Arrival time and burst time are required.")
        return
        
    # Validate numeric values
    if not validate_numeric_input(arrival_time) or not validate_numeric_input(burst_time):
        messagebox.showerror("Input Error", "Please enter numeric values for arrival time and burst time.")
        return
    
    # Check priority field if algorithm requires it
    selected_algorithm = algorithm_var.get()
    if selected_algorithm in ["priority_preemptive", "priority_non_preemptive"]:
        priority = priority_entry.get()
        if not priority:
            messagebox.showerror("Input Error", "Priority value is required for Priority scheduling algorithms.")
            return
        if not validate_numeric_input(priority):
            messagebox.showerror("Input Error", "Please enter a numeric value for priority.")
            return
    else:
        priority = 0
    
    # All validations passed, add the process
    process_id = f"P{len(processes) + 1}"
    processes.append({
        "id": process_id, 
        "arrival": int(arrival_time), 
        "burst": int(burst_time), 
        "priority": int(priority_entry.get()) if priority_entry.winfo_ismapped() and priority_entry.get() else 0
    })

    # Clear input fields
    # Update the next process ID
    process_id_label.config(text=f"P{len(processes) + 1}")
    arrival_time_entry.delete(0, tk.END)
    burst_time_entry.delete(0, tk.END)
    if priority_entry.winfo_ismapped():
        priority_entry.delete(0, tk.END)

    # Update process table
    update_process_table()

def remove_process():
    # Get selected item from the table
    selected_item = process_table.selection()
    
    if not selected_item:
        messagebox.showinfo("Remove Process", "Please select a process to remove.")
        return
    
    # Get the process ID of the selected item
    process_id = process_table.item(selected_item)['values'][0]
    
    # Find and remove the process from the list
    for i, process in enumerate(processes):
        if process["id"] == process_id:
            processes.pop(i)
            break
    
    # Renumber the remaining processes sequentially
    for i, process in enumerate(processes):
        process["id"] = f"P{i+1}"
    
    # Update the process table
    update_process_table()
    
    # Update the next process ID label
    process_id_label.config(text=f"P{len(processes) + 1}")

def update_process_table():
    # Clear existing rows
    for row in process_table.get_children():
        process_table.delete(row)

    # Insert new rows
    for process in processes:
        if "Priority" in process_table["columns"]:
            process_table.insert("", "end", values=(process["id"], process["arrival"], process["burst"], process["priority"]))
        else:
            process_table.insert("", "end", values=(process["id"], process["arrival"], process["burst"]))

def update_input_fields(event):
    selected_algorithm = algorithm_var.get()
    
    # Clear existing processes when algorithm changes
    global processes
    processes = []
    
    # Reset the process ID label
    process_id_label.config(text="P1")
    
    # First handle the priority field visibility
    if selected_algorithm in ["priority_preemptive", "priority_non_preemptive"]:
        # Make sure all previous columns are still displayed
        process_table.config(columns=("ID", "Arrival", "Burst", "Priority"))
        process_table.heading("ID", text="Process ID")
        process_table.heading("Arrival", text="Arrival Time")
        process_table.heading("Burst", text="Burst Time")
        process_table.heading("Priority", text="Priority")
        priority_label.grid(column=3, row=0, sticky=tk.W, pady=5)
        priority_entry.grid(column=3, row=1, pady=5)
    else:
        # Configure with only original columns
        process_table.config(columns=("ID", "Arrival", "Burst"))
        process_table.heading("ID", text="Process ID")
        process_table.heading("Arrival", text="Arrival Time")
        process_table.heading("Burst", text="Burst Time")
        priority_label.grid_forget()
        priority_entry.grid_forget()

    # Now handle the time quantum field visibility
    if selected_algorithm == "round_robin":
        time_quantum_label.grid(column=0, row=2, sticky=tk.W, pady=5)
        time_quantum_entry.grid(column=1, row=2, pady=5)
    else:
        time_quantum_label.grid_forget()
        time_quantum_entry.grid_forget()
    
    # Update table with the current process list (which should be empty now)
    update_process_table()

def setup_results_frame():
    global result_frame, gantt_frame, metrics_frame, notebook, show_states_button
    
    # If result frame already exists, clear it
    if result_frame:
        for widget in result_frame.winfo_children():
            widget.destroy()
    else:
        # Create the result frame if it doesn't exist
        result_frame = ttk.Frame(root)
        result_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
    
    # Create a notebook with tabs
    notebook = ttk.Notebook(result_frame)
    notebook.pack(fill=tk.BOTH, expand=True)
    
    # Results tab
    results_tab = ttk.Frame(notebook)
    notebook.add(results_tab, text="Results")
    
    # Create gantt chart frame in results tab
    gantt_frame = ttk.Frame(results_tab)
    gantt_frame.pack(fill=tk.BOTH, expand=True)
    
    # Create container frame for metrics table and show states button
    bottom_container = ttk.Frame(results_tab)
    bottom_container.pack(fill=tk.BOTH, expand=True)
    
    # Create left frame for metrics table (half width)
    left_frame = ttk.Frame(bottom_container)
    left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    
    # Create right frame for the button
    right_frame = ttk.Frame(bottom_container)
    right_frame.pack(side=tk.RIGHT, fill=tk.Y)
    
    # Create metrics frame in left frame
    metrics_frame = ttk.Frame(left_frame)
    metrics_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
    
    # Create show states button in right frame
    show_states_button = ttk.Button(right_frame, text="Show Process States", 
                                   command=lambda: show_process_states_tab())
    show_states_button.pack(pady=10, padx=20)
    
    return gantt_frame, metrics_frame

def show_process_states_tab():
    global notebook, simulation_results, simulation_process_data
    
    # Check if the states tab already exists
    for tab_id in notebook.tabs():
        if notebook.tab(tab_id, "text") == "Process States":
            # Select the tab and return
            notebook.select(tab_id)
            return
    
    # Create a new tab for process states
    states_tab = ttk.Frame(notebook)
    notebook.add(states_tab, text="Process States")
    notebook.select(states_tab)
    
    # Create the process states visualization in the tab
    show_process_states_in_frame(simulation_results, simulation_process_data, states_tab)

def start_simulation_handler():
    # Check if there are processes to simulate
    if not processes:
        messagebox.showinfo("Simulation", "Please add at least one process before starting the simulation.")
        return
        
    # Get selected algorithm and time quantum
    selected_algorithm = algorithm_var.get()
    
    # Validate time quantum for Round Robin
    if selected_algorithm == "round_robin":
        time_quantum = time_quantum_entry.get()
        if not time_quantum:
            messagebox.showerror("Input Error", "Time Quantum is required for Round Robin algorithm.")
            return
        if not validate_numeric_input(time_quantum):
            messagebox.showerror("Input Error", "Please enter a numeric value for Time Quantum.")
            return
        time_quantum = int(time_quantum)
    else:
        time_quantum = None

    # Run the simulation logic
    global simulation_results, simulation_process_data
    simulation_results = start_simulation(processes, algorithm=selected_algorithm, time_quantum=time_quantum)
    
    # Calculate process metrics
    simulation_process_data = calculate_process_metrics(simulation_results)
    
    # Set up the results frame with notebook tabs
    gantt_frame, metrics_frame = setup_results_frame()
    
    # Create the Gantt chart in the gantt frame
    create_gantt_chart_in_frame(simulation_results, gantt_frame)
    
    # Create the metrics table in the metrics frame - with half width
    create_metrics_table_in_frame(simulation_process_data, metrics_frame)
    
    # Show the results frame
    result_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
    
    # If the canvas still exists, hide it
    if canvas:
        canvas.get_tk_widget().grid_forget()

def create_gui():
    global root, figure, ax, canvas
    
    root = tk.Tk()
    root.title("Process Visualization Tool")
    root.geometry("900x700")  # Set initial window size

    # Register validation command
    validate_numeric = root.register(validate_numeric_input)

    # Create input frame
    input_frame = ttk.Frame(root, padding="10")
    input_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

    # Create a container frame for the left side (input fields and table)
    left_container = ttk.Frame(input_frame)
    left_container.grid(row=0, column=0, sticky=(tk.W, tk.N, tk.S))
    
    # Calculate half width in pixels
    half_width = 450  # Adjust as needed for your UI

    # Process ID display label
    ttk.Label(left_container, text="Process ID:").grid(column=0, row=0, sticky=tk.W, pady=5)
    global process_id_label
    process_id_label = ttk.Label(left_container, text="P1")
    process_id_label.grid(column=0, row=1, sticky=tk.W, pady=5)

    ttk.Label(left_container, text="Arrival Time").grid(column=1, row=0, sticky=tk.W, pady=5)
    ttk.Label(left_container, text="Burst Time").grid(column=2, row=0, sticky=tk.W, pady=5)

    global priority_label
    priority_label = ttk.Label(left_container, text="Priority")
    global priority_entry
    priority_entry = ttk.Entry(left_container, validate="key", validatecommand=(validate_numeric, '%P'))

    global arrival_time_entry
    arrival_time_entry = ttk.Entry(left_container, validate="key", validatecommand=(validate_numeric, '%P'))
    arrival_time_entry.grid(column=1, row=1, pady=5)

    global burst_time_entry
    burst_time_entry = ttk.Entry(left_container, validate="key", validatecommand=(validate_numeric, '%P'))
    burst_time_entry.grid(column=2, row=1, pady=5)

    # Button to add process
    add_button = ttk.Button(left_container, text="Add Process", command=add_process)
    add_button.grid(column=4, row=1, pady=5)

    # Button to remove selected process
    remove_button = ttk.Button(left_container, text="Remove Process", command=remove_process)
    remove_button.grid(column=4, row=2, pady=5)

    global time_quantum_label
    time_quantum_label = ttk.Label(left_container, text="Time Quantum (for RR):")
    global time_quantum_entry
    time_quantum_entry = ttk.Entry(left_container, validate="key", validatecommand=(validate_numeric, '%P'))

    # Dropdown for algorithm selection
    global algorithm_var
    algorithm_var = tk.StringVar(value="fcfs")
    algorithm_label = ttk.Label(left_container, text="Select Algorithm:")
    algorithm_label.grid(column=0, row=3, sticky=tk.W, pady=5)
    algorithm_dropdown = ttk.OptionMenu(left_container, algorithm_var, "fcfs", "fcfs", "sjf_preemptive", "sjf_non_preemptive", "priority_preemptive", "priority_non_preemptive", "round_robin", command=update_input_fields)
    algorithm_dropdown.grid(column=1, row=3, columnspan=2, pady=5)

    # Create a table to display processes with reduced width
    global process_table
    process_table = ttk.Treeview(left_container, columns=("ID", "Arrival", "Burst"), show="headings", height=6)
    process_table.heading("ID", text="Process ID")
    process_table.heading("Arrival", text="Arrival Time")
    process_table.heading("Burst", text="Burst Time")
    
    # Set width for each column to control the overall table width
    process_table.column("ID", width=80)
    process_table.column("Arrival", width=80)
    process_table.column("Burst", width=80)
    
    process_table.grid(column=0, row=4, columnspan=5, pady=5, sticky=(tk.W, tk.E))
    
    # Add scrollbar to the table
    scrollbar = ttk.Scrollbar(left_container, orient=tk.VERTICAL, command=process_table.yview)
    process_table.configure(yscroll=scrollbar.set)
    scrollbar.grid(column=5, row=4, sticky=(tk.N, tk.S))

    # Create a button to start the simulation
    start_button = ttk.Button(input_frame, text="Start Simulation", command=start_simulation_handler)
    start_button.grid(column=0, row=5, pady=10, sticky=(tk.W, tk.E))

    # Create a separator
    ttk.Separator(input_frame, orient=tk.HORIZONTAL).grid(column=0, row=6, sticky=(tk.W, tk.E), pady=5)

    # Create a canvas for visualization (will be replaced by our custom visualization)
    figure = plt.Figure(figsize=(8, 4), dpi=100)
    ax = figure.add_subplot(111)
    ax.set_title("Simulation Results Will Appear Here")
    canvas = FigureCanvasTkAgg(figure, root)
    canvas.get_tk_widget().grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

    # Configure column and row weights for proper resizing
    root.columnconfigure(0, weight=1)
    root.rowconfigure(1, weight=1)

    root.mainloop()

if __name__ == "__main__":
    create_gui()
