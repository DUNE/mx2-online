#ifndef EChannelsConfigRegParser_cpp
#define EChannelsConfigRegParser_cpp
/*! \file EChannelsConfigRegParser.cpp
*/

#include <sstream>
#include <iomanip>

#include "EChannelsConfigRegParser.h"
#include "log4cppHeaders.h"

log4cpp::Category& EChConfLog = log4cpp::Category::getInstance(std::string("EChConf"));

const short int EChannelsConfigRegParser::sequencerMask          = 0x8000;
const short int EChannelsConfigRegParser::sequencerBits          = 15;
const short int EChannelsConfigRegParser::memoryTypeMask         = 0x4000;
const short int EChannelsConfigRegParser::memoryTypeBits         = 14;
const short int EChannelsConfigRegParser::hitModeMask            = 0x2000;
const short int EChannelsConfigRegParser::hitModeBits            = 13;
const short int EChannelsConfigRegParser::numberOfHitsMask       = 0x1000;
const short int EChannelsConfigRegParser::numberOfHitsBits       = 12;
const short int EChannelsConfigRegParser::clockMonPhaseSelMask   = 0x0800;
const short int EChannelsConfigRegParser::clockMonPhaseSelBits   = 11;
const short int EChannelsConfigRegParser::channelFirmwareMask    = 0x03C0;
const short int EChannelsConfigRegParser::channelFirmwareBits    = 6;
const short int EChannelsConfigRegParser::enableTestPulseMask    = 0x0020;
const short int EChannelsConfigRegParser::enableTestPulseBits    = 5;
const short int EChannelsConfigRegParser::enableChannelResetMask = 0x0010;
const short int EChannelsConfigRegParser::enableChannelResetBits = 4;
const short int EChannelsConfigRegParser::nfebsMask              = 0x000F;
const short int EChannelsConfigRegParser::nfebsBits              = 0;

//----------------------------------------
EChannelsConfigRegParser::EChannelsConfigRegParser( unsigned short int theRegisterValue ) :
  registerValue(theRegisterValue)
{
  EChConfLog.setPriority(log4cpp::Priority::DEBUG);  
}

//----------------------------------------
EChannelsConfigRegParser::~EChannelsConfigRegParser() 
{
}

//----------------------------------------
void EChannelsConfigRegParser::EnableSequencerReadout()
{
  EChConfLog.infoStream() << "Enable sequencer readout.";
  registerValue |= (1<<sequencerBits);
}

//----------------------------------------
void EChannelsConfigRegParser::DisableSequencerReadout()
{
  registerValue &= ~sequencerMask;
}

//----------------------------------------
void EChannelsConfigRegParser::SetMemoryTypeFIFO()
{
  registerValue &= ~memoryTypeMask;
}

//----------------------------------------
void EChannelsConfigRegParser::SetMemoryTypeRAM()
{
  registerValue |= (1<<memoryTypeBits);
}

//----------------------------------------
void EChannelsConfigRegParser::SetFourBitHitEncoding()
{
  registerValue &= ~numberOfHitsMask;
}

//----------------------------------------
void EChannelsConfigRegParser::SetFiveBitHitEncoding()
{
  registerValue |= (1<<numberOfHitsBits);
}

//----------------------------------------
void EChannelsConfigRegParser::SetClockMonPhaseSelLeading()
{
  registerValue &= ~clockMonPhaseSelMask;
}

//----------------------------------------
void EChannelsConfigRegParser::SetClockMonPhaseSelFalling()
{
  registerValue |= (1<<clockMonPhaseSelBits); 
}

//----------------------------------------
void EChannelsConfigRegParser::SetSinglePipelineReadout()
{
  registerValue |= (1<<hitModeBits);
}

//----------------------------------------
void EChannelsConfigRegParser::SetFullPipelineReadout()
{
  registerValue &= ~hitModeMask;
}

//----------------------------------------
void EChannelsConfigRegParser::EnableChannelTestPulse()
{
  registerValue |= (1<<enableTestPulseBits);
}

//----------------------------------------
void EChannelsConfigRegParser::DisableChannelTestPulse()
{
  registerValue &= ~enableTestPulseMask;
}

//----------------------------------------
void EChannelsConfigRegParser::EnableChannelReset()
{
  registerValue |= (1<<enableChannelResetBits);
}

//----------------------------------------
void EChannelsConfigRegParser::DisableChannelReset()
{
  registerValue &= ~enableChannelResetMask;
}

//----------------------------------------
void EChannelsConfigRegParser::SetNFEBs( unsigned short int nfebs )
{
  // shift is zero here, so drop it from calcs
  nfebs &= nfebsMask;
  registerValue &= ~nfebsMask;
  registerValue |= nfebs;
}


//----------------------------------------
bool EChannelsConfigRegParser::SequencerReadoutEnabled() const
{
  return (registerValue & sequencerMask);
}

//----------------------------------------
bool EChannelsConfigRegParser::SendMemoryFIFO() const
{
  return !SendMemoryRAM();
}

//----------------------------------------
bool EChannelsConfigRegParser::SendMemoryRAM() const
{
  return (registerValue & memoryTypeMask);
}

//----------------------------------------
bool EChannelsConfigRegParser::FourBitHitEncoding() const
{
  return !FiveBitHitEncoding();
}

//----------------------------------------
bool EChannelsConfigRegParser::FiveBitHitEncoding() const
{
  return (registerValue & numberOfHitsMask);
}

//----------------------------------------
bool EChannelsConfigRegParser::SinglePipelineReadout() const
{
  return (registerValue & hitModeMask);
}

//----------------------------------------
bool EChannelsConfigRegParser::FullPipelineReadout() const
{
  return !SinglePipelineReadout();
}

//----------------------------------------
bool EChannelsConfigRegParser::ChannelTestPulseEnabled() const
{
  return (registerValue & enableTestPulseMask);
}

//----------------------------------------
bool EChannelsConfigRegParser::ChannelResetEnabled() const
{
  return (registerValue & enableChannelResetMask);
}

//----------------------------------------
bool EChannelsConfigRegParser::ClockMonPhaseBitIsLeading() const
{
  return !ClockMonPhaseBitIsFalling();
}

//----------------------------------------
bool EChannelsConfigRegParser::ClockMonPhaseBitIsFalling() const
{
  return (registerValue & clockMonPhaseSelMask);
}

//----------------------------------------
unsigned short int EChannelsConfigRegParser::NFEBs() const
{
  // shift is zero, so drop it
  return (registerValue & nfebsMask);
}

//----------------------------------------
unsigned short int EChannelsConfigRegParser::ChannelFirmware() const
{
  return ( (registerValue & channelFirmwareMask)>>channelFirmwareBits );
}

//----------------------------------------
unsigned short int EChannelsConfigRegParser::RawValue() const
{
  return registerValue;
}

//-----------------------------
std::string EChannelsConfigRegParser::Description() const 
{
  std::stringstream ss;
  ss << "Configuration Value = 0x" << std::setfill('0') << std::setw( 4 ) 
    << std::hex << registerValue << std::dec
    << "\n\t" << "; Sequencer Readout = " << SequencerReadoutEnabled() 
    << "\n\t" << "; Send Memory FIFO = " << SendMemoryFIFO() 
    << "\n\t" << "; Send Memory RAM = " << SendMemoryRAM() 
    << "\n\t" << "; Four Bit Hit Encoding = " << FourBitHitEncoding() 
    << "\n\t" << "; Five Bit Hit Encoding = " << FiveBitHitEncoding() 
    << "\n\t" << "; Clock Mon Phase Sel Falling = " << ClockMonPhaseBitIsFalling() 
    << "\n\t" << "; Clock Mon Phase Sel Leading = " << ClockMonPhaseBitIsLeading() 
    << "\n\t" << "; Single Pipeline Readout = " << SinglePipelineReadout() 
    << "\n\t" << "; Full Pipeline Readout = " << FullPipelineReadout() 
    << "\n\t" << "; Test Pulse Enabled = " << ChannelTestPulseEnabled() 
    << "\n\t" << "; Reset Enabled = " << ChannelResetEnabled() 
    << "\n\t" << "; N FEB = " << NFEBs() 
    << "\n\t" << "; Channel Firmware = " << ChannelFirmware(); 
  return ss.str();
}


#endif

