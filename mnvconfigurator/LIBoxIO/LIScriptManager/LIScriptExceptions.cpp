#include "LIScriptExceptions.h"
#include "Blocks/BlockTypes.h"

#include <sstream>

namespace Minerva
{
	LIScriptCommandNotAllowedException::LIScriptCommandNotAllowedException(CommandType ct, CommandBlockType bt)
	   : commandType(ct), blockType(bt)
	{	}
	
	const char * LIScriptCommandNotAllowedException::what() const throw()
	{
		std::stringstream out;
		out << "Error: this command (type " << commandType <<") is not allowed here (thrown by block of type " << blockType << ").";
		return out.str().c_str();
	}

	LIScriptInvalidBlockException::LIScriptInvalidBlockException(CommandBlockType type)
	{
		blockType = type;
	}
	
	const char * LIScriptInvalidBlockException::what() const throw()
	{
		std::stringstream out;
		out << "Error: this command block (type " << blockType << ") is invalid.";
		return out.str().c_str();
	}

	LIScriptBlockCommandRequirementNotSatisfied::LIScriptBlockCommandRequirementNotSatisfied(CommandBlockType bt, CommandType ct)
	   : blockType(bt), commandType(ct)
	{}
	
	const char * LIScriptBlockCommandRequirementNotSatisfied::what() const throw()
	{
		std::stringstream out;
		out << "Error: command block (type " << blockType << ") requires missing command (type " << commandType << ")...";
		return out.str().c_str();
	}

	LIScriptBlockTooManyCommands::LIScriptBlockTooManyCommands(CommandBlockType bt, CommandType ct, int num)
	   : blockType(bt), commandType(ct), maxNum(num)
	{}
	
	const char * LIScriptBlockTooManyCommands::what() const throw()
	{
		std::stringstream out;
		out << "Error: too many of command (type " << commandType <<") in command block (type " << blockType << "): maximum allowed is " << maxNum;
		return out.str().c_str();
	}
	
	LIBoxCommandNotCompatibleException::LIBoxCommandNotCompatibleException(CommandBlockType bt, CommandType ct)
	   : blockType(bt), commandType(ct)
	{}
	
	const char * LIBoxCommandNotCompatibleException::what() const throw()
	{
		std::stringstream out;
		out << "Error: command (type " << commandType <<") is incompatible with command list in command block (type " << blockType << ")...";
		return out.str().c_str();
	}

	LIScriptCommandExcludedException::LIScriptCommandExcludedException(CommandType ct, CommandType ect, int pos)
	   : commandType(ct), excludedCommandType(ect), position(pos)
	{}

	const char * LIScriptCommandExcludedException::what() const throw()
	{
		std::stringstream out;
		out << "Error: command (type " << commandType <<") at position " << position << " excludes command (type " << excludedCommandType << ")...";
		return out.str().c_str();
	}

	LIScriptMissingRequiredCommandException::LIScriptMissingRequiredCommandException(CommandType ct, CommandType rct)
	   : commandType(ct), requiredCommandType(rct)
	{}

	const char * LIScriptMissingRequiredCommandException::what() const throw()
	{
		std::stringstream out;
		out << "Error: required command (type " << requiredCommandType <<") required by command (type " << commandType << ") is missing...";
		return out.str().c_str();
	}

	LIScriptCommandListTooSmallException::LIScriptCommandListTooSmallException(CommandType ct)
	   : commandType(ct)
	{}

	const char * LIScriptCommandListTooSmallException::what() const throw()
	{
		std::stringstream out;
		out << "Error: command list is too small for requirements of command (type " << commandType <<")...";
		return out.str().c_str();
	}
	LIScriptCommandOutOfPlaceException::LIScriptCommandOutOfPlaceException(CommandType ct, CommandType rct, CommandType fct, int pos)
	   : commandType(ct), requiredCommandType(rct), foundCommandType(fct), position(pos)
	{}

	const char * LIScriptCommandOutOfPlaceException::what() const throw()
	{
		std::stringstream out;
		out << "Error: command (type " << requiredCommandType <<") required by command (type " << commandType <<") is not at position " << position << ".  Found command (type " << foundCommandType << ") instead...";
		return out.str().c_str();
	}

};
