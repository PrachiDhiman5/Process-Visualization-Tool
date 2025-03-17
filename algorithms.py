def fcfs(processes):
    """First Come First Serve scheduling algorithm"""
    # Make a copy to avoid modifying the original list
    processes_copy = sorted(processes, key=lambda p: p["arrival"])

    # Simulate FCFS scheduling
    time = 0
    results = []
    for process in processes_copy:
        if time < process["arrival"]:
            time = process["arrival"]
        start_time = time
        end_time = start_time + process["burst"]
        time = end_time
        results.append({"id": process["id"], "start": start_time, "end": end_time, "algorithm": "fcfs"})

    return results

def sjf_non_preemptive(processes):
    """Shortest Job First (Non-Preemptive) scheduling algorithm"""
    # Make a copy to avoid modifying the original list
    processes_copy = [p.copy() for p in processes]
    
    time = 0
    results = []
    remaining_processes = len(processes_copy)
    
    while remaining_processes > 0:
        # Find available processes at current time
        available_processes = [p for p in processes_copy if p["arrival"] <= time and p["burst"] > 0]
        
        if not available_processes:
            # If no process is available, jump to the next arrival time
            next_process = min([p for p in processes_copy if p["burst"] > 0], key=lambda p: p["arrival"])
            time = next_process["arrival"]
            continue
        
        # Select process with shortest burst time
        selected_process = min(available_processes, key=lambda p: p["burst"])
        
        # Execute the selected process
        start_time = time
        end_time = time + selected_process["burst"]
        time = end_time
        
        # Record the result
        results.append({
            "id": selected_process["id"], 
            "start": start_time, 
            "end": end_time, 
            "algorithm": "sjf_non_preemptive"
        })
        
        # Mark the process as completed
        for p in processes_copy:
            if p["id"] == selected_process["id"]:
                p["burst"] = 0
                remaining_processes -= 1
                break
    
    return results

def sjf_preemptive(processes):
    """Shortest Job First (Preemptive) scheduling algorithm (Shortest Remaining Time First)"""
    # Make a copy to avoid modifying the original list
    processes_copy = [p.copy() for p in processes]
    
    # Sort by arrival time for initial processing
    processes_copy.sort(key=lambda p: p["arrival"])
    
    time = 0
    results = []
    remaining_processes = len(processes_copy)
    current_process = None
    current_start = 0
    
    # Create a timeline of events (arrivals and completions)
    events = []
    for p in processes_copy:
        events.append((p["arrival"], "arrival", p["id"]))
    
    while remaining_processes > 0:
        # Find available processes at current time
        available_processes = [p for p in processes_copy if p["arrival"] <= time and p["burst"] > 0]
        
        if not available_processes:
            # If no process is available, jump to the next arrival time
            next_process = min([p for p in processes_copy if p["burst"] > 0], key=lambda p: p["arrival"])
            time = next_process["arrival"]
            continue
        
        # Select process with shortest remaining burst time
        selected_process = min(available_processes, key=lambda p: p["burst"])
        
        # Check if there's a context switch
        if current_process != selected_process["id"]:
            # If there was a process running, record its execution
            if current_process is not None:
                # Find the process that was running
                for p in processes_copy:
                    if p["id"] == current_process:
                        results.append({
                            "id": current_process,
                            "start": current_start,
                            "end": time,
                            "algorithm": "sjf_preemptive"
                        })
                        break
            
            # Start the new process
            current_process = selected_process["id"]
            current_start = time
        
        # Find next event time
        next_arrival = float('inf')
        for p in processes_copy:
            if p["arrival"] > time and p["burst"] > 0:
                next_arrival = min(next_arrival, p["arrival"])
        
        completion_time = time + selected_process["burst"]
        next_event_time = min(next_arrival, completion_time)
        
        # Update the burst time of the selected process
        time_slice = next_event_time - time
        for p in processes_copy:
            if p["id"] == selected_process["id"]:
                p["burst"] -= time_slice
                if p["burst"] <= 0:
                    remaining_processes -= 1
                break
        
        time = next_event_time
    
    # Record the last process if it was running
    if current_process is not None:
        results.append({
            "id": current_process,
            "start": current_start,
            "end": time,
            "algorithm": "sjf_preemptive"
        })
    
    return results

def priority_non_preemptive(processes):
    """Priority (Non-Preemptive) scheduling algorithm"""
    # Make a copy to avoid modifying the original list
    processes_copy = [p.copy() for p in processes]
    
    time = 0
    results = []
    remaining_processes = len(processes_copy)
    
    while remaining_processes > 0:
        # Find available processes at current time
        available_processes = [p for p in processes_copy if p["arrival"] <= time and p["burst"] > 0]
        
        if not available_processes:
            # If no process is available, jump to the next arrival time
            next_process = min([p for p in processes_copy if p["burst"] > 0], key=lambda p: p["arrival"])
            time = next_process["arrival"]
            continue
        
        # Select process with highest priority (lower number = higher priority)
        selected_process = min(available_processes, key=lambda p: p["priority"])
        
        # Execute the selected process
        start_time = time
        end_time = time + selected_process["burst"]
        time = end_time
        
        # Record the result
        results.append({
            "id": selected_process["id"], 
            "start": start_time, 
            "end": end_time, 
            "algorithm": "priority_non_preemptive"
        })
        
        # Mark the process as completed
        for p in processes_copy:
            if p["id"] == selected_process["id"]:
                p["burst"] = 0
                remaining_processes -= 1
                break
    
    return results

def priority_preemptive(processes):
    """Priority (Preemptive) scheduling algorithm"""
    # Make a copy to avoid modifying the original list
    processes_copy = [p.copy() for p in processes]
    
    time = 0
    results = []
    remaining_processes = len(processes_copy)
    current_process = None
    current_start = 0
    
    while remaining_processes > 0:
        # Find available processes at current time
        available_processes = [p for p in processes_copy if p["arrival"] <= time and p["burst"] > 0]
        
        if not available_processes:
            # If no process is available, jump to the next arrival time
            next_process = min([p for p in processes_copy if p["burst"] > 0], key=lambda p: p["arrival"])
            time = next_process["arrival"]
            continue
        
        # Select process with highest priority (lower number = higher priority)
        selected_process = min(available_processes, key=lambda p: p["priority"])
        
        # Check if there's a context switch
        if current_process != selected_process["id"]:
            # If there was a process running, record its execution
            if current_process is not None:
                # Find the process that was running
                for p in processes_copy:
                    if p["id"] == current_process:
                        results.append({
                            "id": current_process,
                            "start": current_start,
                            "end": time,
                            "algorithm": "priority_preemptive"
                        })
                        break
            
            # Start the new process
            current_process = selected_process["id"]
            current_start = time
        
        # Find next event time
        next_arrival = float('inf')
        for p in processes_copy:
            if p["arrival"] > time and p["burst"] > 0:
                next_arrival = min(next_arrival, p["arrival"])
        
        completion_time = time + selected_process["burst"]
        next_event_time = min(next_arrival, completion_time)
        
        # Update the burst time of the selected process
        time_slice = next_event_time - time
        for p in processes_copy:
            if p["id"] == selected_process["id"]:
                p["burst"] -= time_slice
                if p["burst"] <= 0:
                    remaining_processes -= 1
                break
        
        time = next_event_time
    
    # Record the last process if it was running
    if current_process is not None:
        results.append({
            "id": current_process,
            "start": current_start,
            "end": time,
            "algorithm": "priority_preemptive"
        })
    
    return results

def round_robin(processes, time_quantum):
    """Round Robin scheduling algorithm"""
    if not time_quantum or time_quantum <= 0:
        raise ValueError("Time quantum must be a positive integer")
        
    # Make a copy to avoid modifying the original list
    processes_copy = [p.copy() for p in processes]
    
    time = 0
    results = []
    ready_queue = []
    remaining_processes = len(processes_copy)
    
    # Sort processes by arrival time initially
    processes_copy.sort(key=lambda p: p["arrival"])
    
    while remaining_processes > 0:
        # Add newly arrived processes to the ready queue
        for p in processes_copy:
            if p["arrival"] <= time and p["burst"] > 0 and p["id"] not in [proc["id"] for proc in ready_queue]:
                ready_queue.append(p)
        
        if not ready_queue:
            # If the ready queue is empty, find the next process to arrive
            upcoming = [p for p in processes_copy if p["burst"] > 0]
            if upcoming:
                next_arrival = min(upcoming, key=lambda p: p["arrival"])
                time = next_arrival["arrival"]
                continue
            else:
                break  # No more processes to execute
        
        # Get the next process from the ready queue
        current_process = ready_queue.pop(0)
        
        # Calculate execution time for this quantum
        execution_time = min(time_quantum, current_process["burst"])
        
        # Record the execution
        start_time = time
        end_time = time + execution_time
        
        results.append({
            "id": current_process["id"],
            "start": start_time,
            "end": end_time,
            "algorithm": "round_robin"
        })
        
        # Update the process's remaining burst time
        for p in processes_copy:
            if p["id"] == current_process["id"]:
                p["burst"] -= execution_time
                if p["burst"] <= 0:
                    remaining_processes -= 1
                break
        
        time = end_time
        
        # Add newly arrived processes to the ready queue
        for p in processes_copy:
            if p["arrival"] <= time and p["burst"] > 0 and p["id"] not in [proc["id"] for proc in ready_queue] and p["id"] != current_process["id"]:
                ready_queue.append(p)
        
        # If the current process still has burst time left, add it back to the ready queue
        for p in processes_copy:
            if p["id"] == current_process["id"] and p["burst"] > 0:
                ready_queue.append(p)
                break
    
    return results

def start_simulation(processes, algorithm="fcfs", time_quantum=None):
    """Start the simulation with the selected algorithm and parameters"""
    # Make a copy of processes to avoid modifying the original list
    processes_copy = [p.copy() for p in processes]
    
    if algorithm == "fcfs":
        return fcfs(processes_copy)
    elif algorithm == "sjf_preemptive":
        return sjf_preemptive(processes_copy)
    elif algorithm == "sjf_non_preemptive":
        return sjf_non_preemptive(processes_copy)
    elif algorithm == "priority_preemptive":
        return priority_preemptive(processes_copy)
    elif algorithm == "priority_non_preemptive":
        return priority_non_preemptive(processes_copy)
    elif algorithm == "round_robin":
        return round_robin(processes_copy, time_quantum)
    else:
        raise ValueError(f"Unknown algorithm specified: {algorithm}")
