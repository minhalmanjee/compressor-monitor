import subprocess
import sys
import os

# Start ingestion and simulator as background processes
subprocess.Popen([sys.executable, "ingestion.py"])
subprocess.Popen([sys.executable, "simulator.py"])

# Start the streamlit dashboard
os.system(f"{sys.executable} -m streamlit run dashboard.py --server.port=8501 --server.address=0.0.0.0")