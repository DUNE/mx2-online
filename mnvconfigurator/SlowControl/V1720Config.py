import wx
import sys

FileKeyComment='#'
FileKeyWriteToFile='WRITE_TO_FILE'
FileKeyAppendMode='APPEND_MODE'
FileKeyReadoutMode='READOUT_MODE'
FileKeyBLTSize='BLT_SIZE'
FileKeyOutputFormat='OUTPUT_FORMAT'
FileKeyWriteRegister='WRITE_REGISTER'
FormatData='Data'
FormatHeader='Header'
FormatConfigInfo='ConfigInfo'
FormatOneLineCH='OneLineCH'
FormatEventData='EventData'
FormatEventStat='EventStat'

WriteToFile={0:'Do Not Write', 1:'On Command', 2:'Continuous'}
AppendMode={0:'Overwrite', 1:'Append'}
ReadoutMode={0:'Single D32', 1:'BLT32', 2:'MBLT64'}
OutputFormat={FormatData:1, FormatHeader:2, FormatConfigInfo:4, FormatOneLineCH:8, FormatEventData:16, FormatEventStat:32}

def DIGcfgFileLoad(fullpathname):
    '''Read a V1720 configuration file.
    Return (flags, lines) where lines is a list of all configuration file's lines and flags is a dictionary
    flags={FileKeyWriteToFile:None, FileKeyAppendMode:None, FileKeyReadoutMode:None,
           FileKeyBLTSize:None, FileKeyOutputFormat:None, FileKeyWriteRegister:[]}'''
    flags={FileKeyWriteToFile:None, FileKeyAppendMode:None, FileKeyReadoutMode:None,
           FileKeyBLTSize:None, FileKeyOutputFormat:None, FileKeyWriteRegister:[]}
    f=open(fullpathname,'r')
    i=0; lines=[]
    for line in f:
        i+=1
        line=line.replace('\n', '')
        if line.strip()=='' or line[0]==FileKeyComment: continue
        words = line.split(' ')
        lines.append(line)
        if words[0]==FileKeyWriteToFile:
            if int(words[1],10) in WriteToFile.keys():
                if flags[FileKeyWriteToFile]==None: flags[FileKeyWriteToFile]=int(words[1],10); continue
                else: raise Exception('Error in line #%s: %s\n%s'%(i,line,'item already defined'))
            else: raise Exception('Error in line #%s: %s\n%s'%(i,line,WriteToFile))
        if words[0]==FileKeyAppendMode:
            if int(words[1],10) in AppendMode.keys():
                if flags[FileKeyAppendMode]==None: flags[FileKeyAppendMode]=int(words[1],10); continue
                else: raise Exception('Error in line #%s: %s\n%s'%(i,line,'item already defined'))    
            else: raise Exception('Error in line #%s: %s\n%s'%(i,line,AppendMode))
        if words[0]==FileKeyReadoutMode:
            if int(words[1],10) in ReadoutMode.keys():
                if flags[FileKeyReadoutMode]==None: flags[FileKeyReadoutMode]=int(words[1],10); continue
                else: raise Exception('Error in line #%s: %s\n%s'%(i,line,'item already defined'))
            else: raise Exception('Error in line #%s: %s\n%s'%(i,line,ReadoutMode))
        if words[0]==FileKeyBLTSize:
            if flags[FileKeyBLTSize]==None: flags[FileKeyBLTSize]=int(words[1]); continue
            else: raise Exception('Error in line #%s: %s\n%s'%(i,line,'item already defined'))
        if words[0]==FileKeyOutputFormat:
            value=int(words[1],16)
            if value&0x3F==value:
                if flags[FileKeyOutputFormat]==None: flags[FileKeyOutputFormat]=value; continue
                else: raise Exception('Error in line #%s: %s\n%s'%(i,line,'item already defined'))
            else: raise Exception('Error in line #%s: %s\n%s'%(i,line,'must be a 6 bit(flags) number'))
        if words[0]==FileKeyWriteRegister:
            if len(words)<3: raise Exception('Error in line #%s: %s\n%s'%(i,line,'address or data missing'))
            addr=int(words[1],16); value=int(words[2],16)
            if addr&0xFFFF==addr and value&0xFFFFFFFF==value:
                if addr in [tupl[0] for tupl in flags[FileKeyWriteRegister]] :
                    raise Exception('Error in line #%s: %s\n%s'%(i,line,'item already defined'))
                else: flags[FileKeyWriteRegister].append((addr, value)); continue
            else: raise Exception('Error in line #%s: %s\n%s'%(i,line,'address is 16bit, data is 32bit'))
        raise Exception('Error in line #%s: %s\n%s'%(i,line,'key not defined'))
    f.close()
    #check there is no NONE value!!!!
    for (k,v) in flags.items():
        if v==None or v=={}: raise Exception('missing parameter %s=%s'%(k,v))   
    return flags, lines


if __name__=='__main__':
##    app=wx.App()
##    frame=wx.Frame(None, -1, 'test frame')
##    dlg = wx.FileDialog(frame, message='READ V1720 Configuration', defaultDir='', defaultFile='',
##        wildcard='DIG Config (*.digcfg)|*.digcfg|All files (*)|*', style=wx.OPEN|wx.CHANGE_DIR)
##    if dlg.ShowModal()==wx.ID_OK:
##        #self.sc.HWcfgFileLoad(wx.FileDialog.GetPath(dlg))
##        DIGcfgFileLoad(wx.FileDialog.GetPath(dlg))
##    dlg.Destroy()
    try:
        #code used to debug DIGcfgFileLoad()
        fullpathname=r'/work/software/cristian/mnvconfigurator/SlowControl/v1720config.digcfg'
        flags, lines = DIGcfgFileLoad(fullpathname)
        print '\n'.join(lines)
        print
        print flags
        
    except: print str(sys.exc_info()[0]) + ", " + str(sys.exc_info()[1])
