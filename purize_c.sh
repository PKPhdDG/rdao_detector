#!/usr/bin/env bash

if ! [ -x "$(command -v gcc)" ]
  then
  echo "Cannot find gcc"
  exit 1
else
  echo "gcc is found"
fi

if [ "$#" -eq 0 ]
  then
  echo "Not enough arguments"
  exit 2
fi

for file in "$@"
do
  echo "Trying purize $file"
  if ! [ -f "$file" ]
    then
    echo "Skipping $file"
    continue
  fi
  if ! [ "$(file -i "$file" | cut -d' ' -f2)" = "text/x-c" ] && ! [ -x "$(gcc -I./utils/fake_libc_include -E $file > $file.pure)" ]
    then
    echo "$file is purified with success"
  fi
done
