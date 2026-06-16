#! /bin/bash

# generates I3 table in the SPIE paper

perl -anle 'printf("$F[0]   & $F[1]  & $F[2]  & $F[3]     & $F[4]      & %8.2f      & %-5d        & $F[9]   & %3d   & $F[11]   \\\\\n", $F[5], $F[8], $F[10])'
exit

