#!/bin/sh

ps -leaf | grep python          | grep -v grep
ps -leaf | grep MinervaNearline | grep -v grep
ps -leaf | grep event_builder   | grep -v grep

