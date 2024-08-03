import os
import subprocess
import re
import xml.etree.ElementTree as ET
from gen_sim import create_simulation_xml

# 'gnome-terminal' or 'terminator' for remote
REMOTE_TERMINAL = 'terminator'
fifo_path = "/tmp/simulation_output_fifo"

def create_fifo():
    if not os.path.exists(fifo_path):
        os.mkfifo(fifo_path)

def open_terminal_for_display(total_motes, fifo_path):
    command = f'python fifo_display_script.py {total_motes} {fifo_path}'
    try:
        if REMOTE_TERMINAL == 'gnome-terminal':
            subprocess.Popen(['gnome-terminal', '--', 'bash', '-c', f'{command} && exec bash'])
        elif REMOTE_TERMINAL == 'terminator':
            subprocess.Popen(['terminator', '-e', f'bash -c "{command} && exec bash"'])
        else:
            print(f"Unsupported terminal: {REMOTE_TERMINAL}")
    except Exception as e:
        print(f"Failed to open terminal: {e}")

def parse_simulation_file(file_path):
    tree = ET.parse(f"../Attack-the-BLOCC/simulations/java_{file_path}_sim.csc")
    root = tree.getroot()
    mote_count = 0
    for node_type in root.findall(".//motetype"):
        mote_count += len(node_type.findall(".//mote"))
    return mote_count

def parse_log_entry(entry):
    log_pattern = re.compile(r"(?P<message_num>\d+)\|(?P<origin_node>\d+)\|(?P<attesting_node>\d+)")
    match = log_pattern.search(entry)
    if match:
        return match.groupdict()
    return None

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
    total_motes = parse_simulation_file(simulation)
    command = ['./gradlew', 'run', f"--args=--no-gui ../../simulations/java_{simulation}_sim.csc"]
    working_directory = '../Attack-the-BLOCC/tools/cooja'
    
    process = subprocess.Popen(
        command,
        cwd=working_directory,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    return process, total_motes

def main():
    create_fifo()
    config = {
        "rows": 2,
        "cols": 2,
        "layers": 1,
        "spacing_x": 3, 
        "spacing_y": 12, 
        "spacing_z": 5,
        "tx_range": 14, 
        "interference_range": 20, 
        "success_ratio": 1
    }

    process, total_motes = run_cooja_simulation(config)
    open_terminal_for_display(total_motes, fifo_path)

    try:
        with open(fifo_path, 'w') as fifo:
            while True:
                output = process.stdout.readline().strip()
                if output:
                    fifo.write(output.strip() + '\n')
                    fifo.flush()
                    print(output)
                
    finally:
        os.remove(fifo_path)

if __name__ == "__main__":
    main()
