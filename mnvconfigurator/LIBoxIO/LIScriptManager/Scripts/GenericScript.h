#ifndef GENERICSCRIPT_H
#define GENERICSCRIPT_H 1

#include "CommandScript.h"
#include "GenericScriptGrammar.h"

#include <string>

namespace Minerva
{
	class GenericScript : public CommandScript
	{
		public:
			GenericScript();
		
			std::string Describe()  { return std::string("Any old LI box script."); };
			
		private:
			// this guy allows us to avoid making one copy of the grammar for each object we instantiate.
			static GenericScriptGrammar * class_grammar;
	};
};

#endif
