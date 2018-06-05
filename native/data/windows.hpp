
#ifndef DATA_WINDOWS_HPP
#define DATA_WINDOWS_HPP

#include "common.hpp"
#include "data/data.hpp"
#include "polyphony.hpp"
#include <memory>

namespace audionodes {

class NodeInputWindow {
  public:
  class Socket {
    friend class NodeInputWindow;
    friend class NodeTree;
    
    bool view_collapsed;
    AudioData *audio_cache = nullptr;
    Data *audio_cache_valid_for = nullptr;
    Data **data;
    const bool tmp_audio_data;
    void delete_temporary_data();
    
    template<class T>
    inline T& get_write() {
      return Data::extract<T>(data ? *data : nullptr);
    }
    
    public:
    Socket(Data**, bool, bool tmp_audio_data=false);
    template<class T = Data>
    inline const T& get() {
      return get_write<T>();
    }
    const Chunk& operator[](size_t idx);
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
  typedef std::vector<Data**> SocketsList;
  
  NodeOutputWindow();
  ~NodeOutputWindow();
  template<class T>
  inline T& get(size_t idx) {
    return Data::extract<T>(*sockets[idx]);
  }
  // Specialization of get for AudioData
  inline AudioData& operator[](size_t idx) {
    return Data::extract<AudioData>(*sockets[idx]);
  }
  inline Data** ref(size_t idx) {
    return idx < sockets.size() ? sockets[idx] : nullptr;
  }
  SocketsList sockets;
};

}

#endif
