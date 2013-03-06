#ifndef SequencerReadoutBlock_cpp
#define SequencerReadoutBlock_cpp

#include "log4cppHeaders.h"
#include "FrameTypes.h"
#include "SequencerReadoutBlock.h"
#include "exit_codes.h"

log4cpp::Category& SequencerReadoutBlockLog = log4cpp::Category::getInstance(std::string("SequencerReadoutBlock"));

//-----------------------------------------------------
SequencerReadoutBlock::SequencerReadoutBlock() :
  data(NULL),
  dataLength(0)
{
  SequencerReadoutBlockLog.setPriority(log4cpp::Priority::INFO);  
  SequencerReadoutBlockLog.debugStream() << "Created new SequencerReadoutBlock";
}

//-----------------------------------------------------
SequencerReadoutBlock::~SequencerReadoutBlock()
{
  for (std::list<LVDSFrame*>::iterator p=frames.begin(); p!=frames.end(); ++p) {
    delete *p;
  }
  frames.clear();
  this->ClearData();
  SequencerReadoutBlockLog.debugStream() << "Destroyed SequencerReadoutBlock";
}

//-----------------------------------------------------
void SequencerReadoutBlock::SetData(unsigned char * data, unsigned short dataLength)
{
  this->data = data;
  this->dataLength = dataLength;
}

//-----------------------------------------------------
void SequencerReadoutBlock::ClearData()
{
  if ( (dataLength > 0) && (NULL != data) ) {
    delete [] data;
    data = NULL;
    dataLength = 0;
  }
}

//-----------------------------------------------------
unsigned char * SequencerReadoutBlock::GetData() const
{
  return data;
}

//-----------------------------------------------------
unsigned short SequencerReadoutBlock::GetDataLength() const
{
  return dataLength;
}

//-----------------------------------------------------
void SequencerReadoutBlock::ProcessDataIntoFrames()
{
  if (0 == dataLength) return;
  if (data) {
    unsigned short index = 0;
    unsigned short length = 0;

    while (index < dataLength) {
      length = (data[FrameTypes::ResponseLength0 + index]<<8) | 
        data[FrameTypes::ResponseLength1 + index];
      SequencerReadoutBlockLog.debugStream() << "Frame Length = " << length;

      unsigned char * frameData = new unsigned char[length];
      memmove(frameData, data+index, length); 

      LVDSFrame * frame = new LVDSFrame();
      frame->SetReceivedMessage( frameData );
      frame->DecodeHeader();
      frame->CheckForErrors();

      frames.push_back( frame );
      index += length;
    }
    this->ClearData();
  }
}

//-----------------------------------------------------
LVDSFrame * SequencerReadoutBlock::PopOffFrame()
{
  LVDSFrame * frame = NULL;
  if ( !frames.empty() ) {
    frame = frames.front();
    frames.pop_front();
  }
  return frame;
}


#endif
