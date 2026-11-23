Temporary README:

Recommended way of using PFNK:
Open a miniconda enviroment you want to install PFNK into:

conda activate your_enviroment

Navigate to the repository folder of PFNK (the folder containing this README and the pyproject.toml) using cd

Install PFNK into that enviroment using:

python -m pip install -e .

You can omit the -e flag but using it allows you to simply pull changes to the libary and they will automatically work without needing to reinstall PFNK

Now you can import stuff from PFNK. E.g. :

from PFNK.plotting import PlotHelper


If you use Jupyter Notebooks it might be advantages to add

%load_ext autoreload
%autoreload 2

to the start of the notebook.

This removes the need to restart the kernel if you change the files of PFNK.


Please let me know if you find any mistakes I made or encounter any errors with PFNK.