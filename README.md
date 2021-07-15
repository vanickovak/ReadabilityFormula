README.md

This repo contains scripts for counting four readability formulas adapted for Czech:
Flesch Reading Ease, Flesch-Kincaid Grade Level, Coleman-Liau Index, and Automated Readability Index.

The input is folder "texts" with .txt  files. The output is json containing countings for every txt file: number of syllables, words, sentences, and all four formulas and number for Flesch Reading Ease derived from Russian data.
The parsing is done by API UDPipe: https://ufal.mff.cuni.cz/udpipe

More info in article:
Bendová, K. Using a parallel Corpus to adapt the Flesch Reading Ease Formula to Czech. To appear in Jazykovedný časopis.




