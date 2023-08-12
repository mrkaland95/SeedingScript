### While using EasyOCR, one of its dependencies must be downgraded for an executable to be possible(scikit).

### Code to downgrade:

### pip uninstall scikit-image
### pip install scikit-image==0.18.3


* You cannot seemingly use the logging framework in conjunction with the PySimpleGUI library.
* NOTE: The "__pycache__" directory should be deleted before doing a build, if a new source file has been added to the project.