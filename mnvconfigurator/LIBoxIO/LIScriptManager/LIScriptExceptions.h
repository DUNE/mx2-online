#ifndef LISCRIPTEXCEPTIONS_H
#define LISCRIPTEXCEPTIONS_H 1

#include "Blocks/BlockTypes.h"
#include "Commands/CommandTypes.h"

#include <stdexcept>

namespace Minerva
{
	// --------------------------------------------------------------------
	// LIScriptException: base class for LI script exceptions.
	// --------------------------------------------------------------------
	
	class LIScriptException: public std::exception
	{
		virtual const char * what() const throw() {};
	};

	class LIScriptCommandNotAllowedException : public LIScriptException
	{
		virtual const char * what() const throw()
		{
			return "Error: this command is not allowed here.";
		}
	};

	class LIScriptBlockNotAllowedException : public LIScriptException
	{
		virtual const char * what() const throw()
		{
			return "Error: this command block is not allowed here.";
		}
	};

	class LIScriptInvalidBlockException : public LIScriptException
	{
		public:
			virtual ~LIScriptInvalidBlockException() throw() {};
			LIScriptInvalidBlockException(CommandBlockType type);
			virtual const char * what() const throw();
		private:
			LIScriptInvalidBlockException();
			CommandBlockType blockType;
	};

	class LIScriptBlockCommandRequirementNotSatisfied : public LIScriptException
	{
		public:
			virtual ~LIScriptBlockCommandRequirementNotSatisfied() throw() {};
			LIScriptBlockCommandRequirementNotSatisfied(CommandBlockType bt, CommandType ct);
			virtual const char * what() const throw();
		private:
			LIScriptBlockCommandRequirementNotSatisfied();
			CommandType commandType;
			CommandBlockType blockType;
	
	};

	class LIScriptBlockTooManyCommands : public LIScriptException
	{
		public:
			virtual ~LIScriptBlockTooManyCommands() throw() {};
			LIScriptBlockTooManyCommands(CommandBlockType blocktype, CommandType ct, int num);
			virtual const char * what() const throw();
		private:
			LIScriptBlockTooManyCommands();
			CommandType commandType;
			CommandBlockType blockType;
			int maxNum;
	
	};

	class LIBoxCommandNotCompatibleException : public LIScriptException
	{
		public:
			virtual ~LIBoxCommandNotCompatibleException() throw() {};
			LIBoxCommandNotCompatibleException(CommandBlockType blocktype, CommandType ct);
			virtual const char * what() const throw();
		private:
			LIBoxCommandNotCompatibleException();
			CommandType commandType;
			CommandBlockType blockType;
	
	};

	class LIScriptCommandExcludedException : public LIScriptException
	{
		public:
			virtual ~LIScriptCommandExcludedException() throw() {};
			LIScriptCommandExcludedException(CommandType ct, CommandType ect, int pos);
			virtual const char * what() const throw();
		private:
			LIScriptCommandExcludedException();
			CommandType commandType;
			CommandType excludedCommandType;
			int position;
	
	};

	class LIScriptMissingRequiredCommandException : public LIScriptException
	{
		public:
			virtual ~LIScriptMissingRequiredCommandException() throw() {};
			LIScriptMissingRequiredCommandException(CommandType ct, CommandType rct);
			virtual const char * what() const throw();
		private:
			LIScriptMissingRequiredCommandException();
			CommandType commandType;
			CommandType requiredCommandType;
	
	};

	class LIScriptCommandListTooSmallException : public LIScriptException
	{
		public:
			virtual ~LIScriptCommandListTooSmallException() throw() {};
			LIScriptCommandListTooSmallException(CommandType ct);
			virtual const char * what() const throw();
		private:
			LIScriptCommandListTooSmallException();
			CommandType commandType;
			CommandType requiredCommandType;
	
	};

	class LIScriptCommandOutOfPlaceException : public LIScriptException
	{
		public:
			virtual ~LIScriptCommandOutOfPlaceException() throw() {};
			LIScriptCommandOutOfPlaceException(CommandType ct, CommandType rct, CommandType fct, int pos);
			virtual const char * what() const throw();
		private:
			LIScriptCommandOutOfPlaceException();
			CommandType commandType;
			CommandType requiredCommandType;
			CommandType foundCommandType;
			int position;
	
	};

};

#endif
