import curses
import os
import time
from file_parser import parse_simulation_file, parse_log_file


state = {
    "simulation_file_path": None,
    "log_file_path": None,
    "log_data": None,
    "message_groups": None,
    "node_positions": None,
    "node_states": None,    
    "trustsets": None,
    "malicious_nodes": None
}


def get_possible_completions(partial_path):
    if os.path.isdir(partial_path):
        return [partial_path]
    
    dir_name, base_name = os.path.split(partial_path)
    if not dir_name:
        dir_name = '.'
    
    try:
        contents = os.listdir(dir_name)
    except FileNotFoundError:
        return []
    
    completions = [os.path.join(dir_name, item) for item in contents if item.startswith(base_name)]
    return completions


def prompt_for_file_path(stdscr, prompt_message, exit_char=27):
    stdscr.addstr(23, 0, prompt_message)
    stdscr.refresh()

    curses.echo()
    file_path = ""
    
    stdscr.move(24, 0)
    
    while True:
        key = stdscr.getch()
        if key == exit_char:  # Exit key
            curses.noecho()
            return None
        elif key in (curses.KEY_ENTER, 10, 13):  # Enter key
            if file_path:
                curses.noecho()
                return file_path
            else:
                stdscr.addstr(24, 0, "Please enter a valid file path.")
                stdscr.refresh()
                time.sleep(2)
                stdscr.addstr(24, 0, " " * 60)  # Clear the line
                stdscr.move(24, 0)
                file_path = ""
                stdscr.refresh()
        elif key == curses.KEY_BACKSPACE or key == 127:  # Handle backspace
            if file_path:
                file_path = file_path[:-1]
                stdscr.addstr(24, 0, " " * 60)  # Clear the line
                stdscr.addstr(24, 0, file_path)
                stdscr.refresh()
        elif key == 9:  # Handle tab for auto-complete
            completions = get_possible_completions(file_path)
            if completions:
                common_prefix = os.path.commonprefix(completions)
                file_path = common_prefix
                stdscr.addstr(24, 0, " " * 60)  # Clear the line
                stdscr.addstr(24, 0, file_path)
                stdscr.refresh()
        else:
            file_path += chr(key)
            stdscr.addstr(24, 0, file_path)
            stdscr.refresh()


def validate_file_path(stdscr, file_path, success_message, error_message, load_function=None, header=None):
    offset = 25 if header is not None else 2

    if os.path.isfile(file_path):
        stdscr.addstr(offset, 0, success_message.format(file_path))
        if load_function:
            load_function(file_path)
    else:
        stdscr.addstr(offset, 0, error_message.format(file_path))
    stdscr.refresh()
    time.sleep(2)
    stdscr.addstr(24, 0, " " * 60)  # Clear the file path input line
    stdscr.addstr(offset, 0, " " * 60)  # Clear the status message
    stdscr.move(24, 0)
    stdscr.refresh()
    return os.path.isfile(file_path)


def load_log_file(stdscr, header=None):  # Calling function
    if header:
        header(stdscr)

    while True:
        file_path = prompt_for_file_path(stdscr, "Enter the path to the log file (or press ESC to go back): ", exit_char=27)
        if file_path is None:
            return
        if validate_file_path(stdscr, file_path, "Loaded log file: {}", "Invalid file path: {}", load_function=load_log_data, header=header):
            return


def load_log_data(file_path):
    state['log_file_path'] = file_path
    state['log_data'], state['message_groups'], state['node_states'] = parse_log_file(file_path)


def load_simulation_file(stdscr, header=None):  # Calling function
    if header:
        header(stdscr)
    
    while True:        
        file_path = prompt_for_file_path(stdscr, "Enter the path to the simulation file (or press ESC to go back): ", exit_char=27)
        if file_path is None:
            return
        if validate_file_path(stdscr, file_path, "Loaded simulation file: {}", "Invalid file path: {}", load_function=load_simulation_data, header=header):
            return


def load_simulation_data(file_path):
    state['simulation_file_path'] = file_path
    state['node_positions'] = parse_simulation_file(file_path)
