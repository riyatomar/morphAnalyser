#original dix
#apertium-destxt $1 | lt-proc -ac hi.morf.bin | apertium-retxt > $1-out.txt 

#LC project dix
# apertium-destxt $1 | lt-proc -ac hi.morfLC.bin | apertium-retxt > $1-out.txt


# Read from stdin and process with the pipeline
apertium-destxt | lt-proc -ac hi.morfLC.bin | apertium-retxt