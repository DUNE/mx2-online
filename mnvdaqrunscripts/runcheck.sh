#!/bin/sh

ps -leaf | grep python | grep -v grep
ps -leaf | grep event_builder | grep -v grep
ps -leaf | grep et_monitor | grep -v grep
ps -leaf | grep minervadaq | grep -v grep

