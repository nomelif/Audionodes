
#ifndef NODE_TREE_HPP
#define NODE_TREE_HPP

#include "common.hpp"
#include "node.hpp"
#include "polyphony.hpp"
#include "data_windows.hpp"

class NodeTree {
  public:
  struct ConstructionLink { // Used when building a new NodeTree on update
    node_uid from_node, to_node;
    size_t from_socket, to_socket;
  };
  struct Link { // Used during execution
    bool connected;
    size_t from_node, from_socket;
    Link(bool connected=false, size_t node=0, size_t socket=0);
  };
  
  private:
  size_t amount;
  std::vector<Node*> node_evaluation_order;
  std::vector<std::vector<Link>> links; // Link-edges to each node
  std::vector<Universe::Descriptor> node_polyphony_descriptors;
  void prepare_polyphony_universes();
  
  public:
  NodeTree(std::vector<Node*>, std::vector<std::vector<Link>>);
  Chunk evaluate();
};

#endif
