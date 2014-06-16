Program Features: 
	Front/Back Clipping does not seem to work. 
	Z buffering and depth cueing appears ~90+% correct.
	Command line arguments needed slight changes.
Language: Python
OS: Linux (Tux)
Compiler: None
Name of file containing main(): CG_hw5
How to compile: N/A (No makefile)
(Let me know if you need a make file for your scripts, I don't provide
one as it wouldn't really do anything)
How to run: ./CG_hw5 -h

**** Command line args: ****
Having numbered arguments screws up negative number arguments,
for example: -3 vs. -3.2 , is "-3" flag with .2 as argument?
For files you must use "-f1","-f2","-f3" instead of "-1","-2","-3".
Sorry, a solution may exist but I don't have time to implement extra arg
parsing functionality.

**** Front/back clipping: ****
This does not appear to work. Depth cueing doesn't seem to show the 
'cut out' models as anticipated. Not sure why.

**** Depth cueing: ****
Vertex Z values do not range evenly from -1.0 to 1.0 for each model.
For instance, the bound-sprellpsd.smf model:
Minimum Z: -0.9375
Maximum Z: -0.3125
If you depth cue for Z over the range -1.0 to 1.0 you are not using
the whole range of colors since actual Z's fall in a smaller range.
Again, for instance, the bound-cow.smf model:
Minimum Z: -0.9796
Maximum Z: 0.1604
The best I could do for this was to store the max and min Z values
for each model and use that range for linear depth cueing.
Results still do not match examples exactly though...

**** Z buffering: ****
This appears mostly correct. However, there are some 
unexplained artifacts/edges that cause my images to differ 
slightly from the examples.
