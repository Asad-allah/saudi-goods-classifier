# One-Click Deployment Script for Windows PowerShell
$ErrorActionPreference = "Continue"

Write-Host "===========================================================================" -ForegroundColor Cyan
Write-Host "🚀 ONE-CLICK DEPLOYMENT TO HUGGING FACE SPACES" -ForegroundColor Green
Write-Host "===========================================================================" -ForegroundColor Cyan

$repoUrl = Read-Host "👉 أدخل رابط مستودع الـ Space في Hugging Face (مثال: https://huggingface.co/spaces/username/project-name)"

if ([string]::IsNullOrWhiteSpace($repoUrl)) {
    Write-Host "❌ لم يتم إدخال رابط. تم إلغاء العملية." -ForegroundColor Red
    exit
}

Write-Host "`n📦 جاري تجهيز الملفات والرفع..." -ForegroundColor Yellow

git init
git add app/ storage/ .superpowers/ Dockerfile .dockerignore pyproject.toml README.md scripts/
git commit -m "Deploy Saudi Goods Classifier to Hugging Face Spaces"
git remote remove space 2>$null
git remote add space $repoUrl
git push -u space main --force

Write-Host "`n===========================================================================" -ForegroundColor Cyan
Write-Host "🎉 تم رفع المشروع بنجاح إلى Hugging Face Spaces!" -ForegroundColor Green
Write-Host "🌐 افتح رابط الـ Space الآن لمشاهدة البناء والتشغيل:" -ForegroundColor White
Write-Host "$repoUrl" -ForegroundColor Yellow
Write-Host "===========================================================================" -ForegroundColor Cyan
