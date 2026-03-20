import time
import logging
import os
from fastapi import FastAPI, Depends, HTTPException, Query, status
from fastapi.responses import StreamingResponse # Faltava este import para a IA
from sqlalchemy.orm import Session
from sqlalchemy import func
import models, schemas, database
from datetime import date
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

# Configuração do Cliente Groq
client = Groq(api_key=os.getenv("GROQ_API_KEY", "SUA_CHAVE_AQUI"))

app = FastAPI(title="Controle Financeiro Power Track")

# Cria as tabelas no banco de dados automaticamente
models.Base.metadata.create_all(bind=database.engine)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("API-FINANCEIRA")

# --- ROTA QUE O FRONTEND CHAMA (CORRIGIDA) ---
@app.post("/transacoes", status_code=status.HTTP_201_CREATED)
async def criar_transacao(item: schemas.MovimentacaoBase, db: Session = Depends(database.get_db)):
    try:
        # Cria o objeto do banco de dados (Task 2.1)
        nova = models.Movimentacao(
            valor=item.valor,
            descricao=item.descricao,
            tipo=item.tipo,
            data=item.data
        )
        
        # Validação simples (Task 2.1)
        if nova.valor <= 0:
            raise HTTPException(status_code=400, detail="O valor deve ser maior que zero")

        db.add(nova)
        db.commit()
        db.refresh(nova)
        
        logger.info(f"Nova transação registrada: {nova.descricao} - R${nova.valor}")
        return nova
    except Exception as e:
        db.rollback()
        logger.error(f"Erro ao salvar: {e}")
        raise HTTPException(status_code=500, detail="Erro interno ao salvar no banco")

@app.get("/dashboard")
def get_dashboard(
    mes: int = Query(None, ge=1, le=12), 
    ano: int = Query(None, ge=2000), 
    db: Session = Depends(database.get_db)
):
    # 1. Criamos as queries base (sem executar ainda com .scalar())
    query_ent = db.query(func.sum(models.Movimentacao.valor)).filter(models.Movimentacao.tipo.ilike('entrada'))
    query_sai = db.query(func.sum(models.Movimentacao.valor)).filter(models.Movimentacao.tipo.ilike('saida'))

    # 2. Se o usuário passou mês ou ano, aplicamos o filtro usando func.extract
    if mes:
        query_ent = query_ent.filter(func.extract('month', models.Movimentacao.data) == mes)
        query_sai = query_sai.filter(func.extract('month', models.Movimentacao.data) == mes)
    
    if ano:
        query_ent = query_ent.filter(func.extract('year', models.Movimentacao.data) == ano)
        query_sai = query_sai.filter(func.extract('year', models.Movimentacao.data) == ano)

    # 3. Agora executamos e pegamos o resultado (scalar)
    ent = query_ent.scalar()
    sai = query_sai.scalar()
    
    # 4. Sua lógica de conversão para Float (Essencial!)
    t_ent = float(ent) if ent else 0.0
    t_sai = float(sai) if sai else 0.0
    
    return {
        "saldo_total": round(t_ent - t_sai, 2),
        "total_entradas": round(t_ent, 2),
        "total_saidas": round(t_sai, 2),
        "periodo": f"{mes}/{ano}" if mes and ano else "Total Acumulado"
    }





@app.get("/extrato/grafico")
def get_grafico(db: Session = Depends(database.get_db)):
    # Retorna uma lista de 31 posições (gastos por dia) para o Highcharts (Task 3.3)
    hoje = date.today()
    gastos_por_dia = [0] * 31
    dados = db.query(
        func.extract('day', models.Movimentacao.data).label('dia'),
        func.sum(models.Movimentacao.valor).label('total')
    ).filter(
        models.Movimentacao.tipo == 'saida',
        func.extract('month', models.Movimentacao.data) == hoje.month
    ).group_by('dia').all()
    
    for dia, total in dados:
        if 1 <= int(dia) <= 31:
            gastos_por_dia[int(dia)-1] = float(total)
            
    return gastos_por_dia

@app.post("/chat")
async def chat_ia(pergunta: str, db: Session = Depends(database.get_db)):
    # 1. Busca os dados do banco para dar contexto à IA
    try:
        dados = db.query(models.Movimentacao).all()
        contexto = "\n".join([f"- {t.descricao}: R${t.valor} ({t.tipo})" for t in dados])
    except Exception:
        contexto = "Sem dados disponíveis no momento."
    
    async def gerar():
        try:
            # 2. Chama a API do Groq com Streaming
            response = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[
                    {"role": "system", "content": f"Você é um assistente financeiro conciso. Dados do usuário: {contexto}"},
                    {"role": "user", "content": pergunta}
                ],
                stream=True
            )
            for chunk in response:
                # Corrigido: acessando o conteúdo do delta corretamente
                if chunk.choices and chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
                    
        except Exception as e:
            # 3. Se a chave falhar ou a VPN bloquear, o erro aparece no CHAT
            erro_msg = str(e)
            if "401" in erro_msg:
                yield "ERRO: Sua API KEY do Groq está inválida (401). Verifique o arquivo .env."
            elif "403" in erro_msg:
                yield "ERRO: Acesso negado (403). A VPN pode estar bloqueando a conexão."
            else:
                yield f"Erro na IA: {erro_msg}"

    # 4. Retorno com cabeçalhos que impedem o navegador de "segurar" a resposta
    return StreamingResponse(
        gerar(), 
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Content-Type-Options": "nosniff"
        }
    )



if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
