#!/usr/bin/perl

$proc_list[0] = "python | grep mnvchkdst.py";
$proc_list[1] = "gmplotter | grep gmplotter";

foreach $proc (@proc_list) {
	while (!system("ps -fC $proc")) {
		@fields = split/\s+/,`ps -fC $proc`;
		$rcpid = $fields[1]; # 0 is user
		print "Check DST PID is $rcpid... killing...\n";
		system("kill -9 $rcpid");
		print "Killed!\n";
		print "Waiting...\n";
		system("sleep 1");
	}
}

