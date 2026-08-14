from __future__ import annotations

import argparse
import shutil
import sys
import time
from pathlib import Path
from urllib.parse import quote

import httpx

DEFAULT_MODEL = "intfloat/multilingual-e5-small"
DEFAULT_FILES = [
    "1_Pooling/config.json",
    "config.json",
    "model.safetensors",
    "modules.json",
    "sentence_bert_config.json",
    "sentencepiece.bpe.model",
    "special_tokens_map.json",
    "tokenizer.json",
    "tokenizer_config.json",
]


def _cache_dir_for_model(model_name: str) -> Path:
    safe_name = "models--" + model_name.replace("/", "--")
    return Path.home() / ".cache" / "huggingface" / "hub" / safe_name


def _lock_dir_for_model(model_name: str) -> Path:
    safe_name = "models--" + model_name.replace("/", "--")
    return Path.home() / ".cache" / "huggingface" / "hub" / ".locks" / safe_name


def _delete_exact_path(path: Path) -> None:
    if not path.exists():
        return
    print(f"Removing {path}", flush=True)
    shutil.rmtree(path)


def _resolve_url(model: str, revision: str, filename: str) -> str:
    quoted_model = quote(model, safe="/")
    quoted_filename = quote(filename, safe="/")
    quoted_revision = quote(revision, safe="")
    return f"https://huggingface.co/{quoted_model}/resolve/{quoted_revision}/{quoted_filename}"


def _remote_size(client: httpx.Client, url: str) -> int | None:
    response = client.head(url)
    response.raise_for_status()
    size = response.headers.get("content-length")
    return int(size) if size and size.isdigit() else None


def _download_file(
    client: httpx.Client,
    url: str,
    target: Path,
    *,
    progress_mb: int,
) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    expected_size = _remote_size(client, url)

    if expected_size is not None and target.exists() and target.stat().st_size == expected_size:
        print(f"OK existing {target} ({expected_size} bytes)", flush=True)
        return

    part = target.with_name(target.name + ".part")
    downloaded = part.stat().st_size if part.exists() else 0
    headers = {}
    mode = "wb"
    if downloaded > 0:
        headers["Range"] = f"bytes={downloaded}-"
        mode = "ab"

    with client.stream("GET", url, headers=headers) as response:
        if response.status_code == 200 and downloaded > 0:
            downloaded = 0
            mode = "wb"
        response.raise_for_status()

        print(
            f"Downloading {target.name}: "
            f"start={downloaded} expected={expected_size if expected_size is not None else 'unknown'}",
            flush=True,
        )
        started = time.perf_counter()
        next_report_at = downloaded + progress_mb * 1024 * 1024

        with part.open(mode + "") as handle:
            for chunk in response.iter_bytes(chunk_size=1024 * 1024):
                if not chunk:
                    continue
                handle.write(chunk)
                downloaded += len(chunk)
                if downloaded >= next_report_at:
                    elapsed = max(time.perf_counter() - started, 0.001)
                    speed = downloaded / 1024 / 1024 / elapsed
                    if expected_size:
                        pct = downloaded / expected_size * 100
                        print(
                            f"  {target.name}: {downloaded / 1024 / 1024:.1f} MB "
                            f"/ {expected_size / 1024 / 1024:.1f} MB ({pct:.1f}%) "
                            f"@ {speed:.2f} MB/s",
                            flush=True,
                        )
                    else:
                        print(
                            f"  {target.name}: {downloaded / 1024 / 1024:.1f} MB "
                            f"@ {speed:.2f} MB/s",
                            flush=True,
                        )
                    next_report_at = downloaded + progress_mb * 1024 * 1024

    final_size = part.stat().st_size
    if expected_size is not None and final_size != expected_size:
        raise RuntimeError(f"Incomplete download for {target}: got {final_size}, expected {expected_size}")
    part.replace(target)
    elapsed = max(time.perf_counter() - started, 0.001)
    print(
        f"DONE {target} ({final_size / 1024 / 1024:.1f} MB, "
        f"{final_size / 1024 / 1024 / elapsed:.2f} MB/s)",
        flush=True,
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Directly download runtime files for a SentenceTransformers model.")
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--revision", default="main")
    parser.add_argument("--output", default="storage/models/intfloat-multilingual-e5-small")
    parser.add_argument(
        "--read-timeout-seconds",
        type=float,
        default=180,
        help="Idle read timeout for one connection. The script retries forever by default.",
    )
    parser.add_argument("--connect-timeout-seconds", type=float, default=60)
    parser.add_argument("--retry-delay-seconds", type=float, default=5)
    parser.add_argument(
        "--max-attempts",
        type=int,
        default=0,
        help="Attempts per file. 0 means retry forever while preserving the partial file.",
    )
    parser.add_argument("--progress-mb", type=int, default=25)
    parser.add_argument("--clear-output", action="store_true")
    parser.add_argument("--clear-hf-cache", action="store_true")
    args = parser.parse_args()

    output = Path(args.output).resolve()
    workspace = Path.cwd().resolve()
    if args.clear_output:
        if not output.is_relative_to(workspace):
            raise RuntimeError(f"Refusing to clear output outside workspace: {output}")
        _delete_exact_path(output)

    if args.clear_hf_cache:
        _delete_exact_path(_cache_dir_for_model(args.model))
        _delete_exact_path(_lock_dir_for_model(args.model))

    timeout = httpx.Timeout(
        connect=args.connect_timeout_seconds,
        read=args.read_timeout_seconds,
        write=args.read_timeout_seconds,
        pool=args.connect_timeout_seconds,
    )
    print(f"Model: {args.model}", flush=True)
    print(f"Revision: {args.revision}", flush=True)
    print(f"Output: {output}", flush=True)
    print(f"Read timeout seconds: {args.read_timeout_seconds}", flush=True)
    print(f"Max attempts per file: {'unlimited' if args.max_attempts == 0 else args.max_attempts}", flush=True)
    print(f"Runtime files: {len(DEFAULT_FILES)}", flush=True)

    with httpx.Client(follow_redirects=True, timeout=timeout) as client:
        for filename in DEFAULT_FILES:
            url = _resolve_url(args.model, args.revision, filename)
            attempts = 0
            while True:
                attempts += 1
                try:
                    _download_file(client, url, output / filename, progress_mb=args.progress_mb)
                    break
                except (httpx.TimeoutException, httpx.TransportError, RuntimeError) as exc:
                    if args.max_attempts > 0 and attempts >= args.max_attempts:
                        raise
                    print(
                        f"Retrying {filename} after {type(exc).__name__}: {exc}",
                        file=sys.stderr,
                        flush=True,
                    )
                    time.sleep(args.retry_delay_seconds)

    print("All runtime files downloaded.", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
