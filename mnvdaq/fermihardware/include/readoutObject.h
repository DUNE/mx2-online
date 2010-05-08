#ifndef readoutObject_h
#define readoutObject_h

#include "croc.h"

class readoutObject {
	private:
		int febID;
		std::list<channels*> channelsList;
		std::list<int*> hitsPerChannelList;
	public:
		readoutObject(int id) { 
			febID = id;
		};
		~readoutObject() { };

		std::list<channels*> inline *getChannelsList() { return &channelsList; };
		std::list<int*> inline *getHitsPerChannelList() { return &hitsPerChannelList; };
		int inline getFebID() { return febID; };
		void inline addChannel(channels* ch) { channelsList.push_back(ch); };
		void inline addHits(int* h) { hitsPerChannelList.push_back(h); };
		void inline clearHits() { hitsPerChannelList.clear(); };
};
#endif
