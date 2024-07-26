import xml.etree.ElementTree as ET
import re
from collections import defaultdict
from tqdm import tqdm


def parse_simulation_file(file_path):
    tree = ET.parse(file_path)
    root = tree.getroot()
    
    node_positions = {}
    for node_type in root.findall(".//motetype"):
        for node in node_type.findall(".//mote"):
            position = node.find(".//interface_config/pos")
            node_id = node.find(".//interface_config/id")
            
            if position is not None and node_id is not None:
                node_id_int = int(node_id.text)
                node_positions[node_id_int] = (float(position.get('x')), float(position.get('y')),float(position.get('z')))
    
    radiomedium = root.find(".//radiomedium")
    transmitting_range = float(radiomedium.find(".//transmitting_range").text)
    interference_range = float(radiomedium.find(".//interference_range").text)
    
    return node_positions, transmitting_range, interference_range


def parse_timestamp(timestamp_str):
    minutes, seconds = map(float, timestamp_str.split(':'))
    total_seconds = minutes * 60 + seconds
    return {'minutes': int(minutes), 'seconds': seconds, 'total_seconds': total_seconds}


def parse_log_file(file_path):
    log_data = defaultdict(list)
    message_groups = defaultdict(list)
    node_states = defaultdict(lambda: {'tx': [], 'rx': []})

    # log_pattern = re.compile(  # C
    #     r'(?P<timestamp>\d+:\d+\.\d+)\tID:(?P<node_id>\d+)\t\[[A-Z]+: Node\s*\]\s*'
    #     r'(?P<action>[A-Za-z]+): \'(?P<message_num>\d+)\|(?P<origin_node>\d+)\|(?P<attest_node>\d+)\|(?P<broadcast_time>\d+)\''
    #     r'(?: from node: \'(?P<from_node>\d+)\')?\s*(?:->\s*(?P<comment>.*))?'
    # )

    log_pattern = re.compile(
        r'(?P<timestamp>\d+:\d+\.\d+)\s+ID:(?P<node_id>\d+)\s+'
        r'(?P<action>[A-Za-z]+): \'(?P<message_num>\d+)\|(?P<origin_node>\d+)\|(?P<attest_node>\d+)\|(?P<broadcast_time>\d+)\''
        r'(?: from node: \'(?P<from_node>\d+)\')?\s*(?:->\s*(?P<comment>.*))?'
    )

    with open(file_path, 'r') as file:
        total_lines = sum(1 for _ in file)
    
    with open(file_path, 'r') as file:
        for line in tqdm(file, total=total_lines):
            match = log_pattern.match(line)
            if match:
                log_entry = match.groupdict()
                
                # log_entry['timestamp'] = float(log_entry['timestamp'].replace(':', ''))
                # log_entry['timestamp'] = parse_timestamp(log_entry['timestamp'])
                log_entry['node_id'] = int(log_entry['node_id'])
                log_entry['message_num'] = int(log_entry['message_num'])
                log_entry['origin_node'] = int(log_entry['origin_node'])
                log_entry['attest_node'] = int(log_entry['attest_node'])
                log_entry['broadcast_time'] = int(log_entry['broadcast_time'])
                if log_entry['from_node'] is not None:
                    log_entry['from_node'] = int(log_entry['from_node'])
                
                # log_data[log_entry['node_id']].append(log_entry)
                
                # message_key = (log_entry['message_num'], log_entry['origin_node'], log_entry['attest_node'])
                # message_groups[message_key].append(log_entry)
                
                node_id = log_entry['node_id']
                action = log_entry['action'].lower()
                
                if action == 'tx':
                    node_states[node_id]['tx'].append({
                        'timestamp': log_entry['timestamp'],
                        'message_num': log_entry['message_num'],
                        'broadcast_time': log_entry['broadcast_time'],
                        'attestations': []
                    })

                elif action == 'rx':
                    node_states[node_id]['rx'].append({
                        'timestamp': log_entry['timestamp'],
                        'message_num': log_entry['message_num'],
                        'origin_node': log_entry['origin_node'],
                        'attest_node': log_entry['attest_node'],
                        'from_node': log_entry.get('from_node'),
                        'broadcast_time': log_entry['broadcast_time']
                    })
                    
                    # Update attestations for corresponding tx entries
                    if log_entry['origin_node'] == node_id and log_entry['attest_node'] != 0:
                        for tx_entry in node_states[node_id]['tx']:
                            attestations = tx_entry['attestations']
                            if not any(att['attest_node'] == log_entry['attest_node'] for att in attestations):
                                tx_entry['attestations'].append({
                                    'timestamp': log_entry['timestamp'],
                                    'attest_node': log_entry['attest_node']
                                })
                
    return log_data, message_groups, node_states


"""
pos_dict
{
    node_id_1: (x_coordinate_1, y_coordinate_1, z_coordinate_1),  # int: (float, float, float)
    node_id_2: (x_coordinate_2, y_coordinate_2, z_coordinate_2),  # int: (float, float, float)
    # More nodes...
}

log_data:
{
    node_id_1: [  # int
        {
            'timestamp': float,  # The timestamp of the log entry
            'node_id': int,      # The ID of the node that logged this entry
            'action': str,       # The action type (e.g., 'Tx', 'Rx', 'Bx', 'Ax')
            'message_num': int,  # The message number
            'origin_node': int,  # The origin node that created the message
            'attest_node': int,  # The node that attested the message
            'from_node': int     # The node from which the message was received (if applicable)
        },
        # More log entries for node 1...
    ],
    # More nodes...
}

message_groups:
{
    (message_num, origin_node, attest_node): [  # (int, int, int)
        {
            'timestamp': float,     # The timestamp of the log entry
            'node_id': int,         # The ID of the node that logged this entry
            'action': str,          # The action type (e.g., 'Tx', 'Rx', 'Bx', 'Ax')
            'message_num': int,     # The message number
            'origin_node': int,     # The origin node that created the message
            'attest_node': int,     # The node that attested the message
            'broadcast_time': int,  # The broadcast time
            'from_node': int        # The node from which the message was received (if applicable)
        },
        # More log entries for this message...
    ],
    # More messages...
}

node_states:
{
    node_id_1: {  # int
        'tx': [   # List of transmission events
            {
                'timestamp': float,     # The timestamp of the log entry
                'message_num': int,     # The message number
                'broadcast_time': int,  # The broadcast time
                'attestations': [  # List of attestations received for this message
                    {
                        'timestamp': float,  # The timestamp the attestation was received
                        'attest_node': int   # The node that attested the message
                    },
                    # More attestations...
                ]
            },
            # More transmission events...
        ],
        'rx': [  # List of reception events
            {
                'timestamp': float,    # The timestamp of the log entry
                'message_num': int,    # The message number
                'origin_node': int,    # The origin node that created the message
                'attest_node': int,    # The node that attested the message
                'from_node': int,      # The node from which the message was received (if applicable)
                'broadcast_time': int  # The broadcast time
            },
            # More reception events...
        ]
    },
    # More nodes...
}
"""
