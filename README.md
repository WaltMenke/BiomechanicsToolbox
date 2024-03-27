# BiomechanicsToolbox

![tools](https://github.com/WaltMenke/BiomechanicsToolbox/assets/142276466/db4037b3-256a-45a1-a818-cdaae1543ac6)
## Purpose
A Python-based GUI designed to help with more efficient Biomechanics data processing and presentation.
Please refer to the [BiomechancisToolbox.docx](BiomechanicsToolbox.docx) for further information about capabilities and how to operate the program.

If downloading all files from the main branch to run in your own IDE or terminal, run the [BiomechanicsToolbox.py](BiomechanicsToolbox.py) script only to initiate the program- all other python scripts are for functions or subprocess calls.

## Current Version: v1.0.0
Get the current release version [here](https://github.com/WaltMenke/BiomechanicsToolbox/releases/tag/v1.0.0). 

## Package Installation
It is HIGHLY recommended to use a virtual environment and use:
`pip install -r ToolboxRequirements.txt` 
to obtain the required packages and version as easily as possible.

## Eexecutable Options
If you would like to use an executable version of the program instead of running it through the command line or an IDE, I've uploaded a ZIP file to [Dropbox](https://www.dropbox.com/scl/fi/ftgjmmf4ueztktae1tgce/BiomechanicsToolboxExecutable.zip?rlkey=g2syxgvrmwornxatgzvnb9s96&dl=0
) that contains the required files generated by PyInstaller.

Alternatively, you can download the Github folder [BuildExecutable](BuildExecutable) from the repository, navigate to that directory from a terminal/powershell and run the following code to generate an executable locally:

`pyinstaller --onefile -i"BT_Icon.ico" BiomechanicsToolbox.py`

_Please note that the executable version of this program will often be considerably behind the standalone Python scripts._

## Example Files
As of March 24th, 2024 there is a folder containing example input and output files for multiple functions. This will allow you to test the function inputs, understand the data/file structures required by the program, and look at expected outputs from these files.

## Features
* Script Gen: generates Visual3D scripts and model files based on input templates with attached heights and weights.
* Batch
* Normalize
* Event Pick
* Event Compile
* Ensemble
* SPM (partially implemented)
* EMG (not available)

Please reach out to me if you have feedback, bug reports, etc!
