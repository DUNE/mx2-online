all: LIScriptManager

COMMANDS=Commands/*.cpp
BLOCKS=Blocks/*.cpp
SCRIPTS=Scripts/*.cpp

LIScriptManager: $(COMMANDS) $(BLOCKS) $(SCRIPTS) main.cpp
	g++ -o LIScriptManager $(COMMANDS) $(BLOCKS) $(SCRIPTS) ../LIBoxExceptions.cpp main.cpp
