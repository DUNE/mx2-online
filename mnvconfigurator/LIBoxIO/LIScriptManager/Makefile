all: LIScriptManager

COMMANDS=Commands/*.cpp 
BLOCKS=Blocks/*.cpp
SCRIPTS=Scripts/*.cpp

../getoptpp/getopt_pp.o : ../getoptpp/getopt_pp.h ../getoptpp/getopt_pp.cpp
GETOPTPP_OBJECTS = ../getoptpp/getopt_pp.o
OBJECTS = $(GETOPTPP_OBJECTS)

%.cpp : %.h

LIScriptManager: $(OBJECTS) $(COMMANDS) $(BLOCKS) $(SCRIPTS) LIScriptExceptions.cpp main.cpp
	g++ -o LIScriptManager $(OBJECTS) $(COMMANDS) $(BLOCKS) $(SCRIPTS) LIScriptExceptions.cpp main.cpp
