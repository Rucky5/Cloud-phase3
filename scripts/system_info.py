import json
import platform
import subprocess
from pathlib import Path


def run_powershell(command: str) -> str:
    completed = subprocess.run(
        ["powershell", "-NoProfile", "-Command", command],
        capture_output=True,
        text=True,
        check=False,
    )
    output = (completed.stdout or completed.stderr).strip()
    if "Access denied" in output:
        return ""
    return output


def run_command(command: list[str]) -> str:
    completed = subprocess.run(
        command,
        capture_output=True,
        text=True,
        check=False,
    )
    output = (completed.stdout or completed.stderr).strip()
    if (
        "Access is denied" in output
        or "Access denied" in output
        or "Alias not found" in output
    ):
        return ""
    return output


def first_non_empty(*values: str) -> str:
    for value in values:
        cleaned = value.strip()
        if cleaned:
            return cleaned
    return "Not detected"


def collect_system_info() -> dict:
    cpu_name = first_non_empty(
        run_powershell("(Get-CimInstance Win32_Processor).Name"),
        run_command(["wmic", "cpu", "get", "name"]),
        platform.processor(),
    )
    total_ram_bytes = first_non_empty(
        run_powershell("(Get-CimInstance Win32_ComputerSystem).TotalPhysicalMemory"),
        run_command(["wmic", "ComputerSystem", "get", "TotalPhysicalMemory"]),
    )
    gpu_name = first_non_empty(
        run_powershell("(Get-CimInstance Win32_VideoController | Select-Object -First 1).Name"),
        run_command(["wmic", "path", "win32_VideoController", "get", "name"]),
    )

    ram_gb = "unknown"
    digits_only = "".join(ch for ch in total_ram_bytes if ch.isdigit())
    if digits_only:
        ram_gb = round(int(digits_only) / (1024 ** 3), 2)

    return {
        "os": platform.platform(),
        "machine": platform.machine(),
        "processor": cpu_name,
        "ram_gb": ram_gb,
        "gpu": gpu_name,
    }


def main() -> None:
    output_path = Path("benchmark_results/system_info.json")
    output_path.parent.mkdir(parents=True, exist_ok=True)

    info = collect_system_info()
    output_path.write_text(json.dumps(info, indent=2), encoding="utf-8")

    print(json.dumps(info, indent=2))
    print(f"Saved system info to {output_path}")


if __name__ == "__main__":
    main()
