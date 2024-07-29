import subprocess
import re
import xml.etree.ElementTree as ET
from gen_sim import create_simulation_xml

def parse_simulation_file(file_path):
    tree = ET.parse(f"../Attack-the-BLOCC/simulations/java_{file_path}_sim.csc")
    root = tree.getroot()
    mote_count = 0
    for node_type in root.findall(".//motetype"):
        mote_count += len(node_type.findall(".//mote"))
    return mote_count

def parse_log_entry(entry):
    log_pattern = re.compile(
        r"(?P<message_num>\d+)\|(?P<origin_node>\d+)\|(?P<attesting_node>\d+)"
    )
    match = log_pattern.search(entry)
    if match:
        log_entry = match.groupdict()
        return log_entry
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
