import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
from tkinter import ttk
import tkinter as tk

# Global variable to track the results window
results_window = None

def update_visualization(results, figure, ax, canvas):
    """Update the visualization with the simulation results"""
    global results_window
    
    # Create or focus the results window
    if results_window is None or not results_window.winfo_exists():
        create_results_window(results)
    else:
        results_window.lift()  # Bring window to front
        update_results_window(results)
    
    # Clear the original figure (we won't use it since we're displaying in the new tab)
    ax.clear()
    ax.set_title("Simulation running in results window")
    canvas.draw()

def create_results_window(results):
    """Create a new window to display all the simulation results"""
    global results_window
    
    results_window = tk.Toplevel()
    results_window.title("Simulation Results")
    results_window.geometry("900x700")
    
    # Create a notebook with tabs
    notebook = ttk.Notebook(results_window)
    notebook.pack(fill=tk.BOTH, expand=True)
    
    # Results tab - contains Gantt chart and metrics table
    results_tab = ttk.Frame(notebook)
    notebook.add(results_tab, text="Results")
    
    # Create frames for the Gantt chart and metrics table
    gantt_frame = ttk.Frame(results_tab)
    gantt_frame.pack(fill=tk.BOTH, expand=True)
    
    metrics_frame = ttk.Frame(results_tab)
    metrics_frame.pack(fill=tk.BOTH, expand=True)
    
    # Create the Gantt chart
    create_gantt_chart_in_frame(results, gantt_frame)
    
    # Calculate metrics and create the table
    process_data = calculate_process_metrics(results)
    create_metrics_table_in_frame(process_data, metrics_frame)
    
    # Create button to show process states
    state_button = ttk.Button(results_tab, text="Show Process States", 
                             command=lambda: show_process_states_in_frame(results, process_data, results_tab))
    state_button.pack(pady=10)
    
    # Store references in the window for future updates
    results_window.results = results
    results_window.process_data = process_data
    results_window.gantt_frame = gantt_frame
    results_window.metrics_frame = metrics_frame
    results_window.state_button = state_button

def update_results_window(results):
    """Update the existing results window with new simulation results"""
    if results_window and results_window.winfo_exists():
        # Clear existing frames
        for widget in results_window.gantt_frame.winfo_children():
            widget.destroy()
        for widget in results_window.metrics_frame.winfo_children():
            widget.destroy()
        
        # Calculate new metrics
        process_data = calculate_process_metrics(results)
        
        # Update Gantt chart
        create_gantt_chart_in_frame(results, results_window.gantt_frame)
        
        # Update metrics table
        create_metrics_table_in_frame(process_data, results_window.metrics_frame)
        
        # Update stored references
        results_window.results = results
        results_window.process_data = process_data
        
        # Reset the state button functionality
        results_window.state_button.config(
            command=lambda: show_process_states_in_frame(results, process_data, results_window.state_button.master)
        )

def calculate_process_metrics(results):
    """Calculate process metrics including completion time, turnaround time, and waiting time"""
    # Get unique process IDs and sort them
    process_ids = sorted(set(result["id"] for result in results), key=lambda x: int(x[1:]))
    
    # Create a dictionary to track the metrics of each process
    process_data = {}
    
    # First, initialize process data
    for pid in process_ids:
        process_data[pid] = {
            "arrival_time": float('inf'),
            "burst_time": 0,
            "completion_time": 0,
            "segments": []
        }
    
    # Now populate the data from results
    for result in results:
        pid = result["id"]
        start = result["start"]
        end = result["end"]
        
        # Track the earliest arrival time
        process_data[pid]["arrival_time"] = min(process_data[pid]["arrival_time"], start)
        
        # Add burst time
        segment_burst = end - start
        process_data[pid]["burst_time"] += segment_burst
        
        # Update completion time if this is the latest segment
        process_data[pid]["completion_time"] = max(process_data[pid]["completion_time"], end)
        
        # Add segment information for the Gantt chart
        process_data[pid]["segments"].append({"start": start, "end": end})
    
    # Calculate turnaround time and waiting time
    for pid, data in process_data.items():
        data["turnaround_time"] = data["completion_time"] - data["arrival_time"]
        data["waiting_time"] = data["turnaround_time"] - data["burst_time"]
    
    return process_data

def create_gantt_chart_in_frame(results, frame):
    """Create a Gantt chart in the specified frame"""
    # Get the algorithm name for display
    algorithm_names = {
        "fcfs": "First Come First Serve",
        "sjf_preemptive": "Shortest Job First (Preemptive)",
        "sjf_non_preemptive": "Shortest Job First (Non-Preemptive)",
        "priority_preemptive": "Priority Scheduling (Preemptive)",
        "priority_non_preemptive": "Priority Scheduling (Non-Preemptive)",
        "round_robin": "Round Robin"
    }
    
    algorithm_colors = {
        "fcfs": 'Blues',
        "sjf_preemptive": 'Greens',
        "sjf_non_preemptive": 'Oranges',
        "priority_preemptive": 'Purples',
        "priority_non_preemptive": 'Reds',
        "round_robin": 'YlGnBu'
    }
    
    # Determine the algorithm used
    algorithm = results[0]['algorithm'] if 'algorithm' in results[0] else "fcfs"
    colormap = plt.cm.get_cmap(algorithm_colors.get(algorithm, 'viridis'))
    
    # Calculate metrics
    process_data = calculate_process_metrics(results)
    
    # Create a new figure with appropriate size
    figure = plt.Figure(figsize=(10, 4), dpi=100)
    ax = figure.add_subplot(111)
    
    # Create the Gantt chart
    create_gantt_chart(results, process_data, ax, colormap)
    
    # Set plot title
    ax.set_title(f'{algorithm_names.get(algorithm, algorithm)} Scheduling', pad=20)
    
    # Create canvas for the figure and add it to the frame
    canvas = FigureCanvasTkAgg(figure, frame)
    canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    canvas.draw()
    
    # Add a label for the algorithm
    ttk.Label(frame, text=f"Algorithm: {algorithm_names.get(algorithm, algorithm)}", 
              font=("Arial", 12, "bold")).pack(pady=(5, 0))

def create_metrics_table_in_frame(process_data, frame):
    """Create a table showing process metrics in the specified frame"""
    # Create the table
    columns = ("Process ID", "Arrival Time", "Burst Time", "Completion Time", "Turnaround Time", "Waiting Time")
    metrics_table = ttk.Treeview(frame, columns=columns, show="headings")
    
    # Set column headings
    for col in columns:
        metrics_table.heading(col, text=col)
        metrics_table.column(col, width=100, anchor=tk.CENTER)
    
    # Add data to the table
    for pid, data in sorted(process_data.items(), key=lambda x: int(x[0][1:])):
        metrics_table.insert("", "end", values=(
            pid,
            f"{data['arrival_time']:.1f}",
            f"{data['burst_time']:.1f}",
            f"{data['completion_time']:.1f}",
            f"{data['turnaround_time']:.1f}",
            f"{data['waiting_time']:.1f}"
        ))
    
    # Add a scrollbar
    scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=metrics_table.yview)
    metrics_table.configure(yscroll=scrollbar.set)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    metrics_table.pack(fill=tk.BOTH, expand=True)
    
    # Calculate summary statistics
    avg_turnaround = sum(data["turnaround_time"] for data in process_data.values()) / len(process_data)
    avg_waiting = sum(data["waiting_time"] for data in process_data.values()) / len(process_data)
    
    # Create a separate frame for summary statistics to ensure visibility
    summary_frame = ttk.Frame(frame)
    summary_frame.pack(fill=tk.X, pady=10, padx=5, side=tk.BOTTOM)
    
    # Make the summary statistics more visible with a border and padding
    summary_label_frame = ttk.LabelFrame(summary_frame, text="Summary Statistics")
    summary_label_frame.pack(fill=tk.X, padx=5, pady=5)
    
    # Add the statistics with improved visibility
    ttk.Label(summary_label_frame, text=f"Average Turnaround Time: {avg_turnaround:.2f}", 
              font=("Arial", 12, "bold")).pack(side=tk.TOP, padx=10, pady=5, anchor=tk.W)
    ttk.Label(summary_label_frame, text=f"Average Waiting Time: {avg_waiting:.2f}", 
              font=("Arial", 12, "bold")).pack(side=tk.TOP, padx=10, pady=5, anchor=tk.W)

def create_gantt_chart(results, process_data, ax, colormap):
    """Create a single-row Gantt chart with process blocks"""
    # Collect all execution segments from all processes
    all_segments = []
    for pid, data in process_data.items():
        for segment in data["segments"]:
            all_segments.append({
                "pid": pid,
                "start": segment["start"],
                "end": segment["end"]
            })
    
    # Sort segments by start time
    all_segments.sort(key=lambda x: x["start"])
    
    # Calculate the time range for the chart
    min_time = min(seg["start"] for seg in all_segments)
    max_time = max(seg["end"] for seg in all_segments)
    time_range = max_time - min_time
    
    # Get unique process IDs and sort them
    process_ids = sorted(process_data.keys(), key=lambda x: int(x[1:]))
    num_processes = len(process_ids)
    
    # Draw each segment as a box on a single row
    y_pos = 0  # Single row at y=0
    height = 0.8  # Height of each block
    
    for segment in all_segments:
        pid = segment["pid"]
        start = segment["start"]
        end = segment["end"]
        duration = end - start
        
        # Calculate process index for color mapping
        proc_idx = process_ids.index(pid)
        color = colormap(0.3 + 0.7 * (proc_idx / max(1, num_processes - 1)))
        
        # Create a rectangle for this process segment
        rect = patches.Rectangle((start, y_pos - height/2), duration, height,
                                linewidth=1, edgecolor='black', facecolor=color, alpha=0.7)
        ax.add_patch(rect)
        
        # Add process ID label with consistent font size
        ax.text(start + duration/2, y_pos, pid, 
                ha='center', va='center', fontsize=9, 
                fontweight='bold', color='black')
    
    # Set plot limits and labels
    ax.set_xlim(min_time - 0.5, max_time + 0.5)
    ax.set_ylim(-1, 1)
    
    # Remove y-axis ticks and labels
    ax.set_yticks([])
    ax.set_ylabel('')
    
    # Add grid lines and time labels
    ax.set_xticks(range(int(min_time), int(max_time) + 1))
    ax.grid(axis='x', linestyle='--', alpha=0.7)
    ax.set_xlabel('Time')
    
    # Draw time markers at the bottom
    for t in range(int(min_time), int(max_time) + 1):
        ax.axvline(x=t, color='black', linestyle='--', alpha=0.3)
    
    # Enable scrolling by adjusting figure size based on time range
    figure_width = max(6, min(time_range * 0.8, 20))  # Constrain between 6 and 20 inches
    figure = ax.figure
    figure.set_size_inches(figure_width, 4)

def show_process_states_in_frame(results, process_data, parent_frame):
    """Show the process state transitions within the results window"""
    # Find any existing states frame
    states_frame = None
    for widget in parent_frame.winfo_children():
        if hasattr(widget, 'states_frame_tag') and widget.states_frame_tag:
            states_frame = widget
            break
    
    # If states frame exists, just toggle visibility
    if states_frame:
        if states_frame.winfo_viewable():
            states_frame.pack_forget()
            if hasattr(parent_frame, 'state_button'):
                parent_frame.state_button.config(text="Show Process States")
            else:
                # Find the button in the parent frame
                for widget in parent_frame.winfo_children():
                    if isinstance(widget, ttk.Button) and widget.cget("text") in ["Show Process States", "Hide Process States"]:
                        widget.config(text="Show Process States")
                        break
        else:
            states_frame.pack(fill=tk.BOTH, expand=True)
            if hasattr(parent_frame, 'state_button'):
                parent_frame.state_button.config(text="Hide Process States")
            else:
                # Find the button in the parent frame
                for widget in parent_frame.winfo_children():
                    if isinstance(widget, ttk.Button) and widget.cget("text") in ["Show Process States", "Hide Process States"]:
                        widget.config(text="Hide Process States")
                        break
        return
    
    # Create new states frame
    states_frame = ttk.Frame(parent_frame)
    states_frame.states_frame_tag = True
    states_frame.pack(fill=tk.BOTH, expand=True)
    
    # Change button text - find the button
    button_found = False
    for widget in parent_frame.winfo_children():
        if isinstance(widget, ttk.Button) and widget.cget("text") in ["Show Process States", "Hide Process States"]:
            widget.config(text="Hide Process States")
            button_found = True
            break
    
    # Create a canvas with scrollbars for the state transitions
    canvas_frame = ttk.Frame(states_frame)
    canvas_frame.pack(fill=tk.BOTH, expand=True)
    
    # Add horizontal and vertical scrollbars
    h_scrollbar = ttk.Scrollbar(canvas_frame, orient=tk.HORIZONTAL)
    v_scrollbar = ttk.Scrollbar(canvas_frame, orient=tk.VERTICAL)
    h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
    v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    # Create canvas
    canvas = tk.Canvas(canvas_frame, xscrollcommand=h_scrollbar.set, yscrollcommand=v_scrollbar.set, bg="white")
    canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    
    # Configure scrollbars
    h_scrollbar.config(command=canvas.xview)
    v_scrollbar.config(command=canvas.yview)
    
    # Create a frame to contain all content
    content_frame = ttk.Frame(canvas)
    canvas_window = canvas.create_window((0, 0), window=content_frame, anchor="nw")
    
    # Sort processes by ID
    process_ids = sorted(process_data.keys(), key=lambda x: int(x[1:]))
    
    # Define state colors
    state_colors = {
        "New": "#add8e6",      # Light blue
        "Ready": "#90ee90",    # Light green
        "Running": "#ffcc66",  # Light orange
        "Waiting": "#ffb6c1",  # Light pink
        "Terminated": "#d3d3d3"  # Light gray
    }
    
    # Define state transition widths
    state_width = 100
    transition_width = 50
    row_height = 60
    padding = 20
    
    # Process the timeline data
    timeline = {}
    max_time = 0
    
    # Extract arrival times
    for pid in process_ids:
        arrival_time = process_data[pid]["arrival_time"]
        max_time = max(max_time, process_data[pid]["completion_time"])
        
        # Initialize timeline for this process
        if pid not in timeline:
            timeline[pid] = []
    
    # Extract running segments from results
    for result in results:
        pid = result["id"]
        start_time = result["start"]
        end_time = result["end"]
        
        # Add state transitions for running segments
        timeline[pid].append((start_time, "Ready", "Running"))
        timeline[pid].append((end_time, "Running", "Ready"))
    
    # Sort all timeline events by time
    for pid in timeline:
        timeline[pid].sort(key=lambda x: x[0])
    
    # Calculate canvas size based on content
    canvas_width = max(800, int(max_time * 100) + 400)  # Add extra space for state boxes
    canvas_height = len(process_ids) * (row_height + padding) + 100
    
    # Make sure the canvas is big enough
    canvas.config(scrollregion=(0, 0, canvas_width, canvas_height))
    
    # Draw time scale at the top
    for t in range(int(max_time) + 2):
        x_pos = 200 + t * 100
        canvas.create_line(x_pos, 20, x_pos, canvas_height - 20, dash=(4, 4), fill="gray")
        canvas.create_text(x_pos, 10, text=f"t={t}", anchor="n")
    
    # Draw process state transitions for each process
    for i, pid in enumerate(process_ids):
        y_pos = 50 + i * (row_height + padding)
        
        # Draw process ID
        canvas.create_text(20, y_pos + row_height/2, text=pid, font=("Arial", 12, "bold"), anchor="w")
        
        # Get process arrival and completion times
        arrival_time = process_data[pid]["arrival_time"]
        completion_time = process_data[pid]["completion_time"]
        
        # Draw initial "New" state
        x_pos = 100
        canvas.create_rectangle(x_pos, y_pos, x_pos + state_width, y_pos + row_height, 
                            fill=state_colors["New"], outline="black")
        canvas.create_text(x_pos + state_width/2, y_pos + row_height/2, text="New", font=("Arial", 10))
        
        # Draw arrow to "Ready" state
        x_pos += state_width
        canvas.create_line(x_pos, y_pos + row_height/2, x_pos + transition_width, y_pos + row_height/2, 
                       arrow=tk.LAST, width=2)
        canvas.create_text(x_pos + transition_width/2, y_pos + row_height/2 - 15, text=f"t={arrival_time}", font=("Arial", 8))
        
        # X position now represents the timeline
        x_pos = 200 + arrival_time * 100
        
        # Draw initial "Ready" state
        ready_box_x = x_pos
        canvas.create_rectangle(x_pos, y_pos, x_pos + state_width, y_pos + row_height, 
                            fill=state_colors["Ready"], outline="black")
        canvas.create_text(x_pos + state_width/2, y_pos + row_height/2, text="Ready", font=("Arial", 10))
        
        # Draw the timeline events for this process
        current_x = x_pos + state_width
        current_state = "Ready"
        
        # Skip any transitions happening before arrival time
        proc_timeline = [t for t in timeline[pid] if t[0] >= arrival_time]
        
        for event_time, from_state, to_state in proc_timeline:
            # Position on the timeline
            time_x = 200 + event_time * 100
            
            # Draw arrow from current position to next event
            canvas.create_line(current_x, y_pos + row_height/2, time_x, y_pos + row_height/2, 
                           arrow=tk.LAST, width=2)
            canvas.create_text((current_x + time_x)/2, y_pos + row_height/2 - 15, 
                            text=f"t={event_time}", font=("Arial", 8))
            
            # Draw state box
            canvas.create_rectangle(time_x, y_pos, time_x + state_width, y_pos + row_height, 
                                fill=state_colors[to_state], outline="black")
            canvas.create_text(time_x + state_width/2, y_pos + row_height/2, text=to_state, font=("Arial", 10))
            
            # Update position for next segment
            current_x = time_x + state_width
            current_state = to_state
        
        # Draw final transition to "Terminated" state
        termination_x = 200 + completion_time * 100
        canvas.create_line(current_x, y_pos + row_height/2, termination_x, y_pos + row_height/2, 
                       arrow=tk.LAST, width=2)
        canvas.create_text((current_x + termination_x)/2, y_pos + row_height/2 - 15, 
                        text=f"t={completion_time}", font=("Arial", 8))
        
        # Draw "Terminated" state
        canvas.create_rectangle(termination_x, y_pos, termination_x + state_width, y_pos + row_height, 
                            fill=state_colors["Terminated"], outline="black")
        canvas.create_text(termination_x + state_width/2, y_pos + row_height/2, text="Terminated", font=("Arial", 10))
    
    # Update the canvas to adjust to the content frame's size
    def _configure_canvas(event):
        # Update the scroll region to encompass the inner frame
        canvas.configure(scrollregion=canvas.bbox("all"))
    
    content_frame.bind("<Configure>", _configure_canvas)
    
    # Ensure the canvas takes up the full frame space
    canvas_frame.update_idletasks()

def show_process_states(results, process_data):
    """Handler for the Show Process States button (for backward compatibility)"""
    if results_window and results_window.winfo_exists():
        # Use the new implementation that shows states in the same window
        show_process_states_in_frame(results, process_data, results_window.state_button.master)
    else:
        # Fallback to the original implementation if the results window doesn't exist
        create_results_window(results)

# Import for FigureCanvasTkAgg - needed here to avoid circular imports
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
