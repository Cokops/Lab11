import my_rust_core
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
async def root():
    # Используем функцию из Rust
    result = my_rust_core.fast_sum([1.0, 2.0, 3.0, 4.0, 5.0])
    return {"message": f"Rust computed sum: {result}"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)