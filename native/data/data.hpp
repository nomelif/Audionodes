
#ifndef DATA_HPP
#define DATA_HPP

#include "common.hpp"
#include <map>

namespace audionodes {

struct Data {
  virtual ~Data();

  template<class T>
  static T& extract(Data* data) {
    T *p = dynamic_cast<T*>(data);
    if (p != nullptr) {
      return *p;
    } else {
      // Data-object doesn't contain T, return empty dummy T instead
      return T::dummy;
    }
  }

  template<class T>
  static const T& extract(const Data* data) {
    const T *p = dynamic_cast<const T*>(data);
    if (p != nullptr) {
      return *p;
    } else {
      return T::dummy;
    }
  }
  
  static Data dummy;
};

struct AudioData : public Data {
  Chunk mono;
  typedef std::vector<Chunk> PolyList;
  static const size_t default_reserve = 16;
  PolyList poly;
  void make_collapsed_version();
  AudioData(bool init = false, size_t reserve = default_reserve);
  AudioData(PolyList);
  AudioData(Chunk);
  static AudioData dummy;
  
  // Interface object to write polyphonic data, computes collapsed version
  // on destruction
  class PolyWriter {
    AudioData &bind;
    public:
    PolyList &internal;
    inline Chunk& operator[](size_t idx) {
      return internal[idx];
    }
    inline void resize(size_t size) {
      internal.resize(size);
    }
    PolyWriter(AudioData&);
    PolyWriter(AudioData&, size_t);
    ~PolyWriter();
  };
};

}

#endif
