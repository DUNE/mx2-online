using System;
using System.Collections.Generic;
using System.Text;

namespace MinervaGUI
{
    public class FEInfo
    {
        private int CrocID;
        private int ChannelID;
        private int FeID;

        public FEInfo(int myCrocID, int myChannelId, int myFeID)
        {
            CrocID = myCrocID;
            ChannelID = myChannelId;
            FeID = myFeID;
        }
        public struct StructTemperature { public double Min; public double Max; public double Mon;}
        public struct StructHVActual { public int Min; public int Max; public int Mon;}
        public struct StructHVPeriodAuto { public int Min; public int Max; public int Mon;}
        public struct ChannelAmplitude { public int Min; public int Max; public int Mon;}

        public int CROCID { get { return CrocID; } }
        public int CROCCHID { get { return ChannelID; } }
        public int FEID { get { return FeID; } }
        public bool IsMonitored = false;
        public StructTemperature Temperature = new StructTemperature();
        public StructHVActual HVActual = new StructHVActual();
        public StructHVPeriodAuto HVPeriodAuto = new StructHVPeriodAuto();
        public ChannelAmplitude[,] TripChannelAmplitude = new ChannelAmplitude[6, 36];

    }
}
