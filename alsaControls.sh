#!/usr/bin/env bash

/usr/bin/amixer -D equal controls | sed -n 's/.*\([0-9][0-9]\. [[:digit:]]\+ [k\?Hz]\+\).*/\1/p'