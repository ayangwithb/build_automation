#!/usr/bin/env python3
"""build_bms_release.py - replicate VSCode 'Make BMS Release' task chain."""
import argparse
import subprocess
import sys
from datetime import datetime
from pathlib import Path

# workspace root = this script's directory
WORKSPACE = Path(__file__).resolve().parent


def run_step(name: str, cmd: list[str], cwd: Path | None = None) -> None:
    """Run a single build step; abort on non-zero exit code."""
    print(f"[STEP] {name}")
    print(f"       cmd: {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=cwd, shell=False)
    if result.returncode != 0:
        print(f"[FAIL] '{name}' exited with code {result.returncode}")
        sys.exit(result.returncode)


def main() -> None:
    parser = argparse.ArgumentParser(description="BMS release build automation")
    parser.add_argument("--ecu", default="BMS", help="PRJCFG_ECU value")
    parser.add_argument("--hwcode", required=True, help="PRJCFG_HWCODE value")
    args = parser.parse_args()

    ecu = args.ecu
    hwcode = args.hwcode

    build_dir = WORKSPACE / f"Build_{ecu}"
    make_exe = build_dir / "Util" / "make.exe"
    ecu_cfg_bat = build_dir / "Ecu_Configuration.bat"
    zip_bat = WORKSPACE / f"TC387_ASW_{ecu}" / "Tool" / "MakeRelease" / "MakeZipFile.bat"

    # common make args
    make_common = [
        "--silent",
        "--no-builtin-rules",
        f"PROJECT_PATH={WORKSPACE}",
        f"PRJCFG_ECU={ecu}",
        f"PRJCFG_HWCODE={hwcode}",
    ]

    print(f"=== BMS Release Build start: {datetime.now():%Y-%m-%d %H:%M:%S} ===")
    print(f"workspace: {WORKSPACE}")

    # [1/4] Clean - all
    run_step(
        "Clean - all",
        [str(make_exe), *make_common, "clean/all"],
        cwd=build_dir,
    )

    # [2/4] Pre Build - all
    run_step(
        "Pre Build - all",
        [str(ecu_cfg_bat), ecu, hwcode],
        cwd=build_dir,
    )

    # [3/4] Build - all(Release): RELEASE_OPTION=1
    run_step(
        "Build - all(Release)",
        [str(make_exe), *make_common, "RELEASE_OPTION=1", "all"],
        cwd=build_dir,
    )

    # [4/4] Make Release Package Zip
    run_step(
        "Make Release Package Zip",
        [str(zip_bat), hwcode],
    )

    print(f"=== Build completed: {datetime.now():%Y-%m-%d %H:%M:%S} ===")


if __name__ == "__main__":
    main()