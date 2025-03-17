import tkinter as tk
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
from algorithms import start_simulation  # Import the simulation function
from visualization import update_visualization  # Import the visualization function

# Simulated process data
processes = []

def add_process():
    # Get input values
    arrival_time = arrival_time_entry.get()
    burst_time = burst_time_entry.get()

    if arrival_time and burst_time:
        priority = priority_entry.get() if priority_entry.winfo_ismapped() else 0
        # Add process to the list
        processes.append({"id": f"P{len(processes) + 1}", "arrival": int(arrival_time), "burst": int(burst_time), "priority": int(priority)})

        # Clear input fields
        arrival_time_entry.delete(0, tk.END)
        burst_time_entry.delete(0, tk.END)
        if priority_entry.winfo_ismapped():
            priority_entry.delete(0, tk.END)

        # Update process table
        update_process_table()

def update_process_table():
    # Clear existing rows
    for row in process_table.get_children():
        process_table.delete(row)

    # Insert new rows
    for process in processes:
        if priority_entry.winfo_ismapped():
            process_table.insert("", "end", values=(process["arrival"], process["burst"], process["priority"]))
        else:
            process_table.insert("", "end", values=(process["arrival"], process["burst"]))

def update_input_fields():
    selected_algorithm = algorithm_var.get()
    if selected_algorithm in ["priority_preemptive", "priority_non_preemptive"]:
        priority_label.grid(column=2, row=0, sticky=tk.W, pady=5)
        priority_entry.grid(column=3, row=0, pady=5)
        process_table.config(columns=("Arrival", "Burst", "Priority"), show="headings")
        process_table.heading("Priority", text="Priority")
    else:
        priority_label.grid_forget()
        priority_entry.grid_forget()
        process_table.config(columns=("Arrival", "Burst"), show="headings")

    if selected_algorithm == "round_robin":
        time_quantum_label.grid(column=2, row=1, sticky=tk.W, pady=5)
        time_quantum_entry.grid(column=3, row=1, pady=5)
    else:
        time_quantum_label.grid_forget()
        time_quantum_entry.grid_forget()

def start_simulation():
    # Get selected algorithm and time quantum
    selected_algorithm = algorithm_var.get()
    time_quantum = int(time_quantum_entry.get()) if selected_algorithm == "round_robin" else None

    # Run the simulation logic
    results = start_simulation(processes, algorithm=selected_algorithm, time_quantum=time_quantum)

    # Update the visualization
    update_visualization(results, figure, ax, canvas)

def create_gui():
    root = tk.Tk()
    root.title("Process Visualization Tool")

    # Create input form
    frame = ttk.Frame(root, padding="10")
    frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

    ttk.Label(frame, text="Arrival Time:").grid(column=0, row=0, sticky=tk.W, pady=5)
    global arrival_time_entry
    arrival_time_entry = ttk.Entry(frame)
    arrival_time_entry.grid(column=1, row=0, pady=5)

    ttk.Label(frame, text="Burst Time:").grid(column=0, row=1, sticky=tk.W, pady=5)
    global burst_time_entry
    burst_time_entry = ttk.Entry(frame)
    burst_time_entry.grid(column=1, row=1, pady=5)

    global priority_label
    priority_label = ttk.Label(frame, text="Priority:")
    global priority_entry
    priority_entry = ttk.Entry(frame)

    global time_quantum_label
    time_quantum_label = ttk.Label(frame, text="Time Quantum (for RR):")
    global time_quantum_entry
    time_quantum_entry = ttk.Entry(frame)

    # Button to add process
    add_button = ttk.Button(frame, text="Add Process", command=add_process)
    add_button.grid(column=0, row=2, columnspan=2, pady=5)

    # Dropdown for algorithm selection
    global algorithm_var
    algorithm_var = tk.StringVar(value="fcfs")
    algorithm_label = ttk.Label(frame, text="Select Algorithm:")
    algorithm_label.grid(column=0, row=3, sticky=tk.W, pady=5)
    algorithm_dropdown = ttk.OptionMenu(frame, algorithm_var, "fcfs", "fcfs", "sjf_preemptive", "sjf_non_preemptive", "priority_preemptive", "priority_non_preemptive", "round_robin", command=update_input_fields)
    algorithm_dropdown.grid(column=1, row=3, pady=5)

    # Create a table to display processes
    global process_table
    process_table = ttk.Treeview(frame, columns=("Arrival", "Burst"), show="headings")
    process_table.heading("Arrival", text="Arrival Time")
    process_table.heading("Burst", text="Burst Time")
    process_table.grid(column=0, row=4, columnspan=4, pady=5)

    # Create a button to start the simulation
    start_button = ttk.Button(frame, text="Start Simulation", command=start_simulation)
    start_button.grid(column=0, row=5, columnspan=2, pady=10)

    # Create a canvas for visualization
    global figure, ax, canvas
    figure = plt.Figure(figsize=(6, 4), dpi=100)
    ax = figure.add_subplot(111)
    canvas = FigureCanvasTkAgg(figure, root)
    canvas.get_tk_widget().grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

    root.mainloop()

if __name__ == "__main__":
    create_gui()
