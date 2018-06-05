#include "data/windows.hpp"

namespace audionodes {

NodeInputWindow::Socket::Socket(Data **data, bool view_collapsed, bool tmp_audio_data) :
  view_collapsed(view_collapsed),
  data(data),
  tmp_audio_data(tmp_audio_data)
{}

const Chunk& NodeInputWindow::Socket::operator[](size_t idx) {
  if (audio_cache == nullptr || audio_cache_valid_for != *data) {
    audio_cache = &get_write<AudioData>();
    audio_cache_valid_for = *data;
  }
  if (view_collapsed || idx >= audio_cache->poly.size()) {
    return audio_cache->mono;
  } else {
    return audio_cache->poly[idx];
  }
}
void NodeInputWindow::Socket::delete_temporary_data() {
  if (tmp_audio_data) {
    delete *data;
    delete data;
  }
}

size_t NodeInputWindow::get_channel_amount() {
  return universes.input->get_channel_amount();
}

NodeInputWindow::NodeInputWindow(SocketsList sockets, Universe::Descriptor universes) :
  sockets(sockets),
  universes(universes)
{}
NodeInputWindow::~NodeInputWindow() {
  for (Socket &socket : sockets) {
    socket.delete_temporary_data();
  }
}

NodeOutputWindow::NodeOutputWindow() {}

NodeOutputWindow::~NodeOutputWindow() {
  for (auto ptr : sockets) {
    delete *ptr;
    delete ptr;
  }
}

}
