#ifndef PATHCACHE_H
#define PATHCACHE_H

#include <vector>
#include <unordered_map>
#include <shared_mutex>
#include <boost/graph/adjacency_list.hpp>
#include <boost/functional/hash.hpp>

using Graph = boost::adjacency_list<boost::vecS, boost::vecS, boost::directedS>;
using Vertex = boost::graph_traits<Graph>::vertex_descriptor;

class PathCache {
public:
    PathCache() = default;
    bool has_path(const Graph& G, Vertex start, Vertex end);
    std::vector<std::vector<Vertex>> all_simple_paths(const Graph& G, Vertex start, Vertex end);

private:
    bool bfs_path_exists(const Graph& G, Vertex start, Vertex end);
    std::unordered_map<std::pair<Vertex, Vertex>, bool, boost::hash<std::pair<Vertex, Vertex>>> has_path_cache;
    std::unordered_map<std::pair<Vertex, Vertex>, std::vector<std::vector<Vertex>>, boost::hash<std::pair<Vertex, Vertex>>> all_simple_paths_cache;
    mutable std::shared_mutex cache_mutex;
};

#endif // PATHCACHE_H
