import os
import sys
import tarfile
import glob
import shutil
import subprocess
from databricks.sdk import WorkspaceClient


# ---------------------------------------------------------
# Configuration
# ---------------------------------------------------------

ARTIFACT_VOLUME = "/Volumes/royalinsurance/edw/app_artifacts"

JAR_NAME = "insurance-dashboard.jar"

ZULU_ARCHIVE_NAME = "zulu21.54.107-ca-jdk21.0.13-linux_x64.tar.gz"

TEMP_DIR = "/tmp/insurance-app"
ZULU_DIR = os.path.join(TEMP_DIR, "zulu")

LOCAL_JAR = os.path.join(TEMP_DIR, JAR_NAME)
LOCAL_ZULU_ARCHIVE = os.path.join(TEMP_DIR, ZULU_ARCHIVE_NAME)

REMOTE_JAR = f"{ARTIFACT_VOLUME}/{JAR_NAME}"
REMOTE_ZULU_ARCHIVE = f"{ARTIFACT_VOLUME}/{ZULU_ARCHIVE_NAME}"


# ---------------------------------------------------------
# Logging helper
# ---------------------------------------------------------

def log(message):
    print(f"[LAUNCHER] {message}", flush=True)


# ---------------------------------------------------------
# Download file from Unity Catalog Volume
# ---------------------------------------------------------

def download_volume_file(workspace_client, source_path, destination_path):

    log(f"Downloading {source_path}")

    response = workspace_client.files.download(source_path)

    with open(destination_path, "wb") as output_file:
        shutil.copyfileobj(response.contents, output_file)

    size = os.path.getsize(destination_path)

    log(
        f"Downloaded successfully: "
        f"{destination_path} ({size:,} bytes)"
    )


# ---------------------------------------------------------
# Main launcher
# ---------------------------------------------------------

def main():

    log("Starting Insurance Dashboard launcher...")

    # -----------------------------------------------------
    # Get Databricks application port
    # -----------------------------------------------------

    port = os.environ.get("DATABRICKS_APP_PORT")

    if not port:
        log("ERROR: DATABRICKS_APP_PORT is not set")
        sys.exit(1)

    log(f"Databricks App Port: {port}")

    # -----------------------------------------------------
    # Prepare temporary directory
    # -----------------------------------------------------

    os.makedirs(TEMP_DIR, exist_ok=True)

    if os.path.exists(ZULU_DIR):
        shutil.rmtree(ZULU_DIR)

    os.makedirs(ZULU_DIR, exist_ok=True)

    # -----------------------------------------------------
    # Connect to Databricks
    # -----------------------------------------------------

    log("Connecting to Databricks Workspace API...")

    try:
        workspace_client = WorkspaceClient()
    except Exception as e:
        log(f"ERROR creating WorkspaceClient: {e}")
        sys.exit(1)

    log(f"Artifact volume: {ARTIFACT_VOLUME}")

    # -----------------------------------------------------
    # Download application JAR
    # -----------------------------------------------------

    try:
        download_volume_file(
            workspace_client,
            REMOTE_JAR,
            LOCAL_JAR
        )
    except Exception as e:
        log(f"ERROR downloading application JAR: {e}")
        sys.exit(1)

    # -----------------------------------------------------
    # Download Azul Zulu JDK
    # -----------------------------------------------------

    try:
        download_volume_file(
            workspace_client,
            REMOTE_ZULU_ARCHIVE,
            LOCAL_ZULU_ARCHIVE
        )
    except Exception as e:
        log(f"ERROR downloading Azul Zulu archive: {e}")
        sys.exit(1)

    # -----------------------------------------------------
    # Extract Azul Zulu
    # -----------------------------------------------------

    log("Extracting Azul Zulu runtime...")

    try:
        with tarfile.open(LOCAL_ZULU_ARCHIVE, "r:gz") as tar:
            tar.extractall(ZULU_DIR)
    except Exception as e:
        log(f"ERROR extracting Azul Zulu: {e}")
        sys.exit(1)

    # -----------------------------------------------------
    # Find Java executable
    # -----------------------------------------------------

    log("Searching for Azul Zulu java executable...")

    java_candidates = glob.glob(
        os.path.join(
            ZULU_DIR,
            "**",
            "bin",
            "java"
        ),
        recursive=True
    )

    if not java_candidates:
        log("ERROR: Could not find Java executable after extraction.")
        sys.exit(1)

    java_executable = java_candidates[0]

    log(f"Java executable found: {java_executable}")

    # -----------------------------------------------------
    # JAVA_HOME
    # -----------------------------------------------------

    java_home = os.path.dirname(
        os.path.dirname(java_executable)
    )

    os.environ["JAVA_HOME"] = java_home

    log(f"JAVA_HOME={java_home}")

    # -----------------------------------------------------
    # Verify Java runtime
    # -----------------------------------------------------

    log("Verifying Java runtime...")

    try:
        java_version = subprocess.run(
            [java_executable, "-version"],
            capture_output=True,
            text=True,
            check=True
        )

        log("Java runtime information:")

        if java_version.stdout:
            print(java_version.stdout, flush=True)

        if java_version.stderr:
            print(java_version.stderr, flush=True)

    except Exception as e:
        log(f"ERROR verifying Java runtime: {e}")
        sys.exit(1)

    # -----------------------------------------------------
    # Verify application JAR
    # -----------------------------------------------------

    if not os.path.exists(LOCAL_JAR):
        log(f"ERROR: Application JAR not found: {LOCAL_JAR}")
        sys.exit(1)

    log("Starting Insurance Portfolio Intelligence...")
    log(f"Application JAR: {LOCAL_JAR}")
    log(f"Listening on: 0.0.0.0:{port}")

    # -----------------------------------------------------
    # Start Spring Boot
    # -----------------------------------------------------

    command = [
        java_executable,
        "-jar",
        LOCAL_JAR,
        f"--server.port={port}",
        "--server.address=0.0.0.0"
    ]

    log("Starting Spring Boot application...")

    try:

        process = subprocess.Popen(
            command,
            stdout=sys.stdout,
            stderr=sys.stderr,
            env=os.environ
        )

        exit_code = process.wait()

        log(
            f"Spring Boot process exited "
            f"with code {exit_code}"
        )

        sys.exit(exit_code)

    except Exception as e:

        log(f"ERROR starting Spring Boot application: {e}")
        sys.exit(1)


# ---------------------------------------------------------
# Entry point
# ---------------------------------------------------------

if __name__ == "__main__":
    main()