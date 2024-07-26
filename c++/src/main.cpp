#include <iostream>
#include <fstream>
#include <vector>
#include <queue>
#include <unordered_set>
#include <unordered_map>
#include <boost/graph/adjacency_list.hpp>
#include <boost/graph/breadth_first_search.hpp>
#include <boost/graph/visitors.hpp>
#include <boost/functional/hash.hpp>
#include <nlohmann/json.hpp>

using json = nlohmann::json;
using namespace boost;

struct EdgeProperties {
    int weight;
};

using Graph = adjacency_list<vecS, vecS, undirectedS, no_property, EdgeProperties>;
using Vertex = graph_traits<Graph>::vertex_descriptor;
using Edge = graph_traits<Graph>::edge_descriptor;

struct GraphData {
    Graph G;
    std::vector<std::unordered_set<int>> trustsets;
    std::unordered_set<int> malicious_nodes;
};

namespace std {
    template <>
    struct hash<std::pair<int, int>> {
        size_t operator()(const std::pair<int, int>& p) const {
            auto hash1 = std::hash<int>{}(p.first);
            auto hash2 = std::hash<int>{}(p.second);
            return hash1 ^ (hash2 << 1);
        }
    };
}

GraphData deserialize_graph_and_data(const std::string& filename) {
    std::ifstream file(filename);
    json data;
    file >> data;

    Graph G;
    std::unordered_map<int, Vertex> node_map;
    for (const auto& node : data["nodes"]) {
        Vertex v = add_vertex(G);
        node_map[node] = v;
    }

    for (const auto& edge : data["edges"]) {
        add_edge(node_map[edge[0]], node_map[edge[1]], EdgeProperties{1}, G);
    }

    std::vector<std::unordered_set<int>> trustsets;
    for (const auto& trustset : data["trustsets"]) {
        std::unordered_set<int> ts;
        for (const auto& node : trustset) {
            ts.insert(node.get<int>());
        }
        trustsets.push_back(ts);
    }

    std::unordered_set<int> malicious_nodes;
    for (const auto& node : data["malicious_nodes"]) {
        malicious_nodes.insert(node.get<int>());
    }

    return {G, trustsets, malicious_nodes};
}

void find_all_simple_paths(const Graph& G, Vertex start, Vertex end, std::vector<Vertex>& path, std::vector<std::vector<Vertex>>& paths, std::vector<bool>& visited) {
    path.push_back(start);
    visited[start] = true;

    if (start == end) {
        paths.push_back(path);
    } else {
        for (auto edge : boost::make_iterator_range(out_edges(start, G))) {
            Vertex next = target(edge, G);
            if (!visited[next]) {
                find_all_simple_paths(G, next, end, path, paths, visited);
            }
        }
    }

    path.pop_back();
    visited[start] = false;
}

std::vector<std::vector<Vertex>> get_all_simple_paths(const Graph& G, Vertex start, Vertex end) {
    std::vector<std::vector<Vertex>> paths;
    std::vector<Vertex> path;
    std::vector<bool> visited(num_vertices(G), false);
    find_all_simple_paths(G, start, end, path, paths, visited);
    return paths;
}

class PathCache {
public:
    PathCache() = default;

    bool has_path(const Graph& G, Vertex start, Vertex end) {
        auto key = std::make_pair(start, end);
        auto it = has_path_cache.find(key);
        if (it != has_path_cache.end()) {
            return it->second;
        }
        bool result = bfs_path_exists(G, start, end);
        has_path_cache[key] = result;
        return result;
    }

    std::vector<std::vector<Vertex>> all_simple_paths(const Graph& G, Vertex start, Vertex end) {
        auto key = std::make_pair(start, end);
        auto it = all_simple_paths_cache.find(key);
        if (it != all_simple_paths_cache.end()) {
            return it->second;
        }
        std::vector<std::vector<Vertex>> paths = get_all_simple_paths(G, start, end);
        all_simple_paths_cache[key] = paths;
        return paths;
    }

private:
    bool bfs_path_exists(const Graph& G, Vertex start, Vertex end) {
        std::queue<Vertex> queue;
        std::vector<bool> visited(num_vertices(G), false);
        queue.push(start);
        visited[start] = true;

        while (!queue.empty()) {
            Vertex current = queue.front();
            queue.pop();

            if (current == end) {
                return true;
            }

            for (auto edge : boost::make_iterator_range(out_edges(current, G))) {
                Vertex next = target(edge, G);
                if (!visited[next]) {
                    queue.push(next);
                    visited[next] = true;
                }
            }
        }
        return false;
    }

    std::unordered_map<std::pair<Vertex, Vertex>, bool, boost::hash<std::pair<Vertex, Vertex>>> has_path_cache;
    std::unordered_map<std::pair<Vertex, Vertex>, std::vector<std::vector<Vertex>>, boost::hash<std::pair<Vertex, Vertex>>> all_simple_paths_cache;
};

bool check_assumption_5_in_cpp(const GraphData& graph_data, std::unordered_map<std::pair<int, int>, std::unordered_map<int, std::set<std::pair<int, int>>>>& valid_nodes) {
    const Graph& G = graph_data.G;
    const auto& trustsets = graph_data.trustsets;
    const auto& malicious_nodes = graph_data.malicious_nodes;

    PathCache cache;

    auto contains_honest_member = [&](const std::vector<Vertex>& path, const std::unordered_set<int>& trustset) {
        for (const auto& node : path) {
            if (trustset.count(node) && !malicious_nodes.count(node)) {
                return true;
            }
        }
        return false;
    };

    for (size_t i = 0; i < trustsets.size(); ++i) {
        for (size_t j = 0; j < trustsets.size(); ++j) {
            if (i == j) continue;

            const auto& C1 = trustsets[i];
            const auto& C2 = trustsets[j];
            bool valid_node_found = false;

            for (const auto& c1 : C1) {
                bool all_paths_valid = true;
                std::set<std::pair<int, int>> paths;

                for (const auto& source : boost::make_iterator_range(vertices(G))) {
                    if (source == c1) continue;

                    if (cache.has_path(G, source, c1)) {
                        auto simple_paths = cache.all_simple_paths(G, source, c1);
                        for (const auto& path : simple_paths) {
                            if (!contains_honest_member(path, C2)) {
                                all_paths_valid = false;
                                break;
                            }

                            paths.emplace(path.front(), path.back());
                        }

                        if (!all_paths_valid) break;
                    }
                }

                if (all_paths_valid) {
                    valid_node_found = true;
                    valid_nodes[{i, j}][c1] = paths;

                    // std::cout << i << ", " << j << " -> " << std::endl;
                    for (const std::pair<int, int>& path : paths) {
                        // std::cout << "=>" << path.first << " " << path.second << std::endl;
                    }

                    break;
                }
            }

            if (!valid_node_found) {
                valid_nodes[{i, j}] = std::unordered_map<int, std::set<std::pair<int, int>>>{};
                return false;
            }
        }
    }
    return true;
}

void save_valid_nodes_to_json(const std::unordered_map<std::pair<int, int>, std::unordered_map<int, std::set<std::pair<int, int>>>>& valid_nodes, const std::string& filename) {
    json j;

    for (const auto& outer_pair : valid_nodes) {
        int i = outer_pair.first.first;
        int j_val = outer_pair.first.second;

        for (const auto& inner_pair : outer_pair.second) {
            int c1 = inner_pair.first;

            for (const auto& path_pair : inner_pair.second) {
                j[std::to_string(i)][std::to_string(j_val)][std::to_string(c1)].push_back({path_pair.first, path_pair.second});
            }
        }
    }

    std::ofstream file(filename);
    file << j.dump(2);
}

int main(int argc, char* argv[]) {
    if (argc < 2) {
        std::cerr << "Usage: " << argv[0] << " <data_file>" << std::endl << std::flush;
        return 1;
    }

    std::string data_file = argv[1];
    std::cout << "============================ Start C++ ============================" << std::endl << std::flush;

    GraphData graph_data = deserialize_graph_and_data(data_file);

    std::unordered_map<std::pair<int, int>, std::unordered_map<int, std::set<std::pair<int, int>>>> valid_nodes;
    bool result = check_assumption_5_in_cpp(graph_data, valid_nodes);

    save_valid_nodes_to_json(valid_nodes, "c++/valid_nodes.json");

    if (result) {
        std::cout << "Assumption 5 is valid" << std::endl << std::flush;
    } else {
        std::cout << "Assumption 5 is not valid" << std::endl << std::flush;
    }

    std::cout << "============================= End C++ =============================" << std::endl << std::flush;
    return 0;
}
