import contextlib
from pathlib import Path
import shutil

from . import log

# Artifacts that will be cleaned
ARTIFACTS_TO_CLEAN = [
    "output",
    "htmlcov",
    ".pytest_cache",
    ".ruff_cache",
    ".coverage",
    "__pycache__",
]


def format_size(size_bytes):
    """Convert bytes to human-readable format (B, KB, MB, GB)."""
    for unit in ["B", "KB", "MB", "GB"]:
        if size_bytes < 1024:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.1f} TB"


def get_path_size(path):
    """Calculate total size of a file or directory in bytes."""
    path_obj = Path(path)
    if not path_obj.exists():
        return 0

    if path_obj.is_file():
        return path_obj.stat().st_size

    total_size = 0
    for item in path_obj.rglob("*"):
        if item.is_file():
            with contextlib.suppress(OSError, PermissionError):
                total_size += item.stat().st_size
    return total_size


def get_artifacts_to_remove(delete_output=True):
    """Get list of existing artifacts that can be removed with their sizes."""
    existing_artifacts = []
    for artifact in ARTIFACTS_TO_CLEAN:
        if artifact == "output" and not delete_output:
            continue
        artifact_path = Path(artifact)
        if artifact_path.exists():
            size = get_path_size(artifact_path)
            existing_artifacts.append((artifact_path, size))
    return existing_artifacts


def display_cleanup_preview(artifacts):
    """Display a preview of artifacts that will be removed with total size."""
    if not artifacts:
        log.dim("No artifacts to remove.")
        return False

    log.header("Artifacts to Remove")
    total_size = 0
    for artifact_path, size in artifacts:
        artifact_type = "directory" if artifact_path.is_dir() else "file"
        size_str = format_size(size)
        log.dim(f"  • {artifact_path} ({artifact_type}, {size_str})")
        total_size += size

    total_str = format_size(total_size)

    print()
    log.info(f"Total space to free: {total_str}")
    print()
    return True


def confirm_cleanup():
    """Prompt user for confirmation before cleaning."""
    log.header("Confirm Cleanup")
    log.warn(
        "This action is IRREVERSIBLE and will PERMANENTLY delete the listed artifacts."
    )

    print()
    response = input("  Do you want to proceed with cleanup? [y/N]: ").strip().lower()

    return response == "y"


def confirm_delete_output():
    """Prompt user to decide whether the output folder should be removed."""
    log.header("Decide whether to remove the 'output' folder:")
    response = input("  Delete the output folder too? [y/N]: ").strip().lower()
    return response == "y"


def clean_artifacts(verbose=False):
    """Remove generated artifacts including output, coverage, and cache directories."""
    delete_output = True

    if Path("output").exists():
        delete_output = confirm_delete_output()

    artifacts = get_artifacts_to_remove(delete_output=delete_output)

    # Display preview of what will be removed
    if not display_cleanup_preview(artifacts):
        log.error("Cleanup cancelled - no artifacts found.")
        return 0

    # Request confirmation
    if not confirm_cleanup():
        print()
        log.warn("Cleanup cancelled by user.")
        print()
        return 0

    # Perform cleanup
    if verbose:
        log.header("Cleaning Generated Artifacts")

    removed_count = 0
    total_freed = 0
    for artifact_path, size in artifacts:
        try:
            if artifact_path.is_dir():
                shutil.rmtree(artifact_path)
            else:
                artifact_path.unlink()
            if verbose:
                log.ok(f"Removed {artifact_path}")
            removed_count += 1
            total_freed += size
        except Exception as exc:
            log.warn(f"Failed to remove {artifact_path}: {exc}")

    if removed_count > 0:
        freed_str = format_size(total_freed)

        print()
        log.ok(
            f"Cleanup completed: {removed_count} artifact(s) removed ({freed_str} freed)."
        )
    else:
        log.dim("No artifacts were removed.")
    print()

    return 0
