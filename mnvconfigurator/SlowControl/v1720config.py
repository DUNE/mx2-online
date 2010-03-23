WriteToFile={'Do Not Write':0, 'On Command':1, 'Continuous':2}
AppendMode={'Overwrite':0, 'Append':1}
ReadoutMode={'Single D32':0, 'BLT32':1, 'MBLT64':2}



##FileKeys={'Comment':'#', 'WriteToFile':'WRITE_TO_FILE', 'AppendMode':'APPEND_MODE',
##          'ReadoutMode':'READOUT_MODE', 'BLTSize':'BLT_SIZE'}
import wx
import sys

def DIGcfgFileLoad(fullpathname):
    '''Read a configuration file and write it into the current hardware'''
    KeyComment='#'
    KeyWriteToFile='WRITE_TO_FILE'
    KeyAppendMode='APPEND_MODE'
    KeyReadoutMode='READOUT_MODE'
    KeyBLTSize='BLT_SIZE'
    KeyOutputFormat='OUTPUT_FORMAT'
    KeyWriteRegister='WRITE_REGISTER'
    flags={KeyWriteToFile:None, KeyAppendMode:None, KeyReadoutMode:None,
           KeyBLTSize:None, KeyOutputFormat:None, KeyWriteRegister:{}}
    f=open(fullpathname,'r')
    i=0; lines=[]
    for line in f:
        i+=1
        line=line.replace('\n', '')
        if line.strip()=='' or line[0]==KeyComment: continue
        words = line.split(' ')
        lines.append(line)
        if words[0]==KeyWriteToFile:
            if int(words[1],10) in WriteToFile.values():
                if flags[KeyWriteToFile]==None: flags[KeyWriteToFile]=int(words[1],10); continue
                else: raise Exception('Error in line #%s: %s\n%s'%(i,line,'item already defined'))
            else: raise Exception('Error in line #%s: %s\n%s'%(i,line,WriteToFile))
        if words[0]==KeyAppendMode:
            if int(words[1],10) in AppendMode.values():
                if flags[KeyAppendMode]==None: flags[KeyAppendMode]=int(words[1],10); continue
                else: raise Exception('Error in line #%s: %s\n%s'%(i,line,'item already defined'))    
            else: raise Exception('Error in line #%s: %s\n%s'%(i,line,AppendMode))
        if words[0]==KeyReadoutMode:
            if int(words[1],10) in ReadoutMode.values():
                if flags[KeyReadoutMode]==None: flags[KeyReadoutMode]=int(words[1],10); continue
                else: raise Exception('Error in line #%s: %s\n%s'%(i,line,'item already defined'))
            else: raise Exception('Error in line #%s: %s\n%s'%(i,line,ReadoutMode))
        if words[0]==KeyBLTSize:
            if flags[KeyBLTSize]==None: flags[KeyBLTSize]=int(words[1]); continue
            else: raise Exception('Error in line #%s: %s\n%s'%(i,line,'item already defined'))
        if words[0]==KeyOutputFormat:
            value=int(words[1],16)
            if value&0x3F==value:
                if flags[KeyOutputFormat]==None: flags[KeyOutputFormat]=value; continue
                else: raise Exception('Error in line #%s: %s\n%s'%(i,line,'item already defined'))
            else: raise Exception('Error in line #%s: %s\n%s'%(i,line,'must be a 6 bit(flags) number'))
        if words[0]==KeyWriteRegister:
            if len(words)<3: raise Exception('Error in line #%s: %s\n%s'%(i,line,'address or data missing'))
            addr=int(words[1],16); value=int(words[2],16)
            if addr&0xFFFF==addr and value&0xFFFFFFFF==value:                
                if flags[KeyWriteRegister].has_key(addr):
                    raise Exception('Error in line #%s: %s\n%s'%(i,line,'item already defined'))
                else: flags[KeyWriteRegister][addr]=value; continue
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
        fullpathname=r'/work/software/cristian/mnvconfigurator/SlowControl/v1720config.digcfg'
        flags, lines = DIGcfgFileLoad(fullpathname)
        print '\n'.join(lines)
        print
        print flags                              
    except: print str(sys.exc_info()[0]) + ", " + str(sys.exc_info()[1])
