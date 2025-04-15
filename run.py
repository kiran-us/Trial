import subprocess

# Start FastAPI with Uvicorn
uvicorn_cmd = ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "3002"]

# Start Streamlit app inside frontend folder
streamlit_cmd = [
    "streamlit", "run", "frontend/app.py",
    "--server.port", "8501",
    "--server.runOnSave","true"
]

# Run both commands concurrently
processes = [
    subprocess.Popen(uvicorn_cmd),
    subprocess.Popen(streamlit_cmd)
]

# Wait for both processes to complete
for process in processes:
  process.wait()