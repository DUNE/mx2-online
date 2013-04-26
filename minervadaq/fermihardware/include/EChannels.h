#ifndef EChannels_h
#define EChannels_h
/*! \file EChannels.h
*/

#include <list>
#include <fstream>
#include <string>
#include <sstream>
#include <tr1/memory>  // for shared_ptrs

#include "CAENVMEtypes.h"

#include "FrameTypes.h"
#include "VMECommunicator.h"
#include "VMEModuleTypes.h"

class LVDSFrame;
class FPGAFrame;
class TRIPFrame;
class FrontEndBoard;
class EChannelsConfigRegParser;

/*! 
  \class EChannels
  \brief This class holds data associated with a CROC-E channel.
  \author Gabriel Perdue

  This class holds the data which belongs to a CROC-E channel, including the list
  of FEB's which are on the channel.  
*/

class EChannels : public VMECommunicator {
  private:
    unsigned int channelNumber;             /*!< the channel identifying index, used for retrieval, currently indexed 0-3 */  
    unsigned int channelDirectAddress;	    /*!< base + offset - this is the true VME address */

    unsigned int receiveMemoryAddress;
    unsigned int sendMemoryAddress;
    unsigned int framePointersMemoryAddress;
    unsigned int configurationAddress;
    unsigned int commandAddress;
    unsigned int eventCounterAddress;
    unsigned int framesCounterAndLoopDelayAddress;
    unsigned int frameStatusAddress;
    unsigned int txRxStatusAddress;
    unsigned int receiveMemoryPointerAddress;
    unsigned int headerDataAddress;

    std::vector<FrontEndBoard*> FrontEndBoardsVector;     

    unsigned char isAvailable( FrontEndBoard* feb ) const;
    void SetChannelConfiguration( unsigned char* message ) const;

    static const short int eventCounterMask;  
    static const short int eventCounterBits;  
    static const short int receiveMemoryMask; 
    static const short int receiveMemoryBits; 

  public:
    explicit EChannels( unsigned int vmeAddress, unsigned int channelNumber, 
        const Controller* controller );
    ~EChannels();

    virtual void throwIfError( int error, const std::string& msg ) const;

    void ResetSendMemoryPointer() const;  
    void ResetReceiveMemoryPointer() const;  
    void ClearAndResetStatusRegister() const;  
    unsigned short ReadFrameStatusRegister() const;
    unsigned short ReadTxRxStatusRegister() const;

    std::tr1::shared_ptr<EChannelsConfigRegParser> GetChannelConfiguration() const;
    void SetChannelConfiguration( std::tr1::shared_ptr<EChannelsConfigRegParser> config ) const;

    void WriteMessageToMemory( unsigned char* message, int messageLength ) const;
    void SendMessage() const;

    void ResetEventCounter() const;
    unsigned short ReadEventCounter() const;
    unsigned short WaitForSequencerReadoutCompletion() const;
    unsigned short WaitForMessageReceived() const;
    unsigned int ReadDPMPointer() const;
    unsigned char* ReadMemory( unsigned int dataLength ) const; 

    // write the frames - load them to memory (don't send messages)
    // no WriteFrame is deliberate - too many configs - we just offer preconfigured reads
    void WriteFrameRegistersToMemory( std::tr1::shared_ptr<LVDSFrame> frame ) const;
    void WriteFPGAProgrammingRegistersDumpReadToMemory( std::tr1::shared_ptr<FPGAFrame> frame ) const; 
    void WriteTRIPRegistersReadFrameToMemory( std::tr1::shared_ptr<TRIPFrame> frame ) const; 
    // read the frames - load messages to memory, send them, and then check the dpm pointer
    unsigned short ReadFPGAProgrammingRegistersToMemory( std::tr1::shared_ptr<FPGAFrame> frame ) const;

    unsigned int GetChannelNumber() const;
    unsigned int GetParentECROCAddress() const;
    unsigned int GetParentCROCNumber() const;
    unsigned int GetDirectAddress() const;
    virtual unsigned int GetAddress() const;

    std::pair<int,std::string> DecodeStatusMessage( const unsigned short& status ) const;

    void EnableSequencerReadout() const;
    void DisableSequencerReadout() const;
    void UseFourBitHitEncoding() const;
    void UseFiveBitHitEncoding() const;
    void UseSinglePipelineReadout() const;
    void UseFullPipelineReadout() const;

    void ConfigureForStandardDataTaking() const;
    void SetupHeaderData( int crateNumber, int crocID, int febFirmware ) const;
    unsigned short GetHeaderData() const;

    void SetupNFrontEndBoards( int nFEBs );
    unsigned int GetNumFrontEndBoards() const;
    std::vector<FrontEndBoard*>* GetFrontEndBoardVector();
    FrontEndBoard* GetFrontEndBoardVector( int index /* should always equal (FEB address - 1) */ );
};
#endif
