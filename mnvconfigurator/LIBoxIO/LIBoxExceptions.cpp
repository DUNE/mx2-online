#include "LIBoxExceptions.h"

#include <string>

namespace Minerva
{
	LIBoxFileException::LIBoxFileException(std::string filename)
	{
		file = filename;
	}

	const char * LIBoxFileException::what() const throw()
	{
		std::string temp = "Could not open file " + file + "...";
		return temp.c_str();
	}
	
};
