#/bin/bash
start=$1
end=$2
git log $start...$end --pretty=format:'- %s ([view commit](http://github.com/emi80/idxtools/commit/%H))' --reverse | grep "#"
