

from fastapi import FastAPI
from routers import router 

app = FastAPI(title="Controle Financeiro Power Track")

# Conecta as rotas do arquivo routers.py ao app principal
app.include_router(router)

if __name__ == "__main__":
    import uvicorn
    # O reload=True ajuda no desenvolvimento (reinicia ao salvar)
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)


