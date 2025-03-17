import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
from tkinter import ttk
import tkinter as tk

def update_visualization(results, figure, ax, canvas):
    """Update the visualization with the simulation results"""
    # Clear the existing plot
    ax.clear()
    
    # Define colors for different processes and algorithms
    algorithm_colors = {
        "fcfs": 'Blues',
        "sjf_preemptive": 'Greens',
        "sjf_non_preemptive": 'Oranges',
        "priority_preemptive": 'Purples',
        "priority_non_preemptive": 'Reds',
        "round_robin": 'YlGnBu'
    }
    
    # Get the algorithm name for display
    algorithm_names = {
        "fcfs": "First Come First Serve",
        "sjf_preemptive": "Shortest Job First (Preemptive)",
        "sjf_non_preemptive": "Shortest Job First (Non-Preemptive)",
        "priority_preemptive": "Priority Scheduling (Preemptive)",
        "priority_non_preemptive": "Priority Scheduling (Non-Preemptive)",
        "round_robin": "Round Robin"
    }
    
    if not results:
        ax.set_title("No results to display")
        canvas.draw()
        return
    
    # Determine the algorithm used
    algorithm = results[0]['algorithm'] if 'algorithm' in results[0] else "fcfs"
    colormap = plt.cm.get_cmap(algorithm_colors.get(algorithm, 'viridis'))
    
    # Calculate metrics and create data for Gantt chart
    process_data = calculate_process_metrics(results)
    
    # Create a table with the metrics
    create_metrics_table(process_data, algorithm_names.get(algorithm, algorithm))
    
    # Create single-row Gantt chart
    create_gantt_chart(results, process_data, ax, colormap)
    
    # Set plot title
    ax.set_title(f'{algorithm_names.get(algorithm, algorithm)} Scheduling', pad=20)
    
    # Draw the canvas
    canvas.draw()

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

def create_metrics_table(process_data, algorithm_name):
    """Create a table showing process metrics"""
    # Create a new top-level window for the table
    table_window = tk.Toplevel()
    table_window.title(f"{algorithm_name} - Process Metrics")
    table_window.geometry("600x400")
    
    # Create frame for the table
    frame = ttk.Frame(table_window, padding="10")
    frame.pack(fill=tk.BOTH, expand=True)
    
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
    
    # Add summary statistics at the bottom
    avg_turnaround = sum(data["turnaround_time"] for data in process_data.values()) / len(process_data)
    avg_waiting = sum(data["waiting_time"] for data in process_data.values()) / len(process_data)
    
    summary_frame = ttk.Frame(table_window, padding="10")
    summary_frame.pack(fill=tk.X)
    
    ttk.Label(summary_frame, text=f"Average Turnaround Time: {avg_turnaround:.2f}").pack(side=tk.LEFT, padx=10)
    ttk.Label(summary_frame, text=f"Average Waiting Time: {avg_waiting:.2f}").pack(side=tk.LEFT, padx=10)

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
        # Fixed font size of 9 for all process IDs
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
    # This will make the figure wider for longer time ranges
    figure_width = max(6, min(time_range * 0.8, 20))  # Constrain between 6 and 20 inches
    figure = ax.figure
    figure.set_size_inches(figure_width, 4)

def show_process_states(results, process_data):
    """Show the process state transitions based on the simulation results"""
    # Create a new top-level window
    states_window = tk.Toplevel()
    states_window.title("Process State Transitions")
    states_window.geometry("800x600")
    
    # Create a canvas with scrollbars
    canvas_frame = ttk.Frame(states_window)
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
    
    # Frame for content
    content_frame = ttk.Frame(canvas)
    canvas.create_window((0, 0), window=content_frame, anchor="nw")
    
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
    
    # Calculate timeline points
    timeline = {}
    max_time = 0
    
    for result in results:
        pid = result["id"]
        start = result["start"]
        end = result["end"]
        max_time = max(max_time, end)
        
        if pid not in timeline:
            timeline[pid] = []
            
        # Add event points
        timeline[pid].append((start, "Ready", "Running"))
        timeline[pid].append((end, "Running", "Ready"))
    
    # Sort timeline events
    for pid in timeline:
        timeline[pid].sort(key=lambda x: x[0])
    
    # Set canvas size based on timeline
    canvas_width = max(800, int(max_time * 100) + 300)
    canvas_height = len(process_ids) * (row_height + padding) + 100
    canvas.config(scrollregion=(0, 0, canvas_width, canvas_height))
    
    # Draw time scale at the top
    for t in range(int(max_time) + 1):
        x_pos = 200 + t * 100
        canvas.create_line(x_pos, 20, x_pos, canvas_height - 20, dash=(4, 4), fill="gray")
        canvas.create_text(x_pos, 10, text=f"t={t}", anchor="n")
    
    # Draw process state transitions
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
        
        # Draw "Ready" state
        canvas.create_rectangle(x_pos, y_pos, x_pos + state_width, y_pos + row_height, 
                            fill=state_colors["Ready"], outline="black")
        canvas.create_text(x_pos + state_width/2, y_pos + row_height/2, text="Ready", font=("Arial", 10))
        
        # Draw the timeline events
        current_state = "Ready"
        current_x = x_pos + state_width
        
        for event_time, from_state, to_state in timeline[pid]:
            # Draw transition arrow
            time_x = 200 + event_time * 100
            canvas.create_line(current_x, y_pos + row_height/2, time_x, y_pos + row_height/2, 
                           arrow=tk.LAST, width=2)
            
            # Draw the next state
            canvas.create_rectangle(time_x, y_pos, time_x + state_width, y_pos + row_height, 
                                fill=state_colors[to_state], outline="black")
            canvas.create_text(time_x + state_width/2, y_pos + row_height/2, text=to_state, font=("Arial", 10))
            
            # Update current position
            current_x = time_x + state_width
            current_state = to_state
        
        # Draw final transition to "Terminated"
        termination_x = 200 + completion_time * 100
        canvas.create_line(current_x, y_pos + row_height/2, termination_x, y_pos + row_height/2, 
                       arrow=tk.LAST, width=2)
        
        # Draw "Terminated" state
        canvas.create_rectangle(termination_x, y_pos, termination_x + state_width, y_pos + row_height, 
                            fill=state_colors["Terminated"], outline="black")
        canvas.create_text(termination_x + state_width/2, y_pos + row_height/2, text="Terminated", font=("Arial", 10))
