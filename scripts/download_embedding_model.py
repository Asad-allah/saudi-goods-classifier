from __future__ import annotations

import argparse
import os
import shutil
import time
from pathlib import Path

# Xet can hang on some Windows/network setups while fetching large model blobs.
# Default to the regular HTTP downloader for a more predictable local MVP setup.
os.environ.setdefault("HF_HUB_DISABLE_XET", "1")
os.environ.setdefault("HF_HUB_DOWNLOAD_TIMEOUT", "86400")

from huggingface_hub import snapshot_download


def _cache_dir_for_model(model_name: str) -> Path:
    safe_name = "models--" + model_name.replace("/", "--")
    return Path.home() / ".cache" / "huggingface" / "hub" / safe_name


def _lock_dir_for_model(model_name: str) -> Path:
    safe_name = "models--" + model_name.replace("/", "--")
    return Path.home() / ".cache" / "huggingface" / "hub" / ".locks" / safe_name


def main() -> None:
    parser = argparse.ArgumentParser(description="Download a SentenceTransformers model.")
    parser.add_argument("--model", default="intfloat/multilingual-e5-small")
    parser.add_argument(
        "--clear-cache",
        action="store_true",
        help="Delete only this model cache before downloading.",
    )
    parser.add_argument(
        "--all-files",
        action="store_true",
        help="Download the full repository instead of only runtime files.",
    )
    parser.add_argument("--max-workers", type=int, default=1)
    args = parser.parse_args()

    model_cache = _cache_dir_for_model(args.model)
    lock_cache = _lock_dir_for_model(args.model)

    if args.clear_cache:
        for path in (model_cache, lock_cache):
            if path.exists():
                print(f"Removing {path}", flush=True)
                shutil.rmtree(path)

    print(f"Downloading {args.model}", flush=True)
    started = time.perf_counter()
    allow_patterns = None
    if not args.all_files:
        allow_patterns = [
            "*.json",
            "*.txt",
            "model.safetensors",
            "1_Pooling/*",
        ]
    print(
        "Download mode: "
        + ("all repository files" if args.all_files else f"runtime files only: {allow_patterns}"),
        flush=True,
    )
    print(f"HF_HUB_DISABLE_XET={os.environ.get('HF_HUB_DISABLE_XET')}", flush=True)
    print(f"HF_HUB_DOWNLOAD_TIMEOUT={os.environ.get('HF_HUB_DOWNLOAD_TIMEOUT')}", flush=True)
    snapshot = snapshot_download(
        repo_id=args.model,
        local_files_only=False,
        allow_patterns=allow_patterns,
        max_workers=args.max_workers,
    )
    elapsed = time.perf_counter() - started
    print(f"Downloaded snapshot: {snapshot}", flush=True)
    print(f"Elapsed seconds: {elapsed:.1f}", flush=True)


if __name__ == "__main__":
    main()
