GETOPTPP_OBJECTS = getoptpp/getopt_pp.o
LIBSERIAL_OBJECTS =  libserial/src/SerialStream.o libserial/src/SerialStreamBuf.o 
# libserial/src/SerialPort.o libserial/src/PosixSignalDispatcher.o


OBJECTS = $(GETOPTPP_OBJECTS) $(LIBSERIAL_OBJECTS)

all : LIBoxIO

LIBoxIO : $(OBJECTS) LIBoxExceptions.cpp LIBoxExceptions.h LIBoxIO.cpp LIBoxIO.h main.cpp
	g++ -o LIBoxIO $(OBJECTS) LIBoxExceptions.cpp LIBoxIO.cpp main.cpp
	
getoptpp/getopt_pp.o : getoptpp/getopt_pp.h

libserial/src/SerialPort.o : libserial/src/SerialPort.h
libserial/src/SerialStream.o : libserial/src/SerialStream.h libserial/src/SerialStreamBuf.h libserial/src/SerialStreamBuf.cc
libserial/src/SerialStreamBuf.o : libserial/src/SerialStreamBuf.h
libserial/src/PosixSignalDispatcher.o : libserial/src/PosixSignalDispatcher.h libserial/src/PosixSignalHandler.h

