#!/bin/sh

JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64
JAVA_COMMAND=$JAVA_HOME/bin/java

$JAVA_COMMAND -cp "FightingICE.jar:lib/*:lib/lwjgl/*:lib/natives/linux/*" Main 
