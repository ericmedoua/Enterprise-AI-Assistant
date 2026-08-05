from pathlib import Path
import re


def sanitize_filename(
    filename: str,
) -> str:

    filename = Path(filename).name

    filename = re.sub(
        r"[^A-Za-z0-9._-]",
        "_",
        filename,
    )

    return filename
