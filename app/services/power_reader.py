import csv
import os
from pathlib import Path


def _pick_power_column(headers: list[str]) -> str | None:
    preferred = [
        "package power",
        "processor power",
        "cpu power",
    ]
    lowered = [h.lower() for h in headers]

    for key in preferred:
        for header, low in zip(headers, lowered):
            if key in low and "watt" in low:
                return header

    for header, low in zip(headers, lowered):
        if "power" in low and "watt" in low:
            return header

    return None


def _tail_lines(path: Path, max_lines: int = 200) -> list[str]:
    if max_lines <= 0:
        return []

    with path.open("rb") as handle:
        handle.seek(0, os.SEEK_END)
        end = handle.tell()
        buffer = bytearray()
        lines: list[bytes] = []
        chunk_size = 4096

        while end > 0 and len(lines) <= max_lines:
            read_size = min(chunk_size, end)
            end -= read_size
            handle.seek(end)
            buffer = handle.read(read_size) + buffer
            lines = buffer.splitlines()

        return [line.decode("utf-8", errors="ignore") for line in lines[-max_lines:]]


def read_power_stats() -> dict | None:
    log_path = os.environ.get("POWER_GADGET_LOG_PATH")
    if not log_path:
        return None

    path = Path(log_path)
    if not path.exists():
        return None

    try:
        lines = _tail_lines(path, max_lines=200)
    except Exception:
        return None

    if not lines:
        return None

    reader = csv.DictReader(lines)
    rows = list(reader)

    if not rows or not reader.fieldnames:
        return None

    power_column = _pick_power_column(reader.fieldnames)
    if not power_column:
        return None

    values: list[float] = []
    for row in rows[-60:]:
        raw = row.get(power_column, "")
        try:
            values.append(float(raw))
        except ValueError:
            continue

    if not values:
        return None

    avg_power = round(sum(values) / len(values), 2)
    peak_power = round(max(values), 2)

    return {
        "power_avg_w": avg_power,
        "power_peak_w": peak_power,
        "power_source": f"Intel Power Gadget ({path.name})",
    }
