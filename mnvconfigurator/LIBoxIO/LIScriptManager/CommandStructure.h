#ifndef COMMANDSTRUCTURE_H
#define COMMANDSTRUCTURE_H 1
#include <string>

namespace Minerva
{
	class CommandStructure
	{
		public:
			virtual ~CommandStructure() {};
			
			virtual bool Validate() = 0;
			virtual std::string ToString() = 0;
			virtual std::string Describe() = 0;
	};
};

#endif
