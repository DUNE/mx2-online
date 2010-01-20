#include <iostream>

#include "Scripts/GenericScript.h"
#include "Blocks/TriggerSetupBlock.h"
#include "Commands/TriggerInternalCommand.h"
#include "Commands/TriggerRateHighNumberCommand.h"
#include "Commands/TriggerRateLowNumberCommand.h"

using namespace std;
using namespace Minerva;

void other();

int main()
{
	GenericScript * script = new GenericScript;
	TriggerSetupBlock * block = new TriggerSetupBlock;
	
	TriggerInternalCommand       * c1 = new TriggerInternalCommand;
	TriggerRateHighNumberCommand * c2 = new TriggerRateHighNumberCommand;
	TriggerRateLowNumberCommand  * c3 = new TriggerRateLowNumberCommand;

	c2->set_digit1(3);
	c2->set_digit2(10);
	c3->set_digit1(12);
	c3->set_digit2(5);
	
	block->AddCommand(c1);
	block->AddCommand(c2);
	block->AddCommand(c3);
	
	script->AddBlock(block);

	cout << script->ToString() << endl;
	
	return 0;
}

void other()
{
		float pulseHeight = 0;
		
		// note that the two following integer type casts TRUNCATE.
		int highBit = int( (pulseHeight - 4.0429) / 2.01 );
		int lowBit = int( (pulseHeight - highBit * 2.01 - 4.0429) / .00783 );

          // Converting the low bit into a pair of HEX values
		int lowBit1 = lowBit / 16;		// INTEGER division.
		int lowBit2 = lowBit % 16;
}
