# Average Merge Tree(AMT)

This is visualization tools for calculating 1-center tree. The implementation is described in "A Structural Average of Labeled Merge Trees for Uncertainty Visualization".

<center><img src="Interface.png" width="512"></center>

# How to use

Tested with both Python 2.7, MacOS 10.10 and Ubuntu 16.04.

### What to expect

You can:
- draw trees as ensemble members in "Drawing Panel".
- select, reconfigure and delete trees in "Ensemble Panel".
- set related parameters and view the relation between 1-center and ensemble members in "Control Panel".
- view an animated sequence between an input tree and the 1-center via geodesic or linear strategy in "Animation".
- view vertex and edge consistency for each ensemble member, variational and statistical consistency for 1-center tree in "Consistency Visualization".

<center><img src="2.png" width="512"></center>

### Run
    $ virtualenv AMT-demo-env
    $ source AMT-demo-env/bin/activate
    (AMT-demo-env) $ pip install -r requirements.txt
    (AMT-demo-env) $ python app.py
    * Running on http://127.0.0.1:5000/ (Press CTRL+C to quit)
    * Restarting with stat
    * Debugger is active!
    * Debugger pin code: 174-511-253


### Notes

- The documents and comments are still in progress.
- Application to scalar field ensembles(refer to section 7 of above paper) will be uploaded in the following weeks.

<center><img src="3.png" width="512"></center>
