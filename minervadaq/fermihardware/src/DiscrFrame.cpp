#ifndef DiscrFrame_cpp
#define DiscrFrame_cpp

#include <iomanip>
#include "DiscrFrame.h"
#include "exit_codes.h"

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

log4cpp::Category& DiscrFrameLog = log4cpp::Category::getInstance(std::string("DiscrFrame"));

DiscrFrame::DiscrFrame(febAddresses a) : LVDSFrame()
{
  /*! \fn
   * \param a: The address (number) of the feb
   * \param b: The "RAM Function" which describes the hit of number to be read off
   * Discriminators *always* read the same function.
   */
  febNumber[0] = (unsigned char) a; //feb number (address)
  
  Devices dev      = RAM; //device to be addressed
  Broadcasts broad = None; //we don't broadcast
  Directions dir   = MasterToSlave; //ALL outgoing messages are master-to-slave
  unsigned int b   = (unsigned int)ReadHitDiscr;
  MakeDeviceFrameTransmit(dev, broad, dir, (unsigned int)b, (unsigned int)febNumber[0]); 

  outgoingMessage = new unsigned char [FrameHeaderLengthOutgoing];
  OutgoingMessageLength = FrameHeaderLengthOutgoing;
  MakeMessage(); 

  DiscrFrameLog.setPriority(log4cpp::Priority::DEBUG);  // ERROR?
  DiscrFrameLog.debugStream() << "Made DiscrFrame for FEB " << a; 
}


void DiscrFrame::MakeMessage() 
{
  /*! \fn
   * Makes the outgoing message 
   */
  for (unsigned int i = 0; i < OutgoingMessageLength; ++i) {
    outgoingMessage[i]=frameHeader[i];
  }
}


int DiscrFrame::DecodeRegisterValues(int a) 
{
  /*! \fn 
   *  Decode a discriminator frame.  Argument is dummy for now...
   *  Returns 0 for success or an error code (eventually)...
   */
  // Check to see if the frame is more than zero length...
  unsigned short ml = (message[ResponseLength1]) | (message[ResponseLength0] << 8);
  if ( ml == 0 ) {
    DiscrFrameLog.fatalStream() << "Can't parse an empty InpFrame!";
    exit(EXIT_FEB_UNSPECIFIED_ERROR);
  }
  // Check that the dummy byte is zero...
  if ( message[Data] != 0 ) {
    DiscrFrameLog.fatalStream() << "Dummy byte is non-zero!";
    exit(EXIT_FEB_UNSPECIFIED_ERROR);
  }

  int *TripXNHits = new int [4];
  for (unsigned int i = 0; i < 4; ++i)
    TripXNHits[i] = GetNHitsOnTRiP(i);
#if SHOWNHITS
  DiscrFrameLog.debug("Trip Nhits: %d,%d,%d,%d\n", TripXNHits[0], TripXNHits[1], TripXNHits[2], TripXNHits[3]);
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
        DiscrFrameLog.debug("response[%d] = %d, response[%d] << 8 = %d\n", indx, message[indx], 
            indx + 1, message[indx + 1] << 8);
        DiscrFrameLog.debug("  BRAMWord[%d] = %u\n", i, TempHitArray[i]);
#endif                            
      } // end loop over temp hit array
      //update the DiscTSTicks (Time Stamp Ticks is a 32 bit long number)
      //Here we shift the last 16 bit word 16 bits to the left to make it the most significant word.
      unsigned int TempDiscTicks = ((TempHitArray[19] << 16) + TempHitArray[18]);
#if SHOWBRAM
      DiscrFrameLog.debug("BRAMWord[19] << 16 = %u, BRAMWord[18] = %u\n", (TempHitArray[19] << 16), TempHitArray[18]);
      DiscrFrameLog.debug("  Time Stamp Ticks: = %u\n", TempDiscTicks);
#endif
      //update the DiscQuaterTicks (Discriminator's Quater Tick is a two bit number = 0, 1, 2 or 3)
#if SHOWQUARTERTICKS
      DiscrFrameLog.debug("Update Disc Quarter Ticks:\n");
      DiscrFrameLog.debug(" TempHitArray[17] = %d, TempHitArray[16] = %d\n", TempHitArray[17], TempHitArray[16]);
#endif
      //Here we pull a single bit from a sixteen bit word, mapping channel to bit number.
      //The "second" word (TempHitArray[17] encodes the true second bit, and hence adds 0 or 2.
      //e.g. 16 (bits): 0101 1110 1111 0100
      //     17 (bits): 1000 0000 1000 1100
      //                -------------------
      //encodes (int) : 2101 1110 3111 2300 => Quarter ticks range from 0->3.
      for (unsigned int iCh = 0; iCh < NDiscrChPerTrip; iCh++) {
        TempDiscQuaterTicks = 2 * GetBitFromWord(TempHitArray[17], iCh) +
          GetBitFromWord(TempHitArray[16], iCh);
#if SHOWQUARTERTICKS
        DiscrFrameLog.debug("  iCh = %d, iHit-1 = %d, DQ Ticks = %d\n", iCh, iHit - 1, TempDiscQuaterTicks);
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
      DiscrFrameLog.debug("Update Disc Delay Ticks:\n");
#endif
      unsigned int TempDiscDelTicks = 0;
      for (unsigned int iCh = 0; iCh < NDiscrChPerTrip; iCh++) {
        TempDiscDelTicks = 0;
        for (unsigned int iSRL = 0; iSRL < SRLDepth; iSRL++)
          TempDiscDelTicks = TempDiscDelTicks + GetBitFromWord(TempHitArray[iSRL], iCh);
#if SHOWDELAYTICKS
        DiscrFrameLog.debug("  iCh = %d, iHit-1 = %d, Del Ticks = %d\n", iCh, iHit - 1, SRLDepth - TempDiscDelTicks);
#endif
      }
    } // end loop over hits per trip
  } // end loop over trips

  delete [] TripXNHits;
  delete [] TempHitArray;
  return 0;
}

//-----------------------------------------------------
unsigned int DiscrFrame::GetNHitsOnTRiP(const unsigned int& tripNumber) const // 0 <= tripNumber <= 3
{
  if (NULL == message) {
    DiscrFrameLog.fatalStream() << "Null message buffer in GetNHitsOnTRiP!";
    exit(EXIT_FEB_UNSPECIFIED_ERROR);
  }
  switch (tripNumber) {
    case 0:
      return (0x0F & message[discrNumHits01]);
      break;
    case 1:
      return (0xF0 & message[discrNumHits01]) >> 4;
      break;
    case 2:
      return (0x0F & message[discrNumHits23]);
      break;
    case 3:
      return (0xF0 & message[discrNumHits23]) >> 4;
      break;
    default:
      DiscrFrameLog.fatalStream() << "Only TRiPs 0-3 are valid for GetNHitsOnTRiP.";
      exit(EXIT_FEB_UNSPECIFIED_ERROR);
  }
  return 0;
}

// TODO - this method is bad and should be removed...
int DiscrFrame::GetDiscrFired(int a)
{
  /*! \fn 
   * The title of this function is a bit misleading - it is calculating the number of hits on a FEB, 
   * not checking whether the discriminator on channel "a" fired or not.  The argument is a dummy.
   * \param a an integer placeholder from inheritance
   */
  // Check to see if the frame is more than zero length...
  unsigned short ml = (message[ResponseLength1]) | (message[ResponseLength0] << 8);
  if ( ml == 0 ) {
    DiscrFrameLog.fatalStream() << "Can't parse an empty InpFrame!";
    exit(EXIT_FEB_UNSPECIFIED_ERROR);
  }
  // Check that the dummy byte is zero...
  if ( message[Data] != 0 ) {
    DiscrFrameLog.fatalStream() << "Dummy byte is non-zero!";
    exit(EXIT_FEB_UNSPECIFIED_ERROR);
  }

  if ( ( (0x0F & message[12]) != ((0xF0 & message[12]) >> 4)) ||
      ( (0x0F & message[13]) != ((0xF0 & message[13]) >> 4)) ) 
  {
    DiscrFrameLog.errorStream() << "Mismatch in pushed trip discriminator counts in DiscrFrame::GetDiscrFired!";
    return -1;
  }
  return ((0x0F & message[12]) > (0x0F & message[13])) ? (0x0F & message[12]) : (0x0F & message[13]);
}


//LSBit has bit_index=0
int DiscrFrame::GetBitFromWord(unsigned short int word, int index) 
{
  int ip = (int)pow(2,index);
  return (int)( (ip & word) / ip );
}


//LSBit has bit_index=0
int DiscrFrame::GetBitFromWord(unsigned int word, int index) 
{
  int ip = (int)pow(2,index);
  return (int)( (ip & word) / ip );
}


//LSBit has bit_index=0
int DiscrFrame::GetBitFromWord(long_m word, int index) 
{
  long_m ip = (long_m)pow(2,index);
  return (int)( (ip & word) / ip );
}

#endif

