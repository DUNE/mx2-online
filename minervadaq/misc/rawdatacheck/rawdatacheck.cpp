#include <iostream>
#include <string>
#include <iomanip>
#include <fstream>

std::ifstream::pos_type size;
char * memblock;

int main(int argc, char * argv[]) 
{

  if (argc != 2) {
    std::cout << "Usage : ./rawdatacheck <full path to file>" << std::endl;
    exit(0);
  }
  std::string fileName = argv[1];

  std::ifstream file ( fileName.c_str(), std::fstream::in|std::fstream::binary|std::fstream::ate);
  if (file.is_open())
  {
    size = file.tellg();
    memblock = new char [size];
    file.seekg(0, std::fstream::beg);
    file.read(memblock, size);
    file.close();

    std::cout << "Loaded the complete file content into memory..." << std::endl;
    for (unsigned int i = 0; i < (unsigned int)size; i+=2 ) {
      unsigned int j = i + 1;
      std::cout 
        << std::setfill('0') << std::setw( 2 ) << std::hex << (int)(memblock[i] & 0xFF) << " "
        << std::setfill('0') << std::setw( 2 ) << std::hex << (int)(memblock[j] & 0xFF) << " "
        << "\t"
        << std::setfill('0') << std::setw( 4 ) << std::dec << i << " " 
        << std::setfill('0') << std::setw( 4 ) << std::dec << j
        << std::endl;
    }

    delete[] memblock;
  }
  else std::cout << "Unable to open file!" << std::endl;;

  return 0;
}


