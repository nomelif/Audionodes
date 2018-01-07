
#ifndef DATA_WINDOWS_HPP
#define DATA_WINDOWS_HPP

#include "common.hpp"
#include "data.hpp"
#include "polyphony.hpp"
#include <memory>

class NodeInputWindow {
  public:
  class Socket {
    bool view_collapsed;
    AudioData *audio_cache = nullptr;
    Data *data;
    bool temporary_data;
    public:
    Socket(Data&, bool, bool temporary_data=false);
    template<class T = Data>
    inline const T& get() {
      return data ? data->extract<T>() : T::dummy;
    }
    const Chunk& operator[](size_t idx);
    void delete_temporary_data();
  };
  typedef std::vector<Socket> SocketsList;
  private:
  SocketsList sockets;
  public:
  Universe::Descriptor universes;
  size_t get_channel_amount();
  NodeInputWindow(SocketsList, Universe::Descriptor);
  inline Socket& operator[](size_t idx) {
    return sockets[idx];
  }
  ~NodeInputWindow();
};

class NodeOutputWindow {
  public:
  typedef std::vector<Data*> SocketsList;
  
  NodeOutputWindow(SocketsList);
  ~NodeOutputWindow();
  // The destructor shall only be called when NodeTree::evauluate() ends, not on
  // moves etc (using std::move() to push to node_outputs vector) -> default move ctor
  NodeOutputWindow(NodeOutputWindow&&) = default;
  inline Data& operator[](size_t idx) {
    return *sockets[idx];
  }
  private:
  SocketsList sockets;
};

#endif
