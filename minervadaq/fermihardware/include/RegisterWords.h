#ifndef RegisterWords_h
#define RegisterWords_h
/*! \file RegisterWords.h
*/

/*!
  \brief Pre-processed constants used for specific messages to the VME modules.
  \author Gabriel Perdue

	Essentially, these messages are shorts transformed into byte arrays for 
	convenience in function calls. 
  */
namespace RegisterWords {

	// Process the short messages into byte-swapped words for direct use by the 
	// messaging function. Be careful of what is using a swapped data width and 
	// what isn't. (It is better to be consistent than "right.")
  /* Prototype: unsigned char word[] = { (wordShort & 0xFF), ((wordShort>>8) & 0xFF) };  */

  unsigned char channelReset[]       = {0x00,0x80};  /*!< Clear Status; Send to a ECROC EChannels Command Register */
  unsigned char sendMessage[]        = {0x00,0x40};  /*!< Send Message; Send to a ECROC EChannels Command Register */
  unsigned char resetSendMemory[]    = {0x00,0x20};  /*!< Send to a ECROC EChannels Command Register */
  unsigned char resetReceiveMemory[] = {0x00,0x10};  /*!< Send to a ECROC EChannels Command Register */
  unsigned char clearEventCounter[]  = {0x00,0x08};  /*!< Send to a ECROC EChannels Command Register */
  unsigned char sendSyncPatterns[]   = {0x01,0x00};  /*!< Send to a ECROC EChannels Command Register */

};

#endif
