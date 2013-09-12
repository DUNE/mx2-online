#!/usr/bin/perl

#this perl script looks for zombie tunnel processes left over from a crashed run control.
#if it finds them, it kills them. 

$proc[0] = "'ssh -o ServerAliveInterval=30 '";#-NL 1090:localhost:1090 mnvonline@mnvonline1.fnal.gov'";

foreach $var (@proc) {
    print "Looking to kill old $var...$cmd.... \n";
    while (!system("ps -fC 'ssh -o ServerAliveInterval=30' | grep 'ssh -o ServerAliveInterval=30'")) {
	$counter++;
	@fields = split/\s+/,`ps -fC 'ssh -o ServerAliveInterval=30' | grep 'ssh -o ServerAliveInterval=30'`;
	print "@fields \n";#
	$rcpid = $fields[1]; # 0 is user
	$PPID = $fields[2]; # Gives PPID number 
	
	print "Rogue PID is $rcpid... PPID is $PPID killing...$address\n";
	system("kill -9 $rcpid");
	print "Killed $rcpid!\n";
	print "Waiting...\n";
	system("sleep 1");
    }
}

if(system("ps -fC 'ssh -o ServerAliveInterval=30' | grep 'ssh -o ServerAliveInterval=30' ")){
    print "All zombie tunels have been closed. \n";
}
