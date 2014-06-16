Program Features: All features from HW2 + Polygon filling
Language: Python
OS: Linux (Tux)
Compiler: None
Name of file containing main(): CG_hw3
How to compile: N/A (No makefile) (please let me know if you'd rather
have a makefile that does nothing? So you can type 'make'.)
How to run: ./CG_hw3 -h

Regarding the late submission:
If it means anything, check out the global_vars.py file.
There is a flag at the bottom to use a broken floating point to
integer conversion.
That bug is what held up my submission. You cans see the bug has some 
very strange effects when viewing the end image.
The bug manifests in code as int(172.0) = 171? Weird right? 
Must actually be 171.9999 being truncated.
Solution was to round the floating point first.
int(round(172.0)) = 172 :)
