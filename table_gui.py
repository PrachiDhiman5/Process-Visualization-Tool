import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
from algorithms import start_simulation
from visualization import (
    update_visualization, 
    calculate_process_metrics, 
    create_gantt_chart_in_frame, 
    create_metrics_table_in_frame, 
    show_process_states_in_frame
)

# Color Theme Configuration
class GUITheme:
    """
    Defines a color scheme and sizing for the GUI
    """
    # Color Palette
    BACKGROUND_COLOR = "#F0F4F8"  # Light blue-gray background
    PRIMARY_COLOR = "#2C3E50"     # Dark blue-gray for headers
    ACCENT_COLOR = "#3498DB"      # Bright blue for buttons
    TEXT_COLOR = "#2C3E50"        # Dark text color
    ENTRY_BG_COLOR = "#FFFFFF"    # White entry fields
    HIGHLIGHT_COLOR = "#2980B9"   # Darker blue for hover/active states
    
    # Window Sizing
    WINDOW_WIDTH = 1200   # Increased width
    WINDOW_HEIGHT = 900   # Increased height
    
    # Font Styles
    HEADER_FONT = ("Helvetica", 14, "bold")
    LABEL_FONT = ("Helvetica", 10, "bold")
    NORMAL_FONT = ("Helvetica", 10)

# Global variables
processes = []
simulation_results = None
simulation_process_data = None
show_states_button = None

# Result frame variables
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
    # Get selected algorithm
    selected_algorithm = algorithm_var.get()
    
    # Clear existing processes
    global processes
    processes = []
    
    # Reset the process ID label
    process_id_label.config(text="P1")
    
    # Handle priority field visibility
    if selected_algorithm in ["priority_preemptive", "priority_non_preemptive"]:
        # Configure table columns to include Priority
        process_table.config(columns=("ID", "Arrival", "Burst", "Priority"))
        process_table.heading("ID", text="Process ID")
        process_table.heading("Arrival", text="Arrival Time")
        process_table.heading("Burst", text="Burst Time")
        process_table.heading("Priority", text="Priority")
        
        # Show priority label and entry
        priority_label.grid(column=3, row=0, sticky=tk.W, pady=5)
        priority_entry.grid(column=3, row=1, pady=5)
    else:
        # Configure table columns without Priority
        process_table.config(columns=("ID", "Arrival", "Burst"))
        process_table.heading("ID", text="Process ID")
        process_table.heading("Arrival", text="Arrival Time")
        process_table.heading("Burst", text="Burst Time")
        
        # Hide priority label and entry
        priority_label.grid_forget()
        priority_entry.grid_forget()

    # Handle time quantum field visibility
    if selected_algorithm == "round_robin":
        time_quantum_label.grid(column=0, row=2, sticky=tk.W, pady=5)
        time_quantum_entry.grid(column=1, row=2, pady=5)
    else:
        time_quantum_label.grid_forget()
        time_quantum_entry.grid_forget()
    
    # Update table
    update_process_table()

def setup_results_frame():
    global result_frame, gantt_frame, metrics_frame, notebook, show_states_button
    
    # Clear existing result frame if it exists
    if result_frame:
        for widget in result_frame.winfo_children():
            widget.destroy()
    else:
        # Create result frame if it doesn't exist
        result_frame = ttk.Frame(root)
        result_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
    
    # Create notebook (tabbed interface)
    notebook = ttk.Notebook(result_frame)
    notebook.pack(fill=tk.BOTH, expand=True)
    
    # Create results tab
    results_tab = ttk.Frame(notebook)
    notebook.add(results_tab, text="Results")
    
    # Create Gantt chart frame
    gantt_frame = ttk.Frame(results_tab)
    gantt_frame.pack(fill=tk.BOTH, expand=True)
    
    # Create container for metrics and show states button
    bottom_container = ttk.Frame(results_tab)
    bottom_container.pack(fill=tk.BOTH, expand=True)
    
    # Create left frame for metrics
    left_frame = ttk.Frame(bottom_container)
    left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    
    # Create right frame for show states button
    right_frame = ttk.Frame(bottom_container)
    right_frame.pack(side=tk.RIGHT, fill=tk.Y)
    
    # Create metrics frame
    metrics_frame = ttk.Frame(left_frame)
    metrics_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
    
    # Create show states button
    show_states_button = ttk.Button(right_frame, text="Show Process States", 
                                   command=lambda: show_process_states_tab())
    show_states_button.pack(pady=10, padx=20)
    
    return gantt_frame, metrics_frame

def show_process_states_tab():
    global notebook, simulation_results, simulation_process_data
    
    # Check if process states tab already exists
    for tab_id in notebook.tabs():
        if notebook.tab(tab_id, "text") == "Process States":
            notebook.select(tab_id)
            return
    
    # Create new tab for process states
    states_tab = ttk.Frame(notebook)
    notebook.add(states_tab, text="Process States")
    notebook.select(states_tab)
    
    # Create process states visualization
    show_process_states_in_frame(simulation_results, simulation_process_data, states_tab)

def start_simulation_handler():
    # Check if processes exist
    if not processes:
        messagebox.showinfo("Simulation", "Please add at least one process before starting the simulation.")
        return
    
    # Get selected algorithm
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

    # Run simulation
    global simulation_results, simulation_process_data
    simulation_results = start_simulation(processes, algorithm=selected_algorithm, time_quantum=time_quantum)
    
    # Calculate process metrics
    simulation_process_data = calculate_process_metrics(simulation_results)
    
    # Set up results frame
    gantt_frame, metrics_frame = setup_results_frame()
    
    # Create Gantt chart
    create_gantt_chart_in_frame(simulation_results, gantt_frame)
    
    # Create metrics table
    create_metrics_table_in_frame(simulation_process_data, metrics_frame)
    
    # Show results frame
    result_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
    
    # Hide original canvas if it exists
    if canvas:
        canvas.get_tk_widget().grid_forget()

def create_gui(theme=GUITheme):
    """
    Create the main graphical user interface with customizable theme
    
    Args:
        theme (class): Theme class with color and sizing configurations
    """
    global root, figure, ax, canvas
    global arrival_time_entry, burst_time_entry, priority_entry
    global process_id_label, priority_label, time_quantum_label, time_quantum_entry
    global algorithm_var, process_table
    
    # Create main window
    root = tk.Tk()
    root.title("Advanced Process Scheduling Simulator")
    root.geometry(f"{theme.WINDOW_WIDTH}x{theme.WINDOW_HEIGHT}")
    root.configure(bg=theme.BACKGROUND_COLOR)

    # Configure Styles
    style = ttk.Style()
    style.theme_use('clam')  # Use clam theme for better customization

    # Style Configurations
    style.configure("TFrame", background=theme.BACKGROUND_COLOR)
    style.configure("TLabel", 
                    background=theme.BACKGROUND_COLOR, 
                    foreground=theme.TEXT_COLOR, 
                    font=theme.NORMAL_FONT)
    style.configure("TButton", 
                    background=theme.ACCENT_COLOR, 
                    foreground='white', 
                    font=theme.NORMAL_FONT)
    style.configure("Treeview", 
                    background=theme.ENTRY_BG_COLOR, 
                    fieldbackground=theme.ENTRY_BG_COLOR, 
                    foreground=theme.TEXT_COLOR)
    style.configure("Treeview.Heading", 
                    background=theme.PRIMARY_COLOR, 
                    foreground='white', 
                    font=theme.LABEL_FONT)
    
    # Button Style Mapping
    style.map('TButton', 
              background=[('active', theme.HIGHLIGHT_COLOR), 
                          ('pressed', theme.PRIMARY_COLOR)],
              foreground=[('active', 'white')])

    # Create input frame
    input_frame = ttk.Frame(root, padding="20")
    input_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

    # Header Label
    header_label = ttk.Label(
        input_frame, 
        text="Process Scheduling Simulator", 
        font=theme.HEADER_FONT, 
        foreground=theme.PRIMARY_COLOR
    )
    header_label.grid(column=0, row=0, columnspan=5, pady=(0, 20))

    # Register validation command
    validate_numeric = root.register(validate_numeric_input)

    # Create a container for input fields and table
    left_container = ttk.Frame(input_frame)
    left_container.grid(row=1, column=0, sticky=(tk.W, tk.N, tk.S))

    # Process ID Label
    ttk.Label(left_container, text="Process ID:", font=theme.LABEL_FONT).grid(column=0, row=0, sticky=tk.W, pady=5)
    process_id_label = ttk.Label(left_container, text="P1", font=theme.NORMAL_FONT)
    process_id_label.grid(column=0, row=1, sticky=tk.W, pady=5)

    # Column headers
    ttk.Label(left_container, text="Arrival Time", font=theme.LABEL_FONT).grid(column=1, row=0, sticky=tk.W, pady=5)
    ttk.Label(left_container, text="Burst Time", font=theme.LABEL_FONT).grid(column=2, row=0, sticky=tk.W, pady=5)

    # Input Entries
    arrival_time_entry = ttk.Entry(left_container, validate="key", validatecommand=(validate_numeric, '%P'))
    arrival_time_entry.grid(column=1, row=1, pady=5)

    burst_time_entry = ttk.Entry(left_container, validate="key", validatecommand=(validate_numeric, '%P'))
    burst_time_entry.grid(column=2, row=1, pady=5)

    # Priority Label and Entry (initially hidden)
    priority_label = ttk.Label(left_container, text="Priority", font=theme.LABEL_FONT)
    priority_entry = ttk.Entry(left_container, validate="key", validatecommand=(validate_numeric, '%P'))

    # Add and Remove Process Buttons
    add_button = ttk.Button(left_container, text="Add Process", command=add_process)
    add_button.grid(column=4, row=1, pady=5)

    remove_button = ttk.Button(left_container, text="Remove Process", command=remove_process)
    remove_button.grid(column=4, row=2, pady=5)

    # Time Quantum Label and Entry (initially hidden)
    time_quantum_label = ttk.Label(left_container, text="Time Quantum (for RR):", font=theme.LABEL_FONT)
    time_quantum_entry = ttk.Entry(left_container, validate="key", validatecommand=(validate_numeric, '%P'))

    # Algorithm Selection Dropdown
    algorithm_var = tk.StringVar(value="fcfs")
    algorithm_label = ttk.Label(left_container, text="Select Algorithm:", font=theme.LABEL_FONT)
    algorithm_label.grid(column=0, row=3, sticky=tk.W, pady=5)
    algorithm_dropdown = ttk.OptionMenu(
        left_container, 
        algorithm_var, 
        "fcfs", 
        "fcfs", "sjf_preemptive", "sjf_non_preemptive", 
        "priority_preemptive", "priority_non_preemptive", 
        "round_robin", 
        command=update_input_fields
    )
    algorithm_dropdown.grid(column=1, row=3, columnspan=2, pady=5)

    # Process Table
    process_table = ttk.Treeview(
        left_container, 
        columns=("ID", "Arrival", "Burst"), 
        show="headings", 
        height=6
    )
    process_table.heading("ID", text="Process ID")
    process_table.heading("Arrival", text="Arrival Time")
    process_table.heading("Burst", text="Burst Time")
    
    # Set column widths
    process_table.column("ID", width=100)
    process_table.column("Arrival", width=100)
    process_table.column("Burst", width=100)
    
    # Place the table in the GUI
    process_table.grid(column=0, row=4, columnspan=5, pady=5, sticky=(tk.W, tk.E))
    
    # Add scrollbar to the table
    scrollbar = ttk.Scrollbar(left_container, orient=tk.VERTICAL, command=process_table.yview)
    process_table.configure(yscroll=scrollbar.set)
    scrollbar.grid(column=5, row=4, sticky=(tk.N, tk.S))

    # Start Simulation Button
    start_button = ttk.Button(input_frame, text="Start Simulation", command=start_simulation_handler)
    start_button.grid(column=0, row=5, pady=10, sticky=(tk.W, tk.E))

    # Create a canvas for initial visualization
    figure = plt.Figure(figsize=(8, 4), dpi=100)
    ax = figure.add_subplot(111)
    ax.set_title("Simulation Results Will Appear Here")
    canvas = FigureCanvasTkAgg(figure, root)
    canvas.get_tk_widget().grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

    # Configure row and column weights
    root.columnconfigure(0, weight=1)
    root.rowconfigure(1, weight=1)

    # Start the Tkinter event loop
    root.mainloop()

# Create custom theme classes if desired
class DarkTheme(GUITheme):
    BACKGROUND_COLOR = "#2C3E50"
    PRIMARY_COLOR = "#ECF0F1"
    ACCENT_COLOR = "#E74C3C"
    TEXT_COLOR = "#ECF0F1"
    ENTRY_BG_COLOR = "#34495E"
    HIGHLIGHT_COLOR = "#3498DB"

class LightTheme(GUITheme):
    BACKGROUND_COLOR = "#ECF0F1"
    PRIMARY_COLOR = "#2C3E50"
    ACCENT_COLOR = "#3498DB"
    TEXT_COLOR = "#2C3E50"
    ENTRY_BG_COLOR = "#FFFFFF"
    HIGHLIGHT_COLOR = "#2980B9"

# Script Execution
if __name__ == "__main__":
    # Run with default theme
    create_gui()
    
