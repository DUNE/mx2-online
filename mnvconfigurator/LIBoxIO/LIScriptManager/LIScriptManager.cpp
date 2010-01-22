#include "LIScriptManager.h"

#include "Scripts/GenericScript.h"

#include "Blocks/InitializeBlock.h"
#include "Blocks/LEDSelectionBlock.h"
#include "Blocks/PulseSetupBlock.h"
#include "Blocks/ResetBlock.h"
#include "Blocks/TriggerSetupBlock.h"

#include "Commands/InitializeCommand.h"
#include "Commands/LEDSelectionCommand.h"
#include "Commands/PulseHeightHighBitCommand.h"
#include "Commands/PulseHeightLowBitsCommand.h"
#include "Commands/PulseHeightStoreCommand.h"
#include "Commands/PulseWidthCommand.h"
#include "Commands/ResetCommand.h"
#include "Commands/TriggerExternalCommand.h"
#include "Commands/TriggerInternalCommand.h"
#include "Commands/TriggerRateHighNumberCommand.h"
#include "Commands/TriggerRateLowNumberCommand.h"

#include <string>
#include <fstream>
#include <iostream>
#include <stdexcept>

namespace Minerva
{
	// --------------------------------------------------------------------
	// LIScriptManager::LIScriptManager()
	//    default constructor
	// --------------------------------------------------------------------
	LIScriptManager::LIScriptManager()
	   : inScript(NULL), outScript(NULL)
	{}
	
	// --------------------------------------------------------------------
	// LIScriptManager::CreateScriptFromParameters()
	//    builds a GenericScript object from the parameters set
	//    in the LIScriptManager object.
	// --------------------------------------------------------------------
	bool LIScriptManager::CreateScriptFromParameters()
	{
		if (outScript != NULL)
			delete outScript;
			
		outScript = new GenericScript;
		
		if (!noInitialization)
		{
			InitializeBlock * initializeBlock = new InitializeBlock;
			initializeBlock->AddCommand(new InitializeCommand);
		
			outScript->AddBlock(initializeBlock);
		}
		
		if (!noPulseConfig)
		{
			PulseSetupBlock * pulseBlock = new PulseSetupBlock;
			
			int highBit = int( (pulseHeight - 4.0429) / 2.01 );
			int lowBit  = int( (pulseHeight - highBit * 2.01 - 4.0429) / .00783 );
			int lowBit1 = lowBit / 16;		// INTEGER division.
			int lowBit2 = lowBit % 16;
			
			PulseHeightHighBitCommand * highCommand  = new PulseHeightHighBitCommand(highBit);
			PulseHeightLowBitsCommand * lowCommand   = new PulseHeightLowBitsCommand(lowBit1, lowBit2);
			PulseHeightStoreCommand   * storeCommand = new PulseHeightStoreCommand;
			PulseWidthCommand         * widthCommand = new PulseWidthCommand(pulseWidth);
			
			pulseBlock->AddCommand(highCommand);
			pulseBlock->AddCommand(lowCommand);
			pulseBlock->AddCommand(storeCommand);
			pulseBlock->AddCommand(widthCommand);
			
			outScript->AddBlock(pulseBlock);
		}
		
		if (!noLEDconfig)
		{
			std::string LEDcodes = "0abcdefghijklmnopqrstuv";
			
			int hasA = (LEDgroup.find('A') == std::string::npos);
			int hasB = (LEDgroup.find('B') == std::string::npos);
			int hasC = (LEDgroup.find('C') == std::string::npos);
			int hasD = (LEDgroup.find('D') == std::string::npos);
			
			int inverseAddress = hasA + 2*hasB + 4*hasC + 8*hasD;
			char LEDcode = LEDcodes[15 - inverseAddress];
			
			LEDSelectionBlock   * LEDblock   = new LEDSelectionBlock;
			LEDblock->AddCommand(new LEDSelectionCommand(LEDcode));
			
			outScript->AddBlock(LEDblock);
		}
		
		if (!noTriggerConfig)
		{
			TriggerSetupBlock * triggerBlock = new TriggerSetupBlock;
			
			if (triggerInternal)
			{
				int h1 = triggerRateHighNumber / 16;
				int h2 = triggerRateHighNumber % 16;
				int l1 = triggerRateLowNumber / 16;
				int l2 = triggerRateLowNumber % 16;

				TriggerInternalCommand       * internalCommand   = new TriggerInternalCommand;
				TriggerRateHighNumberCommand * highNumberCommand = new TriggerRateHighNumberCommand(h1, h2);
				TriggerRateLowNumberCommand  * lowNumberCommand  = new TriggerRateLowNumberCommand(l1, l2);
				
				triggerBlock->AddCommand(internalCommand);
				triggerBlock->AddCommand(highNumberCommand);
				triggerBlock->AddCommand(lowNumberCommand);
				
			}
			else
			{
				TriggerExternalCommand * externalCommand = new TriggerExternalCommand;
				triggerBlock->AddCommand(externalCommand);
			}
			
			outScript->AddBlock(triggerBlock);
		}
		
		if (doReset)
		{
			ResetBlock * resetBlock = new ResetBlock;
			resetBlock->AddCommand(new ResetCommand);
			
			outScript->AddBlock(resetBlock);
		}
		
		return true;
	}
	
	// --------------------------------------------------------------------
	// LIScriptManager::ParseFile()
	//    reads inFile and fills inScript with the appropriate structures.
	//    not implemented for now.
	// --------------------------------------------------------------------
	bool LIScriptManager::ParseFile()
	{
		return false;
	}

	// --------------------------------------------------------------------
	// LIScriptManager::Create()
	//    writes out a file generated from outScript.
	// --------------------------------------------------------------------
	bool LIScriptManager::Create()
	{
		if ( !CreateScriptFromParameters() )
			return false;
			
		outFile.open(fileName.c_str());
		if ( !outFile.is_open() )
			return false;
			
		outFile << outScript->ToString() << std::flush;

		outFile.close();
		
		return true;
	}
	
	// --------------------------------------------------------------------
	// LIScriptManager::Validate()
	//    confirms that a file would be understandable by the LI box.
	// --------------------------------------------------------------------
	bool LIScriptManager::Validate()
	{
		inFile.open(fileName.c_str());
		if ( !inFile.is_open() )
			return false;
		
		try
		{
			ParseFile();
		}
		catch (...)
		{
			return false;
		}
		
		return true;
		
		inFile.close();	
	}

	// --------------------------------------------------------------------
	// LIScriptManager::Create()
	//    verfies if a file is equivalent to the one generated from the
	//    arguments passed on the command line
	// --------------------------------------------------------------------
	bool LIScriptManager::Verify()
	{
		if ( !CreateScriptFromParameters() )
			return false;
			
		if (!Validate())
			return false;
			
		return ( (*inScript) == (*outScript) );
	}

	// --------------------------------------------------------------------
	// LIScriptManager::Create()
	//    outputs an annotated version of the input file to STDOUT,
	//    explaining the function of each command
	// --------------------------------------------------------------------
	bool LIScriptManager::Describe()
	{
		bool valid = Validate();
		
		if (valid)
			std::cout << inScript->Describe() << std::flush;

		return true;
	}

	// --------------------------------------------------------------------
	// various (non-trivial) setters for the properties follow.
	// --------------------------------------------------------------------

	void LIScriptManager::set_pulseHeight(float newPulseHeight)
	{
		if (newPulseHeight < 4.05 || newPulseHeight > 12.07)
			throw std::domain_error("Pulse height must be between 4.05 and 12.07 volts (inclusive).");
		
		pulseHeight = newPulseHeight;
		return;
	}
	
	void LIScriptManager::set_pulseWidth(int newPulseWidth)
	{
		if (newPulseWidth < 0 || newPulseWidth > 7)
			throw std::domain_error("Pulse width must be between 0 and 7 inclusive (~20-35 ns).");
			
		pulseWidth = newPulseWidth;
		return;
	}
	
	void LIScriptManager::set_LEDgroup(std::string newLEDgroup)
	{
		std::string okayGroups = "ABCD";
		bool nogood = false;
		
		if ( newLEDgroup.length() > 4 || newLEDgroup.length() == 0 )
			nogood = true;

		for (int i = 0; i < newLEDgroup.length(); i++)
		{
			if (okayGroups.find(newLEDgroup[i]) == std::string::npos)		// is this one of A, B, C, or D?
				nogood = true;
			else if (newLEDgroup.find(newLEDgroup[i], i+1) != std::string::npos) // does this letter occur more than once?
				nogood = true;
		}
		     
		if ( nogood )
			throw std::domain_error("LED group(s) must be specifed like this: ACD, AB, D, etc.");
			
		LEDgroup = newLEDgroup;
		return;
	}

	void LIScriptManager::set_triggerRateLowNumber(int newrate)
	{
		if (newrate < 0 || newrate > 0xff)
			throw std::domain_error("Trigger rate low number must be between 00 and FF...");
		
		triggerRateLowNumber = newrate;
		return;
	}

	void LIScriptManager::set_triggerRateHighNumber(int newrate)
	{
		if (newrate < 0 || newrate > 0xff)
			throw std::domain_error("Trigger rate high number must be between 00 and FF...");
		
		triggerRateHighNumber = newrate;
		return;
	}

};
