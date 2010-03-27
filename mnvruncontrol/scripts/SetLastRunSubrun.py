import shelve

d = shelve.open('last_run_subrun.db', 'c')

got_run = False
while not got_run:
    run = raw_input('Enter last Run: ')
    try:
        if int(run) > 0:
            d['run'] = run
            got_run = True
        else:
            print 'Run number must be a positive integer'
    except:
        print 'Run number must be a positive integer'       

got_subrun = False
while not got_subrun:
    subrun = raw_input('Enter last Subrun: ')
    try:
        if int(subrun) > 0:
            d['subrun'] = subrun
            got_subrun = True
        else:
            print 'Subrun number must be a positive integer'
    except:
        print 'Subrun number must be a positive integer' 

print 'Last Run set to '+str(d['run'])
print 'Last Subrun set to '+str(d['subrun'])
print '\'last_run_subrun.db\' updated/created'

d.close()

