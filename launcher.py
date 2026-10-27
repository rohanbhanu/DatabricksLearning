import os
import sys
import subprocess
from pathlib import Path


def log(message):
    print(f"[LAUNCHER] {message}", flush=True)


def fail(message):
    print(f"[LAUNCHER] ERROR: {message}", file=sys.stderr, flush=True)
    sys.exit(1)


# ---------------------------------------------------------
# Read Databricks App resource configuration
# ---------------------------------------------------------

artifacts_dir = os.getenv("INSURANCE_ARTIFACTS")

if not artifacts_dir:
    fail(
        "INSURANCE_ARTIFACTS environment variable is missing. "
        "Check the volume resource binding in app.yaml."
    )

artifacts_path = Path(artifacts_dir)

log(f"Artifact volume: {artifacts_path}")


# ---------------------------------------------------------
# Verify artifact volume
# ---------------------------------------------------------

if not artifacts_path.exists():
    fail(
        f"Artifact volume does not exist or is not accessible: "
        f"{artifacts_path}"
    )


# ---------------------------------------------------------
# Locate insurance application JAR
# ---------------------------------------------------------

jar_path = artifacts_path / "insurance-dashboard.jar"

log(f"Looking for application JAR: {jar_path}")

if not jar_path.exists():
    fail(f"Application JAR not found: {jar_path}")

log("Insurance application JAR found.")


# ---------------------------------------------------------
# Runtime diagnostics
# ---------------------------------------------------------

log("Checking whether Java is already available...")

java_path = None

try:
    result = subprocess.run(
        ["java", "-version"],
        capture_output=True,
        text=True
    )

    if result.returncode == 0:

        java_path = "java"

        version_output = (
            result.stderr.strip()
            if result.stderr
            else result.stdout.strip()
        )

        log("Java runtime detected.")
        log(version_output)

except FileNotFoundError:
    log("No system Java runtime detected.")


# ---------------------------------------------------------
# We specifically require Azul Zulu for this POC
# ---------------------------------------------------------

if java_path is None:

    fail(
        "Java runtime is not available. "
        "Azul Zulu bootstrap is required."
    )


# ---------------------------------------------------------
# Start Spring Boot
# ---------------------------------------------------------

log("Starting Insurance Portfolio Intelligence...")
log(f"JAR: {jar_path}")

os.execvp(
    java_path,
    [
        java_path,
        "-jar",
        str(jar_path)
    ]
)