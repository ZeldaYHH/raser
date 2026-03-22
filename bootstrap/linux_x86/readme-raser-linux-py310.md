# RASER 3.19 Linux Reference Workflow

This directory contains a validated Linux x86 reference workflow for running RASER with:

- external ROOT
- external Geant4
- geant4_pybind as the Geant4 Python interface
- Python 3.10
- devsim
- local editable installation of raser

This workflow is intended as a reference implementation for the new technical route:

- keep ROOT and Geant4 outside
- replace the old driver-centered path with pybind
- validate the core workflow first on Linux
- use the Linux workflow as the baseline for future Windows/macOS native adaptation

================================================================================
1. Current status
================================================================================

The following have been validated on Linux x86:

- Python 3.10.14
- ROOT 6.36.08 with PyROOT matching Python 3.10
- Geant4 11.2.2
- geant4_pybind
- devsim
- raser editable install
- raser field HPK-Si-LGAD -v
- raser signal HPK-Si-LGAD -g4 proton_beam -vol 200

This means the Linux reference workflow is not just importable, but already able to run core field and signal chains.

================================================================================
2. Technical route
================================================================================

The validated route is:

- external ROOT
- external Geant4
- Python 3.10 runtime
- geant4_pybind as the Geant4 binding layer
- devsim for field/device-related calculations
- raser installed from source

This workflow does not use the old driver as the core interface layer.

================================================================================
3. External dependencies
================================================================================

The following components are expected to be provided externally on the host side.

ROOT
----

Validated version:

- ROOT 6.36.08

Important:

- PyROOT must match the target Python version
- it is not enough that root-config exists
- the ROOT Python bindings must be built against Python 3.10 for this workflow

Geant4
------

Validated version:

- Geant4 11.2.2

Geant4 is kept external and accessed through geant4_pybind.

================================================================================
4. Python environment
================================================================================

Validated Python runtime:

- Python 3.10.14

The local environment includes:

- geant4-pybind
- devsim
- raser
- common runtime dependencies listed in requirements-linux-py310.txt

Two dependency files are recommended:

- requirements-linux-py310.txt: manually curated minimal runtime dependencies
- requirements-linux-py310-lock.txt: full lock/freeze file for local reproduction

================================================================================
5. Repository / working layout
================================================================================

Recommended local layout:

    ~/raser3.19/
    ├── README.txt
    ├── bootstrap/
    │   └── raser-linux-py310-pybind.def
    ├── scripts/
    │   ├── env_linux.sh
    │   ├── run_linux_env.sh
    │   ├── check_env.py
    │   └── test_linux_pybind_host.sh
    ├── requirements-linux-py310.txt
    ├── requirements-linux-py310-lock.txt
    ├── python/
    │   └── 3.10.14/
    ├── .venv310/
    ├── wheels/
    │   └── geant4_pybind-0.1.2-cp310-cp310-manylinux_2_27_x86_64.manylinux_2_28_x86_64.whl
    └── raser-src/

================================================================================
6. Helper scripts
================================================================================

scripts/env_linux.sh
--------------------

Sets the validated Linux runtime environment, including:

    ROOTSYS
    GEANT4_DIR
    RASER_SRC
    RASER_SETTING_PATH
    RASER_OUTPUT_PATH
    MPLBACKEND=Agg

scripts/run_linux_env.sh
------------------------

Unified entry point for running commands inside the validated Linux environment.

Example:

    ~/raser3.19/scripts/run_linux_env.sh python -m raser field HPK-Si-LGAD -v

scripts/check_env.py
--------------------

Prints Python version, key environment variables, and checks imports for:

    ROOT
    geant4_pybind
    devsim
    raser

scripts/test_linux_pybind_host.sh
---------------------------------

Quick host-side smoke test for the validated environment.

================================================================================
7. Installation notes
================================================================================

7.1 Python 3.10
---------------

The validated workflow uses Python 3.10.14. On the test machine, Python 3.10 was built locally because the system package manager did not provide it directly.

7.2 ROOT for Python 3.10
------------------------

The original external ROOT installation was not usable with Python 3.10 because its PyROOT bindings were built against a different Python version.

A separate ROOT build matching Python 3.10 was required.

7.3 Editable installation of RASER
------------------------------------

RASER source was installed in editable mode from:

    cd ~/raser3.19/raser-src
    pip install -e .

================================================================================
8. Verified commands
================================================================================

8.1 Environment checks
----------------------

    ~/raser3.19/scripts/run_linux_env.sh python ~/raser3.19/scripts/check_env.py
    ~/raser3.19/scripts/test_linux_pybind_host.sh

8.2 Import verification
-----------------------

    ~/raser3.19/scripts/run_linux_env.sh python - <<'PY'
    import ROOT, geant4_pybind, devsim, raser
    print("all imports OK")
    PY

8.3 Field workflow
------------------

    ~/raser3.19/scripts/run_linux_env.sh python -m raser field HPK-Si-LGAD -v

This has been verified to complete successfully and generate field-related output files.

8.4 Signal workflow
-------------------

Before running signal, the corresponding field outputs must exist.

Command used:

    ~/raser3.19/scripts/run_linux_env.sh python -m raser signal HPK-Si-LGAD -g4 proton_beam -vol 200

This has been verified to run successfully after preparing the expected field output filenames.

================================================================================
9. Known issues and notes
================================================================================

9.1 ROOT / Python version matching is mandatory
-----------------------------------------------

If PyROOT is built against the wrong Python version, import ROOT will fail even if root-config exists.

9.2 signal depends on pre-generated field outputs
-------------------------------------------------

The signal workflow requires field-related .pkl outputs to be available before signal calculation.

9.3 Bias filename mismatch
--------------------------

A current inconsistency exists between field output filenames and what signal expects.

Example:
- generated by field: Potential_200.0V.pkl
- expected by signal: Potential_200V.pkl

Temporary workaround:

    cd ~/raser3.19/raser-src/output/field/HPK-Si-LGAD

    ln -sf Potential_200.0V.pkl Potential_200V.pkl
    ln -sf TrappingRate_p_200.0V.pkl TrappingRate_p_200V.pkl
    ln -sf TrappingRate_n_200.0V.pkl TrappingRate_n_200V.pkl

A future code cleanup should unify voltage filename formatting.

9.4 Headless plotting
---------------------

For Linux server / batch environments, the workflow uses:

    MPLBACKEND=Agg

This avoids GUI backend problems with matplotlib.

9.5 Voltage argument parsing
----------------------------

The signal, resolution, and tct --voltage arguments were updated from string parsing to numeric parsing. A defensive float conversion was also added in current calculation code.

================================================================================
10. Files prepared for submission
================================================================================

The following items are suitable for version control / GitHub submission:

- bootstrap/raser-linux-py310-pybind.def
- requirements-linux-py310.txt
- requirements-linux-py310-lock.txt
- raser-src/pyproject.toml
- scripts/env_linux.sh
- scripts/run_linux_env.sh
- scripts/check_env.py
- scripts/test_linux_pybind_host.sh
- this README.txt

================================================================================
11. Scope of this README
================================================================================

This README documents the Linux x86 reference workflow that has already been validated locally.

It is not yet the final cross-platform release document for:
- Windows native
- macOS native
- Linux production packaging

Instead, it records the validated baseline that future platform-specific workflows should follow.
