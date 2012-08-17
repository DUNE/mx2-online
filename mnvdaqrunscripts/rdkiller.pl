#!/usr/bin/perl

$proc = "python | grep ReadoutDispatcher.py";

while (!system("ps -fC $proc")) {
	@fields = split/\s+/,`ps -fC $proc`;
	$rcpid = $fields[1]; # 0 is user
	print "Run Control PID is $rcpid... killing...\n";
	system("kill -9 $rcpid");
	print "Killed!\n";
	print "Waiting...\n";
	system("sleep 1");
}


