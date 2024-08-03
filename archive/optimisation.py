import os
import re
import subprocess
import json
import fcntl
import random
from itertools import product
from gen_sim import create_simulation_xml

lock_file_path = "java_file.lock"

def run_cooja_simulation(config):
    rows = config['rows']
    cols = config['cols']
    layers = config['layers']
    spacing_x = config['spacing_x']
    spacing_y = config['spacing_y']
    spacing_z = config['spacing_z']
    tx_range = config['tx_range']
    interference_range = config['interference_range']
    success_ratio = config['success_ratio']    
    
    create_simulation_xml(
        rows=rows,
        cols=cols,
        layers=layers,
        spacing_x=spacing_x,
        spacing_y=spacing_y,
        spacing_z=spacing_z,
        tx_range=tx_range,
        interference_range=interference_range,
        success_ratio=success_ratio,
        language="java"
    )

    simulation = f"{rows}x{cols}x{layers}_{success_ratio}"
    command = ['./gradlew', 'run', f"--args=--no-gui ../../simulations/java_{simulation}_sim.csc"]
    working_directory = '../Attack-the-BLOCC/tools/cooja'
    
    process = subprocess.Popen(
        command,
        cwd=working_directory,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    return process

def update_java_variable(num):
    java_file_path = '../Attack-the-BLOCC/tools/cooja/java/org/contikios/cooja/motes/Peer2PeerMote.java'
    with open(java_file_path, 'r') as file:
        java_code = file.readlines()
    
    for i, line in enumerate(java_code):
        if 'private static final int ATTEST_INTERVAL_MULTIPLE =' in line:
            java_code[i] = f'  private static final int ATTEST_INTERVAL_MULTIPLE = {num};  // Updated by Python script\n'
            break
    
    with open(java_file_path, 'w') as file:
        file.writelines(java_code)

def get_timeout():
    script_file_path = '../Attack-the-BLOCC/tools/cooja/headless_logger.js'
    with open(script_file_path, 'r') as file:
        lines = file.readlines()

    for line in lines:
        if 'TIMEOUT' in line:
            match = re.search(r'TIMEOUT\((\d+)\);', line)
            if match:
                return int(match.group(1))

    return None

def parse_time_from_output(line):
    match = re.search(r'(\d+):(\d+)\.(\d+)', line)
    if match:
        mins = int(match.group(1))
        secs = int(match.group(2))
        millis = int(match.group(3))
        total_time = mins * 60 * 1000 + secs * 1000 + millis
        return total_time
    
    return None

def display_progress_bar(progress, total):
    bar_length = 50
    filled_length = min(int(bar_length * progress // total), bar_length)

    bar = ['-'] * bar_length
    for i in range(filled_length):
        bar[i] = '█'

    bar_str = ''.join(bar)
    print(f'\r\033[K |{bar_str}| {progress}/{total}', end='\r')

def count_existing_logs():
    log_directory = '../Attack-the-BLOCC/simulations/'
    log_pattern = re.compile(r'^\d+x\d+x\d+_\d+\.\d+_\d+\.log$')
    existing_logs = 0

    for log_file in os.listdir(log_directory):
        if log_pattern.match(log_file):
            existing_logs += 1

    return existing_logs

def clear_screen():
    print('\033[H\033[J', end='')

def acquire_lock():
    lock_file = open(lock_file_path, 'w')
    fcntl.flock(lock_file, fcntl.LOCK_EX)
    return lock_file

def release_lock(lock_file):
    fcntl.flock(lock_file, fcntl.LOCK_UN)
    lock_file.close()

def log_file_exists(config):
    rows = config['rows']
    cols = config['cols']
    layers = config['layers']
    success_ratio = config['success_ratio']
    attest_multiple = config['attest_multiple']
    log_filename = f"{rows}x{cols}x{layers}_{success_ratio}_{attest_multiple}.log"
    log_file_path = os.path.join('../Attack-the-BLOCC/simulations/', log_filename)

    return os.path.exists(log_file_path)

def main():
    num_x = [4, 5, 6, 7, 8, 9, 10, 12, 14, 16]
    success = [1, 0.9, 0.8, 0.7, 0.6, 0.5]
    attest_multiple = [1, 5, 10, 20, 40, 60, 80, 100, 150, 200]
    timeout = get_timeout() - 60000

    combinations = list(product(num_x, num_x, num_x, success, attest_multiple))
    random.shuffle(combinations)

    total_combinations = len(combinations)
    existing_logs = count_existing_logs()
    combinations_tried = existing_logs

    for rows, cols, layers, success_ratio, attest_value in combinations:
        config = {
            "rows": rows,
            "cols": cols,
            "layers": layers,
            "spacing_x": 3, 
            "spacing_y": 12, 
            "spacing_z": 5,
            "tx_range": 14, 
            "interference_range": 20, 
            "success_ratio": success_ratio,
            "attest_multiple": attest_value
        }

        if log_file_exists(config):
            combinations_tried += 1
            continue

        combinations_tried += 1
        percentage_done = (combinations_tried / total_combinations) * 100
        print(f"Progress: {percentage_done:.2f}% of combinations tried\n")
        print(json.dumps(config, indent=2), "\n")
        print("Compiling java...\r", end='')

        lock_file = acquire_lock()

        try:
            update_java_variable(attest_value)
            process = run_cooja_simulation(config)

            compilation_done = False
            while not compilation_done:
                output = process.stdout.readline().strip()
                if output:
                    if "> Task :run" in output:
                        compilation_done = True
            
            release_lock(lock_file)

            simulation_done = False
            while not simulation_done:
                output = process.stdout.readline().strip()
                if output:
                    current_time = parse_time_from_output(output)
                    if current_time is not None:
                        display_progress_bar(current_time - 60000, timeout)
                if process.poll() is not None:
                    simulation_done = True

        except Exception as e:
            print(f"Error: {e}")
            release_lock(lock_file)
        
        clear_screen()

if __name__ == "__main__":    
    main()
