#!/usr/bin/perl

$proc[0] = "minervadaq";

foreach $var (@proc) {
	print "Looking to kill $var...\n";
	system("ps -fC $var | grep $var");
	while (!system("ps -fC $var | grep $var")) {
		@fields = split/\s+/,`ps -fC $var | grep $var`;
		$rcpid = $fields[1]; # 0 is user
		print "Rogue PID is $rcpid... killing...\n";
		system("kill -9 $rcpid");
		print "Killed!\n";
		print "Waiting...\n";
		system("sleep 1");
	}
}


