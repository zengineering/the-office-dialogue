#!/usr/bin/env sh

build/install/analysis/bin/theOffice ../the-office-quotes.sqlite correctDb
build/install/analysis/bin/theOffice ../the-office-quotes.sqlite countCharacterLines -l 100

# corrections needed in output json 
#  (Pete in seasons < 9)
#  (Clark in seasons < 9)
