def update_visualization(results, figure, ax, canvas):
    # Clear the existing plot
    ax.clear()

    # Define colors for different algorithms
    algorithm_colors = {
        "fcfs": 'skyblue',
        "sjf_preemptive": 'lightgreen',
        "sjf_non_preemptive": 'lightcoral',
        "priority_preemptive": 'gold',
        "priority_non_preemptive": 'lightpink',
        "round_robin": 'lightblue'
    }

    # Determine the color based on the algorithm used
    algorithm = results[0]['algorithm'] if results and 'algorithm' in results[0] else "fcfs"
    color = algorithm_colors.get(algorithm, 'gray')

    # Plot each process as a horizontal bar
    for process in results:
        ax.barh(0, process["end"] - process["start"], left=process["start"], height=0.5, color=color)

    # Set labels and title
    ax.set_title(f'{algorithm.replace("_", " ").capitalize()} Scheduling Visualization')
    ax.set_xlabel('Time')
    ax.set_yticks([])  # Hide y-axis ticks

    # Redraw the canvas
    canvas.draw()
