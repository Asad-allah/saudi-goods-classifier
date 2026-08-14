#!/usr/bin/env python3
"""Deploy Saudi Goods Classifier to Render.com via Render REST API.
Connects GitHub repository Asad-allah/saudi-goods-classifier and triggers cloud build.
"""

import sys
import json
import urllib.request
import urllib.error

RENDER_API_BASE = "https://api.render.com/v1"

def main():
    print("=" * 75)
    print("🚀 DEPLOY SAUDI GOODS CLASSIFIER TO RENDER.COM")
    print("=" * 75)

    if len(sys.argv) > 1:
        api_key = sys.argv[1].strip()
    else:
        print("\nيرجى إدخال Render API Key الخاص بك")
        print("يمكنك الحصول عليه مجاناً بنقرة زر من:")
        print("👉 https://dashboard.render.com/u/settings#api-keys")
        api_key = input("\n🔑 أدخل Render API Key (يبدأ بـ rnd_...): ").strip()

    if not api_key:
        print("❌ لم يتم إدخال المفتاح. تم إلغاء العملية.")
        return

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }

    # 1. Get Owner ID
    print("\n⏳ جاري التحقق من الحساب على Render...")
    try:
        req = urllib.request.Request(f"{RENDER_API_BASE}/owners", headers=headers)
        with urllib.request.urlopen(req) as resp:
            owners = json.loads(resp.read().decode("utf-8"))
            if not owners:
                print("❌ لم يتم العثور على حساب في Render.")
                return
            owner_id = owners[0]["owner"]["id"]
            owner_name = owners[0]["owner"].get("name", "User")
            print(f"✅ تم تسجيل الدخول بنجاح كـ: {owner_name} (ID: {owner_id})")
    except urllib.error.HTTPError as e:
        print(f"❌ خطأ في المصادقة: {e.code} - {e.read().decode('utf-8')}")
        return
    except Exception as e:
        print(f"❌ خطأ غير متوقع: {e}")
        return

    # 2. Create Web Service
    service_payload = {
        "type": "web_service",
        "name": "saudi-goods-classifier",
        "ownerId": owner_id,
        "repo": "https://github.com/Asad-allah/saudi-goods-classifier",
        "branch": "main",
        "autoDeploy": "yes",
        "serviceDetails": {
            "env": "python",
            "plan": "free",
            "region": "oregon",
            "envSpecificDetails": {
                "buildCommand": "pip install --upgrade pip && pip install -r requirements.txt",
                "startCommand": "uvicorn app.main:app --host 0.0.0.0 --port $PORT"
            },
            "envVars": [
                {"key": "PYTHON_VERSION", "value": "3.12.0"}
            ]
        }
    }

    print("\n🚀 جاري إنشاء وتفعيل السيرفر السحابي الدائم على Render...")
    try:
        req = urllib.request.Request(
            f"{RENDER_API_BASE}/services",
            data=json.dumps(service_payload).encode("utf-8"),
            headers=headers,
            method="POST",
        )
        with urllib.request.urlopen(req) as resp:
            service_data = json.loads(resp.read().decode("utf-8"))
            service_id = service_data.get("id")
            service_name = service_data.get("name")
            service_url = service_data.get("serviceDetails", {}).get("url") or f"https://{service_name}.onrender.com"

            print("\n" + "=" * 75)
            print("🎉 تم إنشاء السيرفر وبدء البناء السحابي بنجاح على Render!")
            print(f"📌 اسم الخدمة: {service_name}")
            print(f"🌐 الرابط الدائم للسيرفر: {service_url}")
            print(f"📊 لوحة التحكم: https://dashboard.render.com/web/{service_id}")
            print("=" * 75)
            print("\n💡 سيكتمل البناء خلال دقيقتين ويكون التطبيق متاحاً 24/7 دون الحاجة لتشغيل لابتوبك!")
    except urllib.error.HTTPError as e:
        err_body = e.read().decode("utf-8")
        if "already in use" in err_body:
            print("ℹ️ الخدمة موجودة بالفعل على Render!")
            print("🌐 رابط الخدمة: https://saudi-goods-classifier.onrender.com")
        else:
            print(f"❌ خطأ أثناء إنشاء الخدمة: {e.code} - {err_body}")
    except Exception as e:
        print(f"❌ خطأ: {e}")

if __name__ == "__main__":
    main()
