import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
from algorithms import start_simulation  # Import the simulation function
from visualization import update_visualization, calculate_process_metrics, show_process_states  # Import visualization functions

# Simulated process data
processes = []
simulation_results = None
simulation_process_data = None
show_states_button = None

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

    # Update the visualization
    update_visualization(simulation_results, figure, ax, canvas)
    
    # Enable the state transition button
    show_states_button.config(state=tk.NORMAL)

def show_process_states_handler():
    """Handler for the Show Process States button"""
    if simulation_results and simulation_process_data:
        show_process_states(simulation_results, simulation_process_data)
    else:
        messagebox.showinfo("Process States", "Please run a simulation first.")

def create_gui():
    root = tk.Tk()
    root.title("Process Visualization Tool")

    # Register validation command
    validate_numeric = root.register(validate_numeric_input)

    # Create input form
    frame = ttk.Frame(root, padding="10")
    frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

    # Process ID display label
    ttk.Label(frame, text="Process ID:").grid(column=0, row=0, sticky=tk.W, pady=5)
    global process_id_label
    process_id_label = ttk.Label(frame, text="P1")
    process_id_label.grid(column=0, row=1, sticky=tk.W, pady=5)

    ttk.Label(frame, text="Arrival Time").grid(column=1, row=0, sticky=tk.W, pady=5)
    ttk.Label(frame, text="Burst Time").grid(column=2, row=0, sticky=tk.W, pady=5)

    global priority_label
    priority_label = ttk.Label(frame, text="Priority")
    global priority_entry
    priority_entry = ttk.Entry(frame, validate="key", validatecommand=(validate_numeric, '%P'))

    global arrival_time_entry
    arrival_time_entry = ttk.Entry(frame, validate="key", validatecommand=(validate_numeric, '%P'))
    arrival_time_entry.grid(column=1, row=1, pady=5)

    global burst_time_entry
    burst_time_entry = ttk.Entry(frame, validate="key", validatecommand=(validate_numeric, '%P'))
    burst_time_entry.grid(column=2, row=1, pady=5)

    # Button to add process - moved to column 4 to avoid overlap
    add_button = ttk.Button(frame, text="Add Process", command=add_process)
    add_button.grid(column=4, row=1, pady=5)

    # Button to remove selected process
    remove_button = ttk.Button(frame, text="Remove Process", command=remove_process)
    remove_button.grid(column=4, row=2, pady=5)

    global time_quantum_label
    time_quantum_label = ttk.Label(frame, text="Time Quantum (for RR):")
    global time_quantum_entry
    time_quantum_entry = ttk.Entry(frame, validate="key", validatecommand=(validate_numeric, '%P'))

    # Dropdown for algorithm selection
    global algorithm_var
    algorithm_var = tk.StringVar(value="fcfs")
    algorithm_label = ttk.Label(frame, text="Select Algorithm:")
    algorithm_label.grid(column=0, row=3, sticky=tk.W, pady=5)
    algorithm_dropdown = ttk.OptionMenu(frame, algorithm_var, "fcfs", "fcfs", "sjf_preemptive", "sjf_non_preemptive", "priority_preemptive", "priority_non_preemptive", "round_robin", command=update_input_fields)
    algorithm_dropdown.grid(column=1, row=3, columnspan=2, pady=5)

    # Create a table to display processes
    global process_table
    process_table = ttk.Treeview(frame, columns=("ID", "Arrival", "Burst"), show="headings")
    process_table.heading("ID", text="Process ID")
    process_table.heading("Arrival", text="Arrival Time")
    process_table.heading("Burst", text="Burst Time")
    process_table.grid(column=0, row=4, columnspan=5, pady=5)  # Expanded to cover column 4
    
    # Add scrollbar to the table
    scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=process_table.yview)
    process_table.configure(yscroll=scrollbar.set)
    scrollbar.grid(column=5, row=4, sticky=(tk.N, tk.S))

    # Create a button to start the simulation
    start_button = ttk.Button(frame, text="Start Simulation", command=start_simulation_handler)
    start_button.grid(column=0, row=5, columnspan=3, pady=10)

    # Create a button to show process states (initially disabled)
    global show_states_button
    show_states_button = ttk.Button(frame, text="Show Process States", command=show_process_states_handler, state=tk.DISABLED)
    show_states_button.grid(column=3, row=5, columnspan=2, pady=10)

    # Create a canvas for visualization
    global figure, ax, canvas
    figure = plt.Figure(figsize=(6, 4), dpi=100)
    ax = figure.add_subplot(111)
    canvas = FigureCanvasTkAgg(figure, root)
    canvas.get_tk_widget().grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

    # Configure column and row weights for proper resizing
    root.columnconfigure(0, weight=1)
    root.rowconfigure(1, weight=1)
    frame.columnconfigure(4, weight=1)

    root.mainloop()

if __name__ == "__main__":
    create_gui()
