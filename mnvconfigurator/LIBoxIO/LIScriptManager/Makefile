all: LIScriptManager

COMMANDS=Commands/*.cpp
BLOCKS=Blocks/*.cpp

LIScriptManager: $(COMMANDS) $(BLOCKS) CommandScript.cpp main.cpp
	g++ -o LIScriptManager $(COMMANDS) $(BLOCKS) ../LIBoxExceptions.cpp main.cpp
