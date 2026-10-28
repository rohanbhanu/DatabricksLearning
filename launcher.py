import os
import subprocess
import sys

jar_path = "/Volumes/royalinsurance/edw/app_artifacts/insurance-dashboard.jar"

port = os.environ.get("DATABRICKS_APP_PORT")

if not port:
    print("[LAUNCHER] ERROR: DATABRICKS_APP_PORT is not set")
    sys.exit(1)

print(f"[LAUNCHER] Starting JAR: {jar_path}")
print(f"[LAUNCHER] Databricks App Port: {port}")

command = [
    "java",
    "-jar",
    jar_path,
    f"--server.port={port}",
    "--server.address=0.0.0.0"
]

print("[LAUNCHER] Starting Spring Boot application...")

process = subprocess.Popen(command)
sys.exit(process.wait())