def fcfs(processes):
    # Sort processes by arrival time
    processes.sort(key=lambda p: p["arrival"])

    # Simulate FCFS scheduling
    time = 0
    results = []
    for process in processes:
        if time < process["arrival"]:
            time = process["arrival"]
        start_time = time
        end_time = start_time + process["burst"]
        time = end_time
        results.append({"id": process["id"], "start": start_time, "end": end_time, "algorithm": "fcfs"})

    return results

def sjf_preemptive(processes):
    # Implement SJF Preemptive logic
    # This is a placeholder implementation
    return []

def sjf_non_preemptive(processes):
    # Sort processes by burst time
    processes.sort(key=lambda p: p["burst"])

    # Simulate SJF Non-Preemptive scheduling
    time = 0
    results = []
    for process in processes:
        if time < process["arrival"]:
            time = process["arrival"]
        start_time = time
        end_time = start_time + process["burst"]
        time = end_time
        results.append({"id": process["id"], "start": start_time, "end": end_time, "algorithm": "sjf_non_preemptive"})

    return results

def priority_preemptive(processes):
    # Implement Priority Preemptive logic
    # This is a placeholder implementation
    return []

def priority_non_preemptive(processes):
    # Sort processes by priority (lower number = higher priority)
    processes.sort(key=lambda p: p["priority"])

    # Simulate Priority Non-Preemptive scheduling
    time = 0
    results = []
    for process in processes:
        if time < process["arrival"]:
            time = process["arrival"]
        start_time = time
        end_time = start_time + process["burst"]
        time = end_time
        results.append({"id": process["id"], "start": start_time, "end": end_time, "algorithm": "priority_non_preemptive"})

    return results

def round_robin(processes, time_quantum):
    # Implement Round Robin logic
    # This is a placeholder implementation
    return []

def start_simulation(processes, algorithm="fcfs", time_quantum=None):
    if algorithm == "fcfs":
        return fcfs(processes)
    elif algorithm == "sjf_preemptive":
        return sjf_preemptive(processes)
    elif algorithm == "sjf_non_preemptive":
        return sjf_non_preemptive(processes)
    elif algorithm == "priority_preemptive":
        return priority_preemptive(processes)
    elif algorithm == "priority_non_preemptive":
        return priority_non_preemptive(processes)
    elif algorithm == "round_robin":
        return round_robin(processes, time_quantum)
    else:
        raise ValueError("Unknown algorithm specified")
