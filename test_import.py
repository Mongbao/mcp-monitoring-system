#!/usr/bin/env python
import os
import sys

# 設置環境變數
os.environ['CI'] = 'true'
os.environ['DISCORD_TOKEN'] = 'dummy_token_for_testing'

try:
    from app.main import app
    print('✅ FastAPI 應用程式可以正常導入')
except Exception as e:
    print(f'❌ 導入失敗: {e}')
    import traceback
    traceback.print_exc()
