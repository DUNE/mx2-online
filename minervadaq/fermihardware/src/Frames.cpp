#ifndef Frames_cpp
#define Frames_cpp

#include <iomanip>
#include "Frames.h"
#include "exit_codes.h"

/*********************************************************************************
 * Class for creating FPGA Frame header objects for use with the 
 * MINERvA data acquisition system and associated software projects.
 *
 * Elaine Schulte, Rutgers University
 * Gabriel Perdue, The University of Rochester
 **********************************************************************************/

/*! all of these values are in bytes */
const int Frames::MinHeaderLength=9; //size (in bytes) of an outgoing FPGA header for ANY device
const int Frames::NDiscrChPerTrip=16;

#if V81FIRMWARE||V83FIRMWARE||V85FIRMWARE
const int Frames::ADCFrameLength=875; //bytes of course (dpm pointer should be this +2)
#endif
#if (V90FIRMWARE)||(V91FIRMWARE)
const int Frames::ADCFrameLength=443; //bytes of course (dpm pointer should be this +2)
#endif

// log4cpp category hierarchy.
log4cpp::Category& framesLog = log4cpp::Category::getInstance(std::string("frames"));

Frames::Frames(log4cpp::Appender* appender) 
{ 
	/*! \fn 
	 * The basic constructor sets the FrameID bytes and sets the log4cpp appender to null.
	 */
	// These don't seem to need a value...
	FrameID[0]   = 0x00; 
	FrameID[1]   = 0x00; //initialize the frame id to no value
	frmsAppender = appender;
	if (frmsAppender == 0 ) {
		std::cout << "FEB Log Appender is NULL!" << std::endl;
		exit(EXIT_FEB_UNSPECIFIED_ERROR);
	}
	framesLog.setPriority(log4cpp::Priority::DEBUG);
}


void Frames::MakeDeviceFrameTransmit(Devices dev,Broadcasts b, Directions d, 
		unsigned int f, unsigned int feb) 
{
	/*! \fn********************************************************************************
	 * a function which makes up an FPGA frame for transmitting information from
	 * the data acquisition routines to the FPGA on the front end board (FEB) and
	 * on to the requested device.
	 *
	 * Inputs:
	 *
	 * \param dev:  The device to which the message is destined
	 * \param b: whether or not this is a broadcast request
	 * \param d: the direction of the message:  either master-to-slave (true for transmit) or
	 *    slave-to-master (receive)
	 * \param f: the device function.  This is specific to the device (dev) receiving the message
	 * \param feb: the number of the FEB to which this frame is destined
	 *********************************************************************************/

	/* set up the basics of the header */
	broadcastCommand[0]= (unsigned char) b;
	messageDirection[0] = (unsigned char) d;
	targetDevice[0] = (unsigned char) dev; 
	deviceFunction[0] = (unsigned char) f;
	febNumber[0] = (unsigned char) feb;

	/* with those in hand, let's make up the header */
	MakeHeader();
}

void Frames::MakeHeader() 
{
	/*! \fn********************************************************************************
	 * a function which packs FPGA frame header data for transmitting information from
	 * the data acquisition routines to the FPGA on the front end board (FEB) and
	 * on to the requested device.
	 *********************************************************************************/

	/* we've done all the conversion & stuff so we can make up the frame header now! */
	/* word 1: the broadcast direction, command, and feb number */
	frameHeader[0] = (messageDirection[0] & 0x80 ); //The direction bit is in bit 7 of word 1
	frameHeader[0] |= (broadcastCommand[0] & 0xF0); //The broadcast command is in bits 4-6
	frameHeader[0] |= (febNumber[0] & 0x0F); //the feb number is bits 0-3

	/* word 2:  target device & its function */
	frameHeader[1] = (targetDevice[0] & 0xF0); //the target device is in bits 4-7
	frameHeader[1] |= (deviceFunction[0] & 0x0F); //the function is in bits 0-3

	/* word 3:  reserved for response information */
	frameHeader[2] = 0x00; //initialize to null

	/* word 4 & 5:  frame ID (whatever that does) */
	frameHeader[3] = FrameID[0]; frameHeader[4] = FrameID[1];

	/* words 5 - 8 are reserved for response information */
	frameHeader[5] = frameHeader[6] = frameHeader[7] = frameHeader[8] = 0x00; //initialize them to null
}

// Each class which inherits frames makes its own messages!
void Frames::MakeMessage() { std::cout << "Hi Elaine!" << std::endl;} 

bool Frames::CheckForErrors() 
{
	/*! \fn bool Frames::CheckForErrors()
	 * Check incoming frame header data for errors.
	 */
	bool errors[10], error;
	error = false; //initialize error 
	for (int i=0;i<10;i++) {
		errors[i] = false; //initialize error array
	}

	ResponseWords word; //which word of the message do we check
	ResponseFlags flag; //what status bits are we checking

	/* we are looking to see if any of the various bits are set */
	unsigned char messageLength[2];
	word = ResponseLength0;
	messageLength[0] = message[word];
	word = ResponseLength1;
	messageLength[1] = message[word];

	word = FrameStart; flag = Direction; //check direction
	errors[0] = !(message[word] & flag); 
	if (errors[0]) {
		error = true; 
		framesLog.errorStream()<<"CheckForErrors: Direction: "<<errors[0];
	}

	word = DeviceStatus; flag = DeviceOK; //check status
	errors[1] = !(message[word] & flag);
	if (errors[1]) {
		error = true; 
		framesLog.errorStream()<<"CheckForErrors: DeviceOK: "<<errors[1];
	}

	word = DeviceStatus; flag = FunctionOK; //check execution status
	errors[2] = !(message[word]&flag);
	if (errors[2]) {
		error = true; 
		framesLog.errorStream()<<"CheckForErrors: FunctionOK: "<<errors[2];
	}

	word = FrameStatus; flag = CRCOK; //check CRC error bit
	errors[3] = !(message[word] & flag);
	if (errors[3]) {
		error = true; 
		framesLog.errorStream()<<"CheckForErrors: CRCOK: "<<errors[3];
	}

	word = FrameStatus; flag = EndHeader; //message ended properly
	errors[4] = !(message[word] & flag);
	if (errors[4]) {
		error = true; 
		framesLog.errorStream()<<"CheckForErrors: EndHeader: "<<errors[4];
	}

	word = FrameStatus; flag = MaxLen; //message exceeded maximum message length
	errors[5] = (message[word] & flag);
	if (errors[5]) {
		error = true; 
		framesLog.errorStream()<<"CheckForErrors: MaxLen: "<<errors[5];
	}

	word = FrameStatus; flag = SecondStart;
	errors[6] = (message[word] & flag);
	if (errors[6]) {
		error = true; 
		framesLog.errorStream()<<"CheckForErrors: SecondStart: "<<errors[6];
	}

	word = FrameStatus; flag = NAHeader;
	errors[7] = (message[word] & flag);
	if (errors[7]) {
		error = true; 
		framesLog.errorStream()<<"CheckForErrors: NAHeader: "<<errors[7];
	}

	return false; // let everything through for now...
	//	return error; // true if *any* error was found!
}


void Frames::DecodeHeader() 
{
	/*! \fn 
	 * extract device information from the FPGA header sent back from
	 * the electronics by a read request.
	 *
	 * note:  these should be decoded using the enumerated types in 
	 * FrameTypes.h 
	 */
#if DEBUG_VERBOSE
	std::cout << " Entering Frames::DecodeHeader..." << std::endl;
#endif
	ResponseWords word;

	word = FrameStart; 
	febNumber[0] = (message[word]&0x0F); //extract the feb board number from which this message came
#if DEBUG_VERBOSE
	std::cout << "  message at framestart: " << (int)message[word] << std::endl;
#endif
	broadcastCommand[0] = (message[word]&0xF0); //extract the broadcast command
	messageDirection[0] = (message[word]&0x80); //get the message direction
#if DEBUG_VERBOSE
	std::cout << "  direction: " << (int)(message[word]&0x80) << std::endl;
#endif
	word = DeviceStatus;
	deviceFunction[0] = (message[word]&0x0F); // extract the device function executed 
	targetDevice[0]   = (message[word]&0xF0); // extract the device which responded
}

void Frames::printMessageBufferToLog( int buffersize )
{
	framesLog.debugStream() << "Printing message buffer of size = " << buffersize;
	if (buffersize > 0) 
		for (int i=0; i<buffersize; i+=2 ) {
			int j = i + 1;
			framesLog.debugStream() 
				<< std::setfill('0') << std::setw( 2 ) << std::hex << (int)message[i] << " " 
				<< std::setfill('0') << std::setw( 2 ) << std::hex << (int)message[j] << " " 
				<< "\t" 
				<< std::setfill('0') << std::setw( 4 ) << std::dec << i << " " 
				<< std::setfill('0') << std::setw( 4 ) << std::dec << j;
			
		}
}
#endif