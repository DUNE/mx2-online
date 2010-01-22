#include <string>
#include <fstream>

#include "Scripts/CommandScript.h"

namespace Minerva
{
	class LIScriptManager
	{
		public:
			LIScriptManager();
			
			bool Create();
			bool Verify();
			bool Validate();
			bool Describe();
			
			inline       bool            get_noInitialization()      const { return noInitialization;      };
			inline       bool            get_noPulseConfig()         const { return noPulseConfig;         };
			inline       float           get_pulseHeight()           const { return pulseHeight;           };
			inline       int             get_pulseWidth()            const { return pulseWidth;            };
			inline       bool            get_noLEDconfig()           const { return noLEDconfig;           };
			inline       std::string     get_LEDgroup()              const { return LEDgroup;              };
			inline       bool            get_noTriggerConfig()       const { return noTriggerConfig;       };
			inline       bool            get_triggerInternal()       const { return triggerInternal;       };
			inline       int             get_triggerRateLowNumber()  const { return triggerRateLowNumber;  };
			inline       int             get_triggerRateHighNumber() const { return triggerRateHighNumber; };
			inline       bool            get_requireResponse()       const { return requireResponse;       };
			inline const std::string   & get_responseRequired()      const { return responseRequired;      };
			inline const std::string   & get_responseSeparator()     const { return responseSeparator;     };
			inline       bool            get_doReset()               const { return doReset;               };
			
			inline const std::string   & get_fileName()              const { return fileName;              };
			inline const std::ifstream & get_inFile()                const { return inFile;                };
			inline const std::ofstream & get_outFile()               const { return outFile;               };
			
			inline const CommandScript * get_inScript()              const { return inScript;              };
			inline const CommandScript * get_outScript()             const { return outScript;             };

			
			inline void  set_noInitialization      (float       newNoInitialization        ) { noInitialization = newNoInitialization; };
			inline void  set_noPulseConfig         (float       newNoPulseConfig           ) { noPulseConfig = newNoPulseConfig; };
			       void  set_pulseHeight           (float       newPulseHeight             );
			       void  set_pulseWidth            (int         newPulseWidth              );
			inline void  set_noLEDConfig           (float       newNoLEDConfig             ) { noLEDconfig = newNoLEDConfig; };
			       void  set_LEDgroup              (std::string newLEDgroup                );
			inline void  set_noTriggerConfig       (float       newNoTriggerConfig         ) { noTriggerConfig = newNoTriggerConfig; };
			inline void  set_triggerInternal       (bool        newTriggerInternal         ) { triggerInternal = newTriggerInternal; };
			       void  set_triggerRateLowNumber  (int         newTriggerRateLowNumber    );
			       void  set_triggerRateHighNumber (int         newTriggerRateHighNumber   );
			inline void  set_requireResponse       (bool        newRequireResponse         ) { requireResponse = newRequireResponse; };
			inline void  set_responseRequired      (std::string newResponseRequired        ) { responseRequired = newResponseRequired; };
			inline void  set_responseSeparator     (std::string newResponseSeparator       ) { responseSeparator = newResponseSeparator; };
			inline void  set_doReset               (float       newDoReset                 ) { doReset = newDoReset; };

			inline void  set_fileName              (std::string newFileName                ) { fileName = newFileName; };

		
		private:
			LIScriptManager(const LIScriptManager&) {};		// no reason to be using the copy constructor.

			// used internally to turn all of the member variables below into usable CommandScripts
			bool CreateScriptFromParameters();
			// used internally to parse an infile.
			bool ParseFile();
		
			bool          noInitialization;
			bool          noPulseConfig;
			float         pulseHeight;
			int           pulseWidth;
			bool          noLEDconfig;
			std::string   LEDgroup;
			bool          noTriggerConfig;
			bool          triggerInternal;
			int           triggerRateLowNumber;
			int           triggerRateHighNumber;
			bool          requireResponse;
			std::string   responseRequired;
			std::string   responseSeparator;
			bool          doReset;
			
			std::string   fileName;
			std::ifstream inFile;
			std::ofstream outFile;
			
			CommandScript * inScript;
			CommandScript * outScript;
	};

};
