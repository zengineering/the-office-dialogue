#!/usr/bin/env sh

build/install/analysis/bin/theOffice ../the-office-quotes.sqlite correctDb
build/install/analysis/bin/theOffice ../the-office-quotes.sqlite countCharacterLines -l 100

# corrections needed to output json (Pete in seasons < 9)
