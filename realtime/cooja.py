
import subprocess
import sys
from gen_sim import create_simulation_xml
import shutil
import glob

def clean_temp_dirs(pattern="/tmp/tmp.*"):
    for temp_dir in glob.glob(pattern):
        try:
            shutil.rmtree(temp_dir)
        except Exception as e:
            print(f"Error removing {temp_dir}: {e}")

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
    command = ['./gradlew_parallel', 'run', '--no-daemon', f"--args=--no-gui ../../simulations/java_{simulation}_sim.csc"]
    working_directory = '../Attack-the-BLOCC/tools/cooja'

    process = subprocess.Popen(
        command,
        cwd=working_directory,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True        
    )

    for stdout_line in iter(process.stdout.readline, ""):
        print(stdout_line.strip())
    for stderr_line in iter(process.stderr.readline, ""):
        print(stderr_line.strip(), file=sys.stderr)

    process.stdout.close()
    process.stderr.close()
    process.wait()
    clean_temp_dirs()

    return process


if __name__ == "__main__":
    config = {
        "rows": 10,
        "cols": 10,
        "layers": 10,
        "spacing_x": 3, 
        "spacing_y": 12, 
        "spacing_z": 5,
        "tx_range": 14, 
        "interference_range": 20, 
        "success_ratio": 1,
        "attest_multiple": 10
    }

    process = run_cooja_simulation(config)
