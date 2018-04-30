#!/usr/bin/env sh

set -e

./gradlew build
./gradlew installDist 
export PATH="$PWD/build/install/analysis/bin:$PATH"
