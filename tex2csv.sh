#!/usr/bin/bash
# Create CSV data from $1.tex and places it in $1.csv (overwriting whatever was there)
# Written by Marcel Goh on 24 January 2021

awk 'BEGIN { read = 0; skip = 0; }\
    $1 == "\\midrule" { read = 1; print ""; next }\
    $1 == "\\bottomrule" { read = 0; skip=1-skip }\
    read == 1 && skip == 0 { print $0 }' ./charts/$1.tex | # delete everything except lines ...
    # ... that are between EVERY OTHER \midrule and \bottomrule pair
sed 's/&/,/g' | # replace '&' characters with commas (thereby converting to csv)
tr -d "[:blank:]" | # delete extra horizontal whitespace
sed $'s/\\\\//g' | # delete trailing '\\'
sed 's/-//g' | # delete dashes
sed 's/rlap{}//g' | # delete "right overlap" macro
awk 'BEGIN { FS=IFS="," }\
    {for (i=1;i<=NF;++i) {\
        if (substr($i, 1, 1) == "?") { printf "%s,",substr($i, 3, length($i)-3); }\
        else { printf "%s,", $i; }\
    } printf "\n";}' > ./csv/$1.csv # delete ?{ and the corresponding }


