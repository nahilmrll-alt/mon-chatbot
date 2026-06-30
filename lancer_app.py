import subprocess
import sys
import os

chemin_app = os.path.join(os.path.dirname(os.path.abspath(sys.argv[0])), "app.py")
subprocess.run(["streamlit", "run", chemin_app])