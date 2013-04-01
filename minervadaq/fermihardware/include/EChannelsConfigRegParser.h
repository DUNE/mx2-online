#ifndef EChannelsConfigRegParser_h
#define EChannelsConfigRegParser_h
/*! \file EChannelsConfigRegParser.h
*/

#include <string>

/*! 
  \class EChannelsConfigRegParser
  \brief Manage the bit-packing needed for the EChannels Configuration Register.
  \author Gabriel Perdue
  */

class EChannelsConfigRegParser {

  private:
    unsigned short int registerValue;

    static const short int sequencerMask;
    static const short int sequencerBits;
    static const short int memoryTypeMask;
    static const short int memoryTypeBits;
    static const short int hitModeMask;
    static const short int hitModeBits;
    static const short int numberOfHitsMask;
    static const short int numberOfHitsBits;
    static const short int channelFirmwareMask;
    static const short int channelFirmwareBits;
    static const short int enableTestPulseMask;
    static const short int enableTestPulseBits;
    static const short int enableChannelResetMask;
    static const short int enableChannelResetBits;
    static const short int nfebsMask;
    static const short int nfebsBits;

  public:
    explicit EChannelsConfigRegParser( unsigned short int theRegisterValue=0 );
    ~EChannelsConfigRegParser();

    void EnableSequencerReadout();
    void DisableSequencerReadout();
    void SetMemoryTypeFIFO();
    void SetMemoryTypeRAM();
    void SetFourBitHitEncoding();
    void SetFiveBitHitEncoding();
    void SetSinglePipelineReadout();
    void SetFullPipelineReadout();
    void EnableChannelTestPulse();
    void DisableChannelTestPulse();
    void EnableChannelReset();
    void DisableChannelReset();
    void SetNFEBs( unsigned short int nfebs );

    bool SequencerReadoutEnabled() const;
    bool SendMemoryFIFO() const;
    bool SendMemoryRAM() const;
    bool FourBitHitEncoding() const;
    bool FiveBitHitEncoding() const;
    bool SinglePipelineReadout() const;
    bool FullPipelineReadout() const;
    bool ChannelTestPulseEnabled() const;
    bool ChannelResetEnabled() const;
    unsigned short int NFEBs() const;
    unsigned short int ChannelFirmware() const;
    unsigned short int RawValue() const;

    std::string Description() const;
};

#endif

