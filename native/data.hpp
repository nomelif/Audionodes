
#ifndef DATA_HPP
#define DATA_HPP

#include "common.hpp"
#include <map>

struct Data {
  virtual ~Data();

  template<class T>
  T& extract() {
    T *p = dynamic_cast<T*>(this);
    if (p != nullptr) {
      return *p;
    } else {
      // Data-object doesn't contain T, return empty dummy T instead
      return T::dummy;
    }
  }

  template<class T>
  const T& extract() const {
    const T *p = dynamic_cast<const T*>(this);
    if (p != nullptr) {
      return *p;
    } else {
      return T::dummy;
    }
  }
};

struct AudioData : public Data {
  Chunk mono;
  typedef std::vector<Chunk> PolyList;
  PolyList poly;
  void make_collapsed_version();
  AudioData(bool init = true);
  AudioData(PolyList);
  AudioData(Chunk);
  static AudioData dummy;
};

#endif
