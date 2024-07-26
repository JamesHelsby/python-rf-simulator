import os
import re
import textwrap
from collections import defaultdict
from file_parser import parse_simulation_file, parse_log_file
from trustsets import TrustsetGenerator, create_malicious_parties
from graph import create_graph, visualize_graph, visualize_graph_3D, visualize_graph_3D_with_click, find_node_with_honest_neighbors
from assumptions import *


class State:
    def __init__(self):
        self.simulation_file_path = None
        self.log_file_path = None

        self.node_positions = None
        self.log_data = None
        self.message_groups = None
        self.node_states = defaultdict(lambda: {'tx': [], 'rx': []})

        self.transmitting_range = None
        self.interference_range = None

        self.trustset_fraction = 2/3
        self.trustset_generator = None
        self.malicious_nodes = None
        self.connectivity_graph = None

  
    def load_log_data(self, file_path):
        print("Loading log data")
        self.log_file_path = file_path
        self.log_data, self.message_groups, self.node_states = parse_log_file(
            file_path=file_path
        )
    

    def update_node_states(self, log_entry):
        node_id = log_entry['node_id']
        action = log_entry['action'].lower()
        
        if action == 'tx':
            self.node_states[node_id]['tx'].append({
                'timestamp': log_entry['timestamp'],
                'message_num': log_entry['message_num'],
                'broadcast_time': log_entry['broadcast_time'],
                'attestations': []
            })

        elif action == 'rx':
            self.node_states[node_id]['rx'].append({
                'timestamp': log_entry['timestamp'],
                'message_num': log_entry['message_num'],
                'origin_node': log_entry['origin_node'],
                'attest_node': log_entry['attest_node'],
                'from_node': log_entry.get('from_node'),
                'broadcast_time': log_entry['broadcast_time']
            })
            
            if log_entry['origin_node'] == node_id and log_entry['attest_node'] != 0:
                for tx_entry in self.node_states[node_id]['tx']:
                    attestations = tx_entry['attestations']
                    if not any(att['attest_node'] == log_entry['attest_node'] for att in attestations):
                        tx_entry['attestations'].append({
                            'timestamp': log_entry['timestamp'],
                            'attest_node': log_entry['attest_node']
                        })
    

    def analyze_log_line(log_line):
        log_pattern = re.compile(
            r'(?P<timestamp>\d+:\d+\.\d+)\tID:(?P<node_id>\d+)\t\[[A-Z]+: Node\s*\]\s*'
            r'(?P<action>[A-Za-z]+): \'(?P<message_num>\d+)\|(?P<origin_node>\d+)\|(?P<attest_node>\d+)\|(?P<broadcast_time>\d+)\''
            r'(?: from node: \'(?P<from_node>\d+)\')?\s*(?:->\s*(?P<comment>.*))?'
        )

        match = log_pattern.match(log_line)
        if match:
            log_entry = match.groupdict()
            
            log_entry['timestamp'] = float(log_entry['timestamp'].replace(':', ''))
            log_entry['node_id'] = int(log_entry['node_id'])
            log_entry['message_num'] = int(log_entry['message_num'])
            log_entry['origin_node'] = int(log_entry['origin_node'])
            log_entry['attest_node'] = int(log_entry['attest_node'])
            log_entry['broadcast_time'] = int(log_entry['broadcast_time'])
            if log_entry['from_node'] is not None:
                log_entry['from_node'] = int(log_entry['from_node'])
            
            state.update_node_states(log_entry)
            
            state.check_assumption_4()
            state.check_assumption_6()
    

    def load_simulation_data(self, file_path):
        print("Loading simulation data")
        self.simulation_file_path = file_path
        self.node_positions, self.transmitting_range, self.interference_range = parse_simulation_file(
            file_path=file_path
        )


    def generate_trustsets(self, fraction=2/3, sample_probability=0.01, seed=42):
        print("Generating trustsets")
        self.trustset_generator = TrustsetGenerator(
            node_positions=self.node_positions,
            fraction=fraction,
            # sample_probability=sample_probability,
            seed=seed
        )

    
    def num_nodes(self):
        return len(self.node_positions)

    
    def create_malicious_parties(self, num_malicious):
        # print("Assigning malicious nodes")
        self.malicious_nodes = create_malicious_parties(
            node_positions=self.node_positions, 
            num_malicious=num_malicious
        )

    
    def create_graph(self):
        # print("Creating connectivity graph")
        self.connectivity_graph = create_graph(
            node_positions=self.node_positions,
            malicious_nodes = self.malicious_nodes,
            distance_threshold=self.transmitting_range
        )

    
    def check_assumption_1(self):
        print("\nChecking assumption 1")
        result, error_message = check_assumption_1(
            node_positions=self.node_positions,
            trustset_generator=self.trustset_generator
        )
        print(f"Status: {result}\n")
        
        if not result:
            print(error_message)
        return result
    

    def check_assumption_2(self):
        print("\nChecking assumption 2")
        result, error_message = check_assumption_2(
            trustset_generator=self.trustset_generator,
            malicious_nodes=self.malicious_nodes            
        )
        print(f"Status: {result}")
        
        if not result:
            print(error_message)
        return result
    

    def check_assumption_3(self):
        print("\nChecking assumption 3")
        result, error_message = check_assumption_3(
            trustset_generator=self.trustset_generator,
            malicious_nodes=self.malicious_nodes         
        )
        print(f"Status: {result}")
        
        if not result:
            print(error_message)
        return result
    

    def check_assumption_4(self):
        print("\nChecking assumption 4")
        result, error_message = check_assumption_4(
            node_states=self.node_states,
            trustset_generator=self.trustset_generator,
            malicious_nodes=self.malicious_nodes,
            t_rep=5
        )
        print(f"Status: {result}")
        
        if not result:
            print(error_message)
        return result
    

    def check_assumption_5(self):
        print("\nChecking assumption 5")
        result, valid_nodes = check_assumption_5_fast(
            G=self.connectivity_graph,
            trustset_generator_factory=self.trustset_generator,
            malicious_nodes=self.malicious_nodes
        )
        print(f"Status: {result}")


    def check_assumption_6(self):
        print("\nChecking assumption 6")
        result, error_message = check_assumption_6(
            node_states=self.node_states,
            trustset_generator_factory=self.trustset_generator,
            malicious_nodes=self.malicious_nodes,
            t_rep=5
        )
        print(f"Status: {result}")
        
        if not result:
            print(error_message)
        return result


    def check_assumptions(self):
        print(textwrap.dedent(f"""
            ===================================================================
            Honest nodes: {set(self.node_positions.keys()) - self.malicious_nodes}
            Malicious nodes: {self.malicious_nodes}
            ===================================================================
        """))

        self.check_assumption_1()
        self.check_assumption_2()
        self.check_assumption_3()
        self.check_assumption_4()        
        # self.check_assumption_5()
        self.check_assumption_6()


if __name__ == "__main__":
    import json
    from state_manager import State
    from graph import visualize_graph

    simulation_title = "java_14x10x12_1"

    state = State()
    state.load_simulation_data(f"../simulations/{simulation_title}_sim.csc")
    state.load_log_data(f"../simulations/{simulation_title}_log.txt")

    max_malicious = state.num_nodes() // 3 - 1

    state.generate_trustsets(fraction=2/3)
    state.create_malicious_parties(num_malicious=max_malicious)

    state.create_graph()
    
    # visualize_graph_3D(state.connectivity_graph, {}, {})
    # print(find_node_with_honest_neighbors(state.connectivity_graph, state.malicious_nodes))
    # visualize_graph_3D_with_click(state.connectivity_graph, {}, {})
    # visualize_graph(state.connectivity_graph, {}, {})
    
    state.check_assumptions()



    # for num_malicious in tqdm(range(max_malicious, 0, -1)):
    #     state.create_malicious_parties(num_malicious)
    #     state.create_graph()
    #     valid_nodes = find_node_with_honest_neighbors(state.connectivity_graph, state.malicious_nodes)

    #     if valid_nodes != 0:
    #         tqdm.write(f"Max malicious: {num_malicious}, {num_malicious / (14 * 10 * 12) * 100}%")
    #         tqdm.write(f"  Number of valid nodes: {valid_nodes}")
            
