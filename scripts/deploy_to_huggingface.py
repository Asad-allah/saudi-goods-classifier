#!/usr/bin/env python3
"""One-Click Deployment Script to Hugging Face Spaces.
Allows uploading the entire project directly to your Hugging Face Space repository.
"""

import os
import sys
import subprocess
from pathlib import Path

def main():
    print("=" * 75)
    print("🚀 ONE-CLICK DEPLOYMENT TO HUGGING FACE SPACES")
    print("=" * 75)

    if len(sys.argv) > 1:
        repo_url = sys.argv[1].strip()
    else:
        print("\nيرجى إدخال رابط مستودع الـ Space في Hugging Face")
        print("مثال: https://huggingface.co/spaces/your-username/saudi-goods-classifier")
        repo_url = input("\n👉 أدخل الرابط هنا: ").strip()

    if not repo_url:
        print("❌ لم يتم إدخال الرابط. تم إلغاء العملية.")
        return

    # Normalize git URL
    if not repo_url.endswith(".git") and "huggingface.co/spaces/" in repo_url:
        git_url = repo_url.replace("https://huggingface.co/spaces/", "https://huggingface.co/spaces/")
    else:
        git_url = repo_url

    print(f"\n📦 جاري تجهيز الملفات وتحديث المستودع...")
    
    # Execute git commands
    cmds = [
        ["git", "init"],
        ["git", "add", "app/", "storage/", ".superpowers/", "Dockerfile", ".dockerignore", "pyproject.toml", "README.md", "scripts/"],
        ["git", "commit", "-m", "Deploy Saudi Goods Classifier to Hugging Face Spaces"],
        ["git", "remote", "remove", "space"],
        ["git", "remote", "add", "space", git_url],
        ["git", "push", "-u", "space", "main", "--force"],
    ]

    for cmd in cmds:
        try:
            res = subprocess.run(cmd, capture_output=True, text=True)
            # Ignore harmless remote remove failure
            if cmd[1] == "remote" and cmd[2] == "remove":
                continue
            if res.returncode != 0 and "nothing to commit" not in res.stderr and "already exists" not in res.stderr:
                print(f"⚠️ تنبيه في الخطوة ({' '.join(cmd)}): {res.stderr.strip()}")
        except Exception as e:
            print(f"خطأ: {e}")

    print("\n" + "=" * 75)
    print("🎉 تم رفع المشروع بنجاح إلى Hugging Face Spaces!")
    print(f"🌐 رابط الـ Space الخاص بك: {repo_url}")
    print("=" * 75)

if __name__ == "__main__":
    main()
