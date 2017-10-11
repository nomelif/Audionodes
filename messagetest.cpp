#include <iostream>
#include <queue>
#include <thread>         // std::this_thread::sleep_for
#include <chrono>         // std::chrono::seconds


extern "C"
{
  extern void push(std::queue<int>* target, int value){
    target->push(value);
  }
  extern std::queue<int> * allocate(){
    return new std::queue<int>();
  }
  extern void main_loop(std::queue<int>* queue){
    while(true){
        if(queue->size() == 0){
          std::this_thread::sleep_for(std::chrono::milliseconds(100));
        }else{
          int value = queue->front();
          queue->pop();
          std::cout << "<<<" << value << std::endl;
        }
    }
  }
}
