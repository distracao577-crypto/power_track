import httpx
import os

BASE_URL = "http://powertrack_backend:8000"

async def get_dashboard(mes=None, ano=None):
    params = {}
    if mes: params['mes'] = mes
    if ano: params['ano'] = ano

    async with httpx.AsyncClient(timeout=10.0) as client:
        r = await client.get(f"{BASE_URL}/dashboard", params=params)
        return r.json()

async def get_grafico():
    async with httpx.AsyncClient(timeout=10.0) as client:
        r = await client.get(f"{BASE_URL}/extrato/grafico")
        return r.json()

async def post_transacao(payload):
    async with httpx.AsyncClient(timeout=10.0) as client:
        r = await client.post(f"{BASE_URL}/transacoes", json=payload)
        return r.status_code == 201

async def chat_ia_stream(pergunta):
    url = f"{BASE_URL}/chat?pergunta={pergunta}"
    async with httpx.AsyncClient(timeout=None) as client:
        async with client.stream("POST", url) as response:
            async for chunk in response.aiter_text():
                yield chunk
