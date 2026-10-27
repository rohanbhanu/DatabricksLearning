import os
import sys
import shutil
import tarfile
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
# CONFIGURATION
# =========================================================

artifacts_dir = os.getenv("INSURANCE_ARTIFACTS")

if not artifacts_dir:
    fail(
        "INSURANCE_ARTIFACTS environment variable "
        "is not configured."
    )

log(f"Artifact volume: {artifacts_dir}")


# =========================================================
# ARTIFACT PATHS
# =========================================================

remote_jar = (
    artifacts_dir.rstrip("/")
    + "/insurance-dashboard.jar"
)

remote_zulu = (
    artifacts_dir.rstrip("/")
    + "/zulu21-linux-x64.tar.gz"
)

local_root = Path("/tmp/insurance-app")
local_root.mkdir(
    parents=True,
    exist_ok=True
)

local_jar = (
    local_root
    / "insurance-dashboard.jar"
)

local_zulu_archive = (
    local_root
    / "zulu21-linux-x64.tar.gz"
)

zulu_extract_dir = (
    local_root
    / "zulu"
)


# =========================================================
# CONNECT TO DATABRICKS
# =========================================================

try:

    log("Connecting to Databricks Workspace API...")

    workspace = WorkspaceClient()

except Exception as exc:

    fail(
        f"Unable to initialize Databricks client: {exc}"
    )


# =========================================================
# HELPER: DOWNLOAD FILE
# =========================================================

def download_file(remote_path, local_path):

    log(
        f"Downloading {remote_path}"
    )

    try:

        response = workspace.files.download(
            remote_path
        )

        with open(local_path, "wb") as output_file:

            shutil.copyfileobj(
                response.contents,
                output_file
            )

    except Exception as exc:

        fail(
            f"Unable to download {remote_path}: {exc}"
        )

    if not local_path.exists():

        fail(
            f"Downloaded file was not created: "
            f"{local_path}"
        )

    size = local_path.stat().st_size

    if size == 0:

        fail(
            f"Downloaded file is empty: "
            f"{local_path}"
        )

    log(
        f"Downloaded successfully: "
        f"{local_path} ({size:,} bytes)"
    )


# =========================================================
# DOWNLOAD SPRING BOOT JAR
# =========================================================

download_file(
    remote_jar,
    local_jar
)


# =========================================================
# DOWNLOAD AZUL ZULU
# =========================================================

download_file(
    remote_zulu,
    local_zulu_archive
)


# =========================================================
# EXTRACT AZUL ZULU
# =========================================================

log("Extracting Azul Zulu runtime...")

try:

    if zulu_extract_dir.exists():

        shutil.rmtree(
            zulu_extract_dir
        )

    zulu_extract_dir.mkdir(
        parents=True,
        exist_ok=True
    )

    with tarfile.open(
        local_zulu_archive,
        "r:gz"
    ) as archive:

        archive.extractall(
            zulu_extract_dir
        )

except Exception as exc:

    fail(
        f"Unable to extract Azul Zulu: {exc}"
    )


# =========================================================
# FIND JAVA EXECUTABLE
# =========================================================

log("Searching for Azul Zulu java executable...")

java_candidates = list(
    zulu_extract_dir.glob(
        "**/bin/java"
    )
)

if not java_candidates:

    fail(
        "Could not find bin/java inside "
        "the extracted Azul Zulu package."
    )

java_path = java_candidates[0]

log(
    f"Java executable found: {java_path}"
)


# =========================================================
# ENSURE JAVA IS EXECUTABLE
# =========================================================

try:

    java_path.chmod(0o755)

except Exception as exc:

    fail(
        f"Unable to mark Java executable: {exc}"
    )


# =========================================================
# VERIFY JVM
# =========================================================

log("Verifying Java runtime...")

try:

    result = subprocess.run(
        [
            str(java_path),
            "-version"
        ],
        capture_output=True,
        text=True
    )

except Exception as exc:

    fail(
        f"Unable to execute Java: {exc}"
    )


version_output = (
    result.stderr.strip()
    or result.stdout.strip()
)

log("Java runtime information:")
log(version_output)


if result.returncode != 0:

    fail(
        "Azul Zulu java -version failed."
    )


# =========================================================
# SET JAVA_HOME
# =========================================================

java_home = java_path.parent.parent

os.environ["JAVA_HOME"] = str(
    java_home
)

os.environ["PATH"] = (
    str(java_path.parent)
    + os.pathsep
    + os.environ.get(
        "PATH",
        ""
    )
)

log(
    f"JAVA_HOME={java_home}"
)


# =========================================================
# START SPRING BOOT APPLICATION
# =========================================================

log(
    "Starting Insurance Portfolio Intelligence..."
)

log(
    f"Application JAR: {local_jar}"
)

os.execv(
    str(java_path),
    [
        str(java_path),
        "-jar",
        str(local_jar)
    ]
)