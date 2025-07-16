#!/bin/bash
# GitHub 倉庫快速設定腳本

set -e

echo "🚀 MCP 監控系統 GitHub 設定腳本"
echo "=================================="

# 檢查是否在正確目錄
if [ ! -f "README.md" ] || [ ! -d "mcp_servers" ]; then
    echo "❌ 錯誤: 請在 mcp_use 專案根目錄執行此腳本"
    exit 1
fi

# 檢查 Git 是否已初始化
if [ ! -d ".git" ]; then
    echo "📦 初始化 Git 倉庫..."
    git init
fi

# 設定 Git 配置
echo "⚙️ 設定 Git 配置..."
read -p "請輸入你的 GitHub 用戶名: " github_username
read -p "請輸入你的 email: " github_email

git config user.name "$github_username"
git config user.email "$github_email"

# 檢查是否已有遠程倉庫
if git remote | grep -q "origin"; then
    echo "✅ 遠程倉庫已設定"
else
    echo "🔗 設定遠程倉庫..."
    read -p "請輸入 GitHub 倉庫 URL (例如: https://github.com/username/mcp-monitoring-system.git): " repo_url
    git remote add origin "$repo_url"
fi

# 檢查是否有未提交的變更
if ! git diff-index --quiet HEAD -- 2>/dev/null; then
    echo "📝 發現未提交的變更，正在提交..."
    git add .
    git commit -m "chore: 使用自動設定腳本更新專案"
fi

# 推送到 GitHub
echo "⬆️ 推送到 GitHub..."
git branch -M main
git push -u origin main

echo ""
echo "✅ GitHub 設定完成！"
echo "🌟 下一步："
echo "   1. 訪問你的 GitHub 倉庫"
echo "   2. 檢查 README.md 是否正確顯示"
echo "   3. 設定分支保護規則（可選）"
echo "   4. 啟用 GitHub Pages（可選）"
echo ""
echo "📚 詳細指南請參考: docs/GITHUB_SETUP.md"
echo "🎉 感謝使用 MCP 監控系統！"
