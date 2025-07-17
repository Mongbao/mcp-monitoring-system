"""
簡單的 FastAPI 測試應用程式
"""
from fastapi import FastAPI

app = FastAPI(title="MCP 監控系統測試")

@app.get("/")
async def root():
    return {"message": "MCP 監控系統運行中"}

@app.get("/health")
async def health():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8003)
