import curses
import os
import time
import pyfiglet
import pandas as pd
from file_loader import state, load_log_file, load_simulation_file


def print_header(stdscr):
    stdscr.clear()
    ascii_banner = pyfiglet.figlet_format('Network Simulation Viewer')
    stdscr.addstr(0, 0, ascii_banner)

    stdscr.addstr(20, 0, f"Simulation file path: {state['simulation_file_path'] if state['simulation_file_path'] else 'Not loaded'}")
    stdscr.addstr(21, 0, f"Log file path:        {state['log_file_path'] if state['log_file_path'] else 'Not loaded'}")
    stdscr.refresh()


def print_menu(stdscr, selected_row_idx, menu):
    print_header(stdscr)
    
    for idx, row in enumerate(menu):
        if idx == selected_row_idx:
            stdscr.attron(curses.color_pair(1))
            stdscr.addstr(23 + idx, 0, row)
            stdscr.attroff(curses.color_pair(1))
        else:
            stdscr.addstr(23 + idx, 0, row)

    stdscr.refresh()


def analyse_data_menu(stdscr):
    analyse_menu = ['Option 1', 'Option 2', 'Back to Main Menu']
    current_row = 0
    
    while True:
        print_menu(stdscr, current_row, analyse_menu)
        key = stdscr.getch()

        if key == curses.KEY_UP and current_row > 0:
            current_row -= 1
        elif key == curses.KEY_DOWN and current_row < len(analyse_menu) - 1:
            current_row += 1
        elif key == curses.KEY_ENTER or key in [10, 13]:
            if current_row == 0:
                # Handle Option 1
                pass
            elif current_row == 1:
                # Handle Option 2
                pass
            elif current_row == 2:
                break  # Exit the analyse menu to go back to the main menu


def main(stdscr):
    curses.curs_set(0)
    curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_WHITE)
    
    current_row = 0
    menu = ['Load Simulation File', 'Load Log File', 'Analyse Data', 'Exit']
    
    while True:
        print_menu(stdscr, current_row, menu)
        key = stdscr.getch()

        if key == curses.KEY_UP and current_row > 0:
            current_row -= 1
        elif key == curses.KEY_DOWN and current_row < len(menu) - 1:
            current_row += 1
        elif key == curses.KEY_ENTER or key in [10, 13]:
            if current_row == 0:
                load_simulation_file(stdscr, print_header)
            elif current_row == 1:
                load_log_file(stdscr, print_header)
            elif current_row == 2:
                if state['simulation_file_path'] and state['log_file_path']:
                    analyse_data_menu(stdscr)
                else:
                    stdscr.addstr(22, 0, "Please load both simulation and log files before analysing data.")
                    stdscr.refresh()
                    time.sleep(2)
                    stdscr.addstr(22, 0, " " * 60)
                    stdscr.refresh()
            elif current_row == 3:
                break


if __name__ == "__main__":
    curses.wrapper(main)
