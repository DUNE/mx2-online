#ifndef adctdc_cpp
#define adctdc_cpp

#include "adctdc.h"

#define SHOWSEQ 1 /*!< \define show unpacked block ram (adc) in internal sequential order...*/
#define SHOWPIX 1 /*!< \define show unpacked block ram (adc) keyed by pixel...*/
#define SHOWNHITS 1 /*!< \define show number of hits when doing discr. parse*/
#define SHOWBRAM 1 /*!< \define show raw (parsed) discr frame data; Also show SYSTICKS*/
#define SHOWDELAYTICKS 1 /*!< \define show delay tick information*/
#define SHOWQUARTERTICKS 1 /*!< define show quarter tick information*/

/*********************************************************************************
* Class for creating RAM request frame objects for use with the 
* MINERvA data acquisition system and associated software projects.
*
* Elaine Schulte, Rutgers University
* Gabriel Perdue, The University of Rochester
*
**********************************************************************************/

adc::adc(febAddresses a, RAMFunctionsHit b) 
{
/*! \fn
 * \param a The address (number) of the feb
 * \param b The "RAM Function" which describes the hit of number to be read off
 */
	febNumber[0] = (unsigned char) a; //feb number (address)
	Devices dev = RAM; //device to be addressed
	Broadcasts broad = None; //we don't broadcast
	Directions dir = MasterToSlave; //ALL outgoing messages are master-to-slave
	MakeDeviceFrameTransmit(dev, broad, dir,(unsigned int)b, (unsigned int) febNumber[0]); //make the frame
	outgoingMessage = new unsigned char [MinHeaderLength+2]; // always the same message!
	MakeMessage(); //make up the message
	OutgoingMessageLength = MinHeaderLength+2; //set the outgoing message length
#if DEBUG_FEB
	std::cout << "Made ADC " << b << " for FEB " << a << std::endl;
#endif
}


void adc::MakeMessage() 
{
/*! \fn
 * MakeMessage is the local implimentation of a virtual function of the same
 * name inherited from Frames.  This function bit-packs the data into an OUTGOING
 * message from values set using the get/set functions assigned to this class (see feb.h).
 */
	for (int i=0;i<MinHeaderLength;i++) {
		outgoingMessage[i]=frameHeader[i];
	}
	for (int i=MinHeaderLength;i<(MinHeaderLength+2);i++) {
		outgoingMessage[i]=0;
	}
#if DEBUG_FEB
	std::cout << "Made ADC Message" << std::endl;
#endif
}


int adc::DecodeRegisterValues(int a)
{	
/*! \fn
 *
 * Based on C. Gingu's ParseInpFrameAsAnaBRAM function (from the FermiDAQ) and D. Casper's DecodeRawEvent
 * Decode the input frame data as Hit data type from all Analog BRAMs argument is dummy for now...
 * Returns 0 for success or an error code (eventually)...
 *
 * \param a will set the FEB firmware.
 */
	// Check to see if the frame is right length...
	unsigned short ml = (message[ResponseLength1] << 8) | message[ResponseLength0];
	if ( ml == 0 ) {
		std::cout << "Can't parse an empty InpFrame!" << std::endl;
			// -> Throw exception here.
		return 1;
	}
	if ( ml != ADCFrameLength ) { 
		std::cout << "ADC Frame length mismatch!" << std::endl;
		// -> Throw exception here.
		return 1;		
	}
	// Check that the dummy byte is zero...
	if ( message[Data] != 0 ) {
		std::cout << "Dummy byte is non-zero!" << std::endl;
		// -> Throw exception here.
		return 1;				
	}

	// Eventually put all of this into a try-catch block...

	// Show header in 16-bit word format...
	int hword = 0;
	for (int i=0; i<12; i+=2) {
		unsigned short int val = (message[i+1] << 8) | message[i];
		printf("Header Word %d = %d (%04X)\n",hword,val,val);
		hword++;
	}

	// The number of bytes per row is going to be a function of firmware!!
	const int bytes_per_row = 4;
	// First, show the adc in simple sequential order...
	// Note that the "TimeVal" will disappear in newer firmware!
#if SHOWSEQ
	int AmplVal     = 0;
	int TimeVal     = 0;
	int ChIndx      = 0;
	int TripIndx    = 0;
	int NTimeAmplCh = nChannelsPerTrip; 
	int nrows       = 215; //really 216, but starting just past row 1...
	int max_show    = 15 + bytes_per_row * nrows; 
	for (int i = 15; i <= max_show; i += 4) {
		AmplVal = ((message[i - 2] << 8) + message[i - 3]);
		TimeVal = ((message[i] << 8) + message[i - 1]); //timeval not useful for MINERvA (D0 thing)
		// Show.  Recall that no *hit index* is shown because each analog bank *is* a "hit" index.
		printf("ChIndx = %d, TripIndx = %d\n", ChIndx,TripIndx);
		// Apply "data mask" (pick out 12 bit adc) and shift two bits to the right (lower).
		printf("  Masked AmplVal = %d\n", (AmplVal & 0x3FFC)>>2); // 0x3FFC = 0011 1111 1111 1100, 12-bit adc 
		ChIndx++;
		if (ChIndx == NTimeAmplCh) { TripIndx++; ChIndx = 0; }
	} //end for - show frame sequential
#endif

	// Show the adc keyed by pixel value...
#if SHOWPIX 
	int lowMap[] = {26,34,25,33,24,32,23,31,22,30,21,29,20,28,19,27,
		11,3,12,4,13,5,14,6,15,7,16,8,17,9,18,10,
		11,3,12,4,13,5,14,6,15,7,16,8,17,9,18,10,
		26,34,25,33,24,32,23,31,22,30,21,29,20,28,19,27};

	for (int pixel = 0; pixel < nPixelsPerFEB; pixel++) {
		// locate the pixel
		int headerLength = 12; // number of bytes
		int side = pixel / (nPixelsPerSide);
		int hiMedEvenOdd = (pixel / (nPixelsPerSide / 2)) % 2;
		int hiMedTrip = 2 * side + hiMedEvenOdd;  // 0...3
		int loTrip = nHiMedTripsPerFEB + side;    // 4...5
		int hiChannel = nSkipChannelsPerTrip + (pixel % nPixelsPerTrip);
		int medChannel = hiChannel + nPixelsPerTrip;
		int loChannel = lowMap[pixel];
		printf("Pixel = %d, HiMedTrip = %d, hiChannel = %d, medChannel = %d, loTrip = %d, lowChannel = %d\n",
			pixel, hiMedTrip, hiChannel, medChannel, loTrip, loChannel);
		// Calculate the offsets (in bytes_per_row increments).
		// The header offset is an additional 12 bytes... 
		int hiOffset = hiMedTrip * nChannelsPerTrip + hiChannel;
		int medOffset = hiMedTrip * nChannelsPerTrip + medChannel;
		int loOffset = loTrip * nChannelsPerTrip + loChannel;
		printf("hiOffset = %d, medOffset = %d, loOffset = %d\n", hiOffset, medOffset, loOffset);
		unsigned short int dataMask = 0x3FFC;
		printf("Qhi = %d, Qmed = %d, Qlo = %d\n", 
			( ( ( (message[headerLength + bytes_per_row*hiOffset + 1] << 8) | message[headerLength + bytes_per_row*hiOffset] ) 
			& dataMask ) >> 2),
			( ( ( (message[headerLength + bytes_per_row*medOffset + 1] << 8) | message[headerLength + bytes_per_row*medOffset] ) 
			& dataMask ) >> 2),
			( ( ( (message[headerLength + bytes_per_row*loOffset + 1] << 8) | message[headerLength + bytes_per_row*loOffset] ) 
			& dataMask ) >> 2)
			);
	}                
#endif
	return 0;
}


disc::disc(febAddresses a) 
{
/*! \fn
 * \param a: The address (number) of the feb
 * \param b: The "RAM Function" which describes the hit of number to be read off
 * Discriminators *always* read the same function.
 */
	febNumber[0] = (unsigned char) a; //feb number (address)
	Devices dev = RAM; //device to be addressed
	Broadcasts broad = None; //we don't broadcast
	Directions dir = MasterToSlave; //ALL outgoing messages are master-to-slave
	unsigned int b = (unsigned int)ReadHitDiscr;
	MakeDeviceFrameTransmit(dev, broad, dir,(unsigned int)b, (unsigned int) febNumber[0]); //make the frame
	outgoingMessage = new unsigned char [MinHeaderLength];
	MakeMessage(); //make up the message
	OutgoingMessageLength = MinHeaderLength; //set the outgoing message length
#if DEBUG_FEB
	std::cout << "Made DISC for FEB " << a << std::endl;
#endif
}


void disc::MakeMessage() 
{
/*! \fn
 * Makes the outgoing message 
 */
	for (int i=0;i<MinHeaderLength;i++) {
		outgoingMessage[i]=frameHeader[i];
	}
}


int disc::DecodeRegisterValues(int a) 
{
/*! \fn 
 *  Decode a discriminator frame.  Argument is dummy for now...
 *  Returns 0 for success or an error code (eventually)...
 */
	// Check to see if the frame is more than zero length...
	unsigned short ml = (message[ResponseLength1] << 8) | message[ResponseLength0];
	if ( ml == 0 ) {
		std::cout << "Can't parse an empty InpFrame!" << std::endl;
		// -> Throw exception here.
		return 1;
	}
	// Check that the dummy byte is zero...
	if ( message[Data] != 0 ) {
		std::cout << "Dummy byte is non-zero!" << std::endl;
		// -> Throw exception here.
		return 1;				
	}

	int *TripXNHits = new int [4];
	//Retrieve the number of hits for each Trip chip.
	TripXNHits[0] = 0x0F & message[12];
	TripXNHits[1] = (0xF0 & message[12]) >> 4;
	TripXNHits[2] = 0x0F & message[13];
	TripXNHits[3] = (0xF0 & message[13]) >> 4;
#if SHOWNHITS
	printf("Trip Nhits: %d,%d,%d,%d\n", TripXNHits[0], TripXNHits[1], TripXNHits[2], TripXNHits[3]);
#endif

	//Retrieve the acual disciminators' timing info.
	int indx = 14;      //Start index for Discrim BRAMs information
	unsigned int SRLDepth = 16;  //SRL length - see VHDL code...
	unsigned short int *TempHitArray = new unsigned short int [20]; //16(SRL) + 2(QuaterTicks) +2(TimeStamp) = 20 words of 2 bytes
	unsigned int TempDiscQuaterTicks = 0;                

	for (int iTrip = 0; iTrip < 4; iTrip++) {
		//Caution: Since TripXNHits[iTrip]=1 means one hit and TripXNHits[iTrip]=0 means no hits
		//the following 'for' loop must start with iHit=1. However, when assingning data into 
		//objects we must substract one for hit index (the array index starts from one).
		for (int iHit = 1; iHit <= TripXNHits[iTrip]; iHit++) {
			//assign InpFrame[] bytes into TempHitArray[] words (16 bits)
			for (int i = 0; i < 20; i++) {
				TempHitArray[i] = (unsigned short int)(message[indx] + (message[indx + 1] << 8));
				indx += 2;
#if SHOWBRAM
				printf("response[%d] = %d, response[%d] << 8 = %d\n", indx, message[indx], 
					indx + 1, message[indx + 1] << 8);
				printf("  BRAMWord[%d] = %u\n", i, TempHitArray[i]);
#endif                            
			} // end loop over temp hit array
			//update the DiscTSTicks (Time Stamp Ticks is a 32 bit long number)
			//Here we shift the last 16 bit word 16 bits to the left to make it the most significant word.
			unsigned int TempDiscTicks = ((TempHitArray[19] << 16) + TempHitArray[18]);
#if SHOWBRAM
			printf("BRAMWord[19] << 16 = %u, BRAMWord[18] = %u\n", (TempHitArray[19] << 16), TempHitArray[18]);
			printf("  Time Stamp Ticks: = %u\n", TempDiscTicks);
#endif
			//update the DiscQuaterTicks (Discriminator's Quater Tick is a two bit number = 0, 1, 2 or 3)
#if SHOWQUARTERTICKS
			printf("Update Disc Quarter Ticks:\n");
			printf(" TempHitArray[17] = %d, TempHitArray[16] = %d\n", TempHitArray[17], TempHitArray[16]);
#endif
			//Here we pull a single bit from a sixteen bit word, mapping channel to bit number.
			//The "second" word (TempHitArray[17] encodes the true second bit, and hence adds 0 or 2.
			//e.g. 16 (bits): 0101 1110 1111 0100
			//     17 (bits): 1000 0000 1000 1100
			//                -------------------
			//encodes (int) : 2101 1110 3111 2300 => Quarter ticks range from 0->3.
			for (int iCh = 0; iCh < NDiscrChPerTrip; iCh++) {
				TempDiscQuaterTicks = 2 * GetBitFromWord(TempHitArray[17], iCh) +
					GetBitFromWord(TempHitArray[16], iCh);
#if SHOWQUARTERTICKS
				printf("  iCh = %d, iHit-1 = %d, DQ Ticks = %d\n", iCh, iHit - 1, TempDiscQuaterTicks);
#endif
			}
			/*! \note {update the DiscDelTicks (Discriminator's Delay Tick is an integer between 0 and 
			*   SRLDepth(16) inclusive.
			*   it counts the number of zeros (if any) before the SRL starts to be filled with ones - see VHDL code... 
			*   We pick a bit from each 16-bit row as a function of channel and sum them.  The true delay tick value is 
			*   16 minus this sum.  So, for example:
			*   row(TempHitArray)    ch0 ch1 ch2 ch3 ch4 ... ch15
			*     0               0   0   0   0   0   ... 
			*     1               1   0   0   0   0   ... 
			*     2               1   1   0   0   0   ... 
			*     3               1   1   1   0   0   ... 
			*     4               1   1   1   0   0   ... 
			*     5               1   1   1   0   0   ... 
			*     ...     
			*    15               1   1   1   0   0   ...
			*    ----------------------------------------
			*     Sum            15  14  13   0   0   ...
			*     Delay Ticks     1   2   3   0   0   ... }
			*/
			//Note: once a delay tick is formed, all subsequent entries for the channel must also be one, so there 
			//are several valid algorithms that could pick this information out.  Also note: this example should not 
			//be interpreted to imply the delay tick number should or will always climb with channel number.
#if SHOWDELAYTICKS
			printf("Update Disc Delay Ticks:\n");
#endif
			unsigned int TempDiscDelTicks = 0;
			for (int iCh = 0; iCh < NDiscrChPerTrip; iCh++) {
				TempDiscDelTicks = 0;
				for (unsigned int iSRL = 0; iSRL < SRLDepth; iSRL++)
					TempDiscDelTicks = TempDiscDelTicks + GetBitFromWord(TempHitArray[iSRL], iCh);
#if SHOWDELAYTICKS
					printf("  iCh = %d, iHit-1 = %d, Del Ticks = %d\n", iCh, iHit - 1, SRLDepth - TempDiscDelTicks);
#endif
			}
		} // end loop over hits per trip
	} // end loop over trips

	delete [] TripXNHits;
	delete [] TempHitArray;
	return 0;
}


int disc::GetDiscrFired(int a)
{
/*! \fn 
 * The title of this function is a bit misleading - it is calculating the number of hits on a FEB, 
 * not checking whether the discriminator on channel "a" fired or not.  The argument is a dummy.
 * \param a an integer placeholder from inheritance
 */
	// Check to see if the frame is more than zero length...
	unsigned short ml = (message[ResponseLength1] << 8) | message[ResponseLength0];
	if ( ml == 0 ) {
		std::cout << "Can't parse an empty InpFrame!" << std::endl;
		// -> Throw exception here.
		return -1;
	}
	// Check that the dummy byte is zero...
	if ( message[Data] != 0 ) {
		std::cout << "Dummy byte is non-zero!" << std::endl;
		// -> Throw exception here.
		return -1;				
	}
	if ( ( (0x0F & message[12]) != ((0xF0 & message[12]) >> 4)) ||
		( (0x0F & message[13]) != ((0xF0 & message[13]) >> 4)) ) 
	{
		std::cout << "Mismatch in pushed trip discriminator counts in disc::GetDiscrFired!" << std::endl;
		// -> Throw exception here.
		return -1;
	}
	return ((0x0F & message[12]) > (0x0F & message[13])) ? (0x0F & message[12]) : (0x0F & message[13]);
}


//LSBit has bit_index=0
int disc::GetBitFromWord(unsigned short int word, int index) 
{
	int ip = (int)pow(2,index);
	return (int)( (ip & word) / ip );
}


//LSBit has bit_index=0
int disc::GetBitFromWord(unsigned int word, int index) 
{
	int ip = (int)pow(2,index);
	return (int)( (ip & word) / ip );
}


//LSBit has bit_index=0
int disc::GetBitFromWord(long_m word, int index) 
{
	long_m ip = (long_m)pow(2,index);
	return (int)( (ip & word) / ip );
}

#endif

