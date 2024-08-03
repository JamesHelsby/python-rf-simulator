import json
import textwrap
import concurrent.futures
from tqdm import tqdm
from graph import visualize_graph as dg


def check_assumption_1(node_positions, trustset_generator):
    total_combinations = trustset_generator.expected_combinations
    for trustset in tqdm(trustset_generator, total=total_combinations, desc="Assumption 1"):
        if not trustset.issubset(node_positions.keys()):
            missing_nodes = trustset - node_positions.keys()
            error_message = textwrap.indent(textwrap.dedent(f"""
                Not all members of all trustsets are graph nodes.

                Nodes {missing_nodes} in trustset {trustset} are not in simulation.
            """), ' ' * 4)
            return False, error_message

    return True, None


def check_assumption_2(trustset_generator, malicious_nodes):
    total_combinations = trustset_generator.expected_combinations
    for trustset in tqdm(trustset_generator, total=total_combinations, desc="Assumption 2"):
        if trustset.issubset(malicious_nodes):
            error_message = textwrap.indent(textwrap.dedent(f"""
                There is at least one pure malicious trustset.

                Trustset {trustset} has no honest nodes.

                Malicious nodes: {malicious_nodes}
            """), ' ' * 4)
            return False, error_message

    return True, None


def check_assumption_3(trustset_generator, malicious_nodes):
    total_combinations = trustset_generator.expected_combinations
    for trustset in tqdm(trustset_generator, total=total_combinations, desc="Assumption 3"):
        if trustset.isdisjoint(malicious_nodes):
            return True, None

    error_message = textwrap.indent(textwrap.dedent(f"""
        There is no pure honest trustset.

        Malicious nodes: {malicious_nodes}
    """), ' ' * 4)
    return False, error_message


def check_assumption_4(node_states, trustset_generator, malicious_nodes, t_rep):
    honest_nodes = set(node_states.keys()) - malicious_nodes
    fully_honest_nodes = set().union(*{trustset for trustset in trustset_generator if trustset.isdisjoint(malicious_nodes)})
    
    if len(fully_honest_nodes) == 0:
        return False, textwrap.indent("\nRequires Assumption 3.\n", ' ' * 4)

    for node in tqdm(honest_nodes):
        messages = node_states[node]['tx']
        for message in messages:
            attestations = message['attestations']
            if not any(attestation['attest_node'] in fully_honest_nodes for attestation in attestations):
                json_message = json.dumps(message, indent=2)
                json_message_indented = textwrap.indent(json_message, ' ' * 4)
                error_message = "\n" + textwrap.indent(textwrap.dedent(f"""
                    Not every honest node is connected to at least one pure honest trustset.

                    Node {node} did not receive any attestations from a pure honest trustset for message {message['message_num']}.
                    Fully honest nodes: {fully_honest_nodes}
                    Malicious nodes: {malicious_nodes}
                """).strip(), ' ' * 4) + f"\n{json_message_indented}\n"
                return False, error_message

    return True, None


def check_assumption_5(G, trustset_generator_factory, malicious_nodes):
    valid_nodes = {}
    assumption_validity = True
    tqdm_disable = True
    
    trustset_generator_1 = iter(trustset_generator_factory)
    trustset_generator_2 = iter(trustset_generator_factory)
    
    for C1 in tqdm(trustset_generator_1, total=trustset_generator_factory.expected_combinations, disable=tqdm_disable):
        for C2 in trustset_generator_2:
            if C1 != C2:
                valid_c1_found = False
                for c1 in C1:
                    all_neighbors_honest = True

                    if c1 in C2 and c1 not in malicious_nodes:
                        valid_c1_found = True
                        break

                    for neighbor in G.neighbors(c1):
                        if neighbor not in C2 or neighbor in malicious_nodes:
                            all_neighbors_honest = False
                            break

                    if all_neighbors_honest:
                        valid_c1_found = True
                        valid_nodes[(C1, C2)] = c1
                        break

                if not valid_c1_found:
                    valid_nodes[(C1, C2)] = None
                    dg(G, C1, C2)
                    assumption_validity = False
        
        trustset_generator_2 = iter(trustset_generator_factory)
                    
    return assumption_validity, valid_nodes


def check_assumption_5_fast(G, trustset_generator_factory, malicious_nodes):
    valid_nodes = {}
    assumption_validity = True
    tqdm_disable = False
    
    trustset_generator_1 = iter(trustset_generator_factory)
    trustset_generator_2 = iter(trustset_generator_factory)

    for C1 in tqdm(trustset_generator_1, total=trustset_generator_factory.expected_combinations, disable=tqdm_disable):
        for C2 in trustset_generator_2:
            if C1 != C2:
                valid_c1_found = False
                for c1 in C1:

                    if c1 in C2 and c1 not in malicious_nodes:
                        valid_c1_found = True
                        break

                if not valid_c1_found:
                    valid_nodes[(C1, C2)] = None
                    dg(G, C1, C2)
                    assumption_validity = False
        
        trustset_generator_2 = iter(trustset_generator_factory)
                    
    return assumption_validity, valid_nodes
   

def check_assumption_6(node_states, trustset_generator_factory, malicious_nodes, t_rep):
    honest_nodes = set(node_states.keys()) - malicious_nodes

    for node in malicious_nodes:
        messages = node_states[node]['tx']
        for message in messages:
            attestations = message['attestations']
            trustset_generator = iter(trustset_generator_factory)
            for trustset in trustset_generator:
                if not any(attestation['attest_node'] in (trustset & honest_nodes) for attestation in attestations):
                    json_message = json.dumps(message, indent=2)
                    json_message_indented = textwrap.indent(json_message, ' ' * 4)
                    error_message = "\n" + textwrap.indent(textwrap.dedent(f"""
                        Not every malicious node is connected to at least one honest node from each trustset.

                        Malicious node {node} did not receive any attestations from honest nodes in trustset {trustset} for message {message['message_num']}.
                    """).strip(), ' ' * 4) + f"\n{json_message_indented}\n"
                    return False, error_message

    return True, None
