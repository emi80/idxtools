#/bin/bash
start=$1
end=$2
git log $1...$2 --pretty=format:'- %s ([view commit](http://github.com/emi80/idxtools/commit/%H))' --reverse | grep "#"
