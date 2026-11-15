"""Gate for dispatching C12 renderer only with nine verified ORIGINAL PNGs."""
from __future__ import annotations

import argparse
import json
from pathlib import Path


class C12DispatchError(ValueError):
    pass


def classify_preflight(report: dict) -> str:
    if (report.get("schema") != "videoforge/c12-technical-three-preflight/v1"
        or report.get("technical_preview_only") is not True
        or report.get("official_video_approved") is not False
        or report.get("human_visual_approved") is not False
        or report.get("image_generation_calls") != 0):
        raise C12DispatchError("C12_DISPATCH_INVALID_PREFLIGHT_POLICY")
    errors = report.get("errors")
    verified = report.get("verified")
    if not isinstance(errors, list) or not isinstance(verified, list):
        raise C12DispatchError("C12_DISPATCH_INVALID_ASSET_INVENTORY")
    if (report.get("status") == "READY_FOR_TECHNICAL_THREECANVAS_RENDER"
        and not errors and len(verified) == 9
        and len({x.get("id") for x in verified}) == 9
        and all(len(x.get("sha256", "")) == 64 for x in verified)):
        return "READY"
    if (report.get("status") == "ASSETS_PENDING"
        and errors and
        all(isinstance(x, str) and x.startswith("MISSING_OR_SYMLINK:")
            for x in errors)):
        return "WAIT_FOR_EXISTING_SOURCE_BYTES"
    raise C12DispatchError("C12_DISPATCH_ASSET_HASH_OR_POLICY_PROBLEM")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument("--github-output", type=Path, default=None)
    args = parser.parse_args()
    try:
        result = classify_preflight(
            json.loads(args.report.read_text(encoding="utf8")))
    except (C12DispatchError, OSError, ValueError) as exc:
        print("C12_DISPATCH_BLOCKED", str(exc))
        return 2
    if args.github_output:
        with args.github_output.open("a", encoding="utf8") as stream:
            stream.write("ready=" + ("true" if result == "READY" else "false") + "\n")
            stream.write("reason=" + result + "\n")
    print("C12_DISPATCH_" + result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
