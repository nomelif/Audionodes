#include "data/windows.hpp"

NodeInputWindow::Socket::Socket(Data &data, bool view_collapsed, bool temporary_data) :
  view_collapsed(view_collapsed),
  data(&data),
  temporary_data(temporary_data)
{}

const Chunk& NodeInputWindow::Socket::operator[](size_t idx) {
  if (audio_cache == nullptr) {
    audio_cache = &data->extract<AudioData>();
  }
  if (view_collapsed || idx >= audio_cache->poly.size()) {
    return audio_cache->mono;
  } else {
    return audio_cache->poly[idx];
  }
}
void NodeInputWindow::Socket::delete_temporary_data() {
  if (temporary_data) delete data;
}

size_t NodeInputWindow::get_channel_amount() {
  return universes.input->get_channel_amount();
}

NodeInputWindow::NodeInputWindow(SocketsList sockets, Universe::Descriptor universes) :
  sockets(sockets),
  universes(universes)
{}
NodeInputWindow::~NodeInputWindow() {
  for (Socket &pane : sockets) {
    pane.delete_temporary_data();
  }
}

NodeOutputWindow::NodeOutputWindow(SocketsList sockets) :
  sockets(sockets)
{}

NodeOutputWindow::~NodeOutputWindow() {
  for (auto ptr : sockets) {
    delete ptr;
  }
}
