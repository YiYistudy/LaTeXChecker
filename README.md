# LaTeXChecker

This is an implementation for checking LaTeX source files using multiple typesetting styles for one manuscript. 

None of the versions of the script modify any LaTeX source files. They run in read-only mode. 

## checkCite.py (LaTeXChecker v1.0)

This script is used to check the LaTeX files without understanding them. 

This script will no longer be under maintenance.

You can still use this version to handle the situation where the input is a folder if you wish to. 

Otherwise, please always use the latest version among all the afterward versions where the input is the main TEX file. 

## checkLaTeX.py (LaTeXChecker v1.1 - v1.9)

This script is used to check the LaTeX files, supporting complex structures. 

Here are some incomplete implementations based on baseline ideas. 

Starting from ``v1.1``, the input should be the main TEX file instead of a folder. 

### v1.3

In this version, some functions are accomplished. 

However, it is not an optimal way to handle LaTeX checking tasks. 

This version of the script cannot run. It acts as a thought provider here. 

### v1.5

The ``Pointer`` and the ``Structure`` are separated. 

Compared with ``v1.3``, the codes are more readable and the thought is more feasible. 

This version of the script cannot run. It acts as a thought provider here. 

### v1.7

This is the last version before v2.0, which leads to the mature structure-building idea. 

The active mode is used in the parsing with the character-by-character reading. 

## LaTeXChecker (LaTeXChecker v2.0 - v2.9)

Start to be a mature checker with file tracking and structure recognition. 

### v2.0

This is the initial version of ``LaTeXChecker.py`` that supports complex structures with understanding the LaTeX files. 

### v2.1

Interaction is accomplished in this version. 

Initial support to command definitions is added. 

More complex situations are considered during the resolution. 

### v2.3 (20241111)

Add support for label and citation checking, covering parts of the functions in LaTeXChecker v1.0. 

### v2.4 (20241112)

Cover all the checking functions in LaTeXChecker v1.0. 

Add support to check whether all the structures are closed. 

Fix bugs in the stack of the pointer. 

Support more commands. 

### v2.5 (20241116)

Adjust the style of the connection lines. 

Fix some bugs. 

Change the behaviors for ``.gv`` files. Revise the extension ``.gz`` to ``.gv``. 

Change the option recognition mode to the non-case-sensitive one. 

### v2.6 (20241124)

Fix the bug of using ``\end{document}`` to end sections and subsections. 

Print the information on the leaving structure node mentioned above for debugging information via a queue. 

Add support for newly defined environments. 

### v2.7 (20241130)

Formalize the main body ``\xxx{yyy}`` recognition. 

### v2.8 (20241227)

Merry Christmas! 

The calculation of the number of references per paper, section, subsection, and subsubsection is added. 

Thanks to [@yiyistudy](https://github.com/yiyistudy) for providing the idea of adding an extendable dictionary to accomplish the calculation. 

This update is debugged once and successfully passed after it was written, marking the implementation of all features in ``v1.0``. 

The logic of selecting a main TEX file in a folder containing multiple TEX files is adjusted. 

![screenshot.png](screenshot.png)
