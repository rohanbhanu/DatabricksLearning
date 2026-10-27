import os
import sys
import shutil
import subprocess
from pathlib import Path

from databricks.sdk import WorkspaceClient


def log(message):
    print(f"[LAUNCHER] {message}", flush=True)


def fail(message):
    print(
        f"[LAUNCHER] ERROR: {message}",
        file=sys.stderr,
        flush=True
    )
    sys.exit(1)


# =========================================================
# 1. Resolve Databricks App resource
# =========================================================

artifacts_dir = os.getenv("INSURANCE_ARTIFACTS")

if not artifacts_dir:
    fail(
        "INSURANCE_ARTIFACTS environment variable is missing. "
        "Check app.yaml resource configuration."
    )

log(f"Artifact volume: {artifacts_dir}")


# =========================================================
# 2. Define remote and local JAR locations
# =========================================================

remote_jar = (
    artifacts_dir.rstrip("/")
    + "/insurance-dashboard.jar"
)

local_dir = Path("/tmp/insurance-app")
local_dir.mkdir(
    parents=True,
    exist_ok=True
)

local_jar = local_dir / "insurance-dashboard.jar"

log(f"Remote JAR: {remote_jar}")
log(f"Local JAR: {local_jar}")


# =========================================================
# 3. Download JAR using Databricks Files API
# =========================================================

try:

    log("Connecting to Databricks Workspace API...")

    workspace = WorkspaceClient()

    log("Downloading insurance-dashboard.jar...")

    response = workspace.files.download(
        remote_jar
    )

    with open(local_jar, "wb") as output_file:
        shutil.copyfileobj(
            response.contents,
            output_file
        )

except Exception as exc:

    fail(
        "Unable to download the application JAR "
        f"from Unity Catalog Volume. Details: {exc}"
    )


# =========================================================
# 4. Verify local JAR
# =========================================================

if not local_jar.exists():

    fail(
        "JAR download completed but local file "
        "was not created."
    )


jar_size = local_jar.stat().st_size

log(
    f"JAR successfully downloaded. "
    f"Size: {jar_size:,} bytes"
)

if jar_size == 0:

    fail(
        "Downloaded JAR is empty."
    )


# =========================================================
# 5. Check existing Java runtime
# =========================================================

log("Checking for existing Java runtime...")

java_command = None

try:

    result = subprocess.run(
        ["java", "-version"],
        capture_output=True,
        text=True
    )

    version_output = (
        result.stderr.strip()
        or result.stdout.strip()
    )

    if result.returncode == 0:

        java_command = "java"

        log("Java runtime detected.")
        log(version_output)

except FileNotFoundError:

    log(
        "No Java executable exists in the "
        "Databricks App runtime."
    )


# =========================================================
# 6. Stop if Java is unavailable
# =========================================================

if java_command is None:

    fail(
        "Java runtime is not available. "
        "Azul Zulu bootstrap is required."
    )


# =========================================================
# 7. Start Spring Boot application
# =========================================================

log("Starting Insurance Portfolio Intelligence...")
log(f"Application JAR: {local_jar}")

os.execvp(
    java_command,
    [
        java_command,
        "-jar",
        str(local_jar)
    ]
)