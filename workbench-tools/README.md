# Analytics Workbench Tool Suite

## Setup
Please install modules from requirements.txt by running

`pip install -r requirements.txt`

then install Tool Suite by running

`python setup.py install`

ESA uses polyglot, which can be hard to install depending on your operating system.
This usually stems from problems installing pyicu (and then also pycld).
If that is the case for you on a windows system, you can try installing that by downloading the appropriate whl file(s) for your system from:
https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyicu (& https://www.lfd.uci.edu/~gohlke/pythonlibs/#pycld2)
(for example for 64bit Windows Python3.6 that's PyICU‑2.6‑cp36‑cp36m‑win_amd64.whl and pycld2‑0.41‑cp36‑cp36m‑win_amd64.whl)
and installing it with

`python -m pip install *path*/*filename*`

after that installing polyglot should work by either running

`pip install -r requirements.txt` again oder specifically installing polyglot with

`pip install polyglot`