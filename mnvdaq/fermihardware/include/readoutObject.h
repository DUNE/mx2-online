#ifndef readoutObject_h
#define readoutObject_h

#include "croc.h"

class readoutObject {
	private:
		croc* theCroc;
		channels* theChannel;
		feb* theFeb;
		int hitNumber;
	public:
		readoutObject() { };
		readoutObject(croc* Croc, channels* Channel, feb* Feb, int Hit) { 
			theCroc    = Croc;
			theChannel = Channel;
			theFeb     = Feb;
			hitNumber  = Hit;
		};
		~readoutObject() { };

		croc inline *getTheCroc() {return theCroc;};
		channels inline *getTheChannel() {return theChannel;};
		feb inline *getTheFeb() {return theFeb;};
		int inline getHitNumber() {return hitNumber;};

};
#endif
