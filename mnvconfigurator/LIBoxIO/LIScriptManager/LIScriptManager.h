#include <string>
#include "Scripts/CommandScript.h"

namespace Minerva
{
	enum LEDGroup

	class LIScriptManager
	{
		public:
			LIScriptManager();
			
			inline float       get_pulseHeight()           const { return pulseHeight;           };
			inline float       get_pulseWidth()            const { return pulseWidth;            };
			inline char        get_LEDgroup()              const { return LEDgroup;              };
			inline bool        get_triggerInternal()       const { return triggerInternal;       };
			inline int         get_triggerRateLowNumber()  const { return triggerRateLowNumber;  };
			inline int         get_triggerRateHighNumber() const { return triggerRateHighNumber; };
			inline bool        get_requireResponse()       const { return requireResponse;       };
			inline std::string get_responseRequired()      const { return responseRequired;      };
			inline std::string get_responseSeparator()     const { return responseSeparated;     };
			inline std::string get_fileName()              const { return fileName               };
			
			       void  set_pulseHeight           (float newPulseHeight         );
			       void  set_pulseWidth            (float newPulseWidth          );
			       void  set_LEDgroup              (char  newLEDgroup            );
			inline void  set_triggerInternal       (bool  newTriggerInternal     ) { triggerInternal = newTriggerInternal; };
			       void  set_triggerRateLowNumber  (int  newTriggerRateLowNumber );
			       void  set_triggerRateHighNumber (int  newTriggerRateHighNumber);
			inline void  set_requireResponse       (bool newRequireResponse      ) { requireResponse = newRequireResponse; };
			       void  set_responseRequired      (std::string responseRequired );
			       void  set_responseSeparator     (std::string responseSeparator);
			       void  set_fileName              (std::string newFileName      );
			
			inline const CommandScript * get_inScript()  const { return inScript; };
			inline const CommandScript * get_outScript() const { return outScript; };
		
		private:
			float       pulseHeight;
			float       pulseWidth;
			char        LEDgroup;
			bool        triggerInternal;
			int         triggerRateLowNumber;
			int         triggerRateHighNumber;
			bool        requireResponse;
			std::string responseRequired;
			std::string responseSeparator;
			
			std::string fileName;
			
			CommandScript * inScript;
			CommandScript * outScript;
	};

};
