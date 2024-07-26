#include "PathCache.h"
#include <queue>
#include <boost/graph/adjacency_list.hpp>
#include <boost/graph/graph_traits.hpp>
#include <boost/range/iterator_range.hpp>

bool PathCache::has_path(const Graph& G, Vertex start, Vertex end) {
    std::pair<Vertex, Vertex> key = std::make_pair(start, end);

    {
        std::shared_lock<std::shared_mutex> lock(cache_mutex);
        auto it = has_path_cache.find(key);
        if (it != has_path_cache.end()) {
            return it->second;
        }
    }

    std::unique_lock<std::shared_mutex> lock(cache_mutex);
    auto it = has_path_cache.find(key);
    if (it != has_path_cache.end()) {
        return it->second;
    }

    bool result = bfs_path_exists(G, start, end);
    has_path_cache[key] = result;
    return result;
}

std::vector<std::vector<Vertex>> PathCache::all_simple_paths(const Graph& G, Vertex start, Vertex end) {
    std::pair<Vertex, Vertex> key = std::make_pair(start, end);

    {
        std::shared_lock<std::shared_mutex> lock(cache_mutex);
        auto it = all_simple_paths_cache.find(key);
        if (it != all_simple_paths_cache.end()) {
            return it->second;
        }
    }

    std::unique_lock<std::shared_mutex> lock(cache_mutex);
    auto it = all_simple_paths_cache.find(key);
    if (it != all_simple_paths_cache.end()) {
        return it->second;
    }

    std::vector<Vertex> path;
    std::vector<std::vector<Vertex>> paths;
    std::vector<bool> visited(num_vertices(G), false);
    find_all_simple_paths_util(G, start, end, path, paths, visited);
    all_simple_paths_cache[key] = paths;
    return paths;
}

bool PathCache::bfs_path_exists(const Graph& G, Vertex start, Vertex end) {
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
