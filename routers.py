from fastapi import APIRouter, Query, HTTPException, status
from schemas import Movimentacao, MovimentacaoBase  
from datetime import date
from typing import List


router = APIRouter()

db_movimentacoes = []
id_counter = 1

@router.post("/adicionar_entrada", response_model=Movimentacao)
def adicionar_entrada(item: MovimentacaoBase):
    global id_counter

    dados_entrada = item.model_dump(exclude={"id"})

    nova = Movimentacao(id=id_counter, **dados_entrada, tipo="Valor de entrada")
    db_movimentacoes.append(nova)
    id_counter += 1
    return nova


@router.post("/adicionar_saida", response_model=Movimentacao)
def adicionar_saida(item: MovimentacaoBase):
    global id_counter
    nova = Movimentacao(id=id_counter, **item.model_dump(), tipo="Valor de saida")
    db_movimentacoes.append(nova)
    id_counter += 1
    return nova

@router.put("/atualizar_movimentacao")
def atualizar_movimentacao(movimentacao_id: int, item: MovimentacaoBase):
    for index, m in enumerate(db_movimentacoes):
        if m.id == movimentacao_id:
            movimentacao_atualizada = Movimentacao(id=movimentacao_id, **item.model_dump(), tipo=m.tipo)
            db_movimentacoes[index] = movimentacao_atualizada
            return {"status": "sucesso", "item": movimentacao_atualizada}
    raise HTTPException(status_code=404, detail="Movimentação não encontrada")


@router.get("/obter_extrato", response_model=Movimentacao)
def obter_extrato(
    data_inicio: date = Query(..., description="Data de início (AAAA-MM-DD)"), 
    data_fim: date = Query(..., description="Data de fim (AAAA-MM-DD)")
):
   
    if data_inicio > data_fim:
        raise HTTPException(status_code=400, detail="A data de início não pode ser maior que a data de fim.")

    extrato_falso = [
        {"id": 1, "valor": -50.0, "descricao": "Netflix", "data": data_inicio, "categoria": "Lazer"},
        {"id": 2, "valor": -120.0, "descricao": "Mercado", "data": data_fim, "categoria": "Alimentação"}
    ]

    return extrato_falso

@router.delete("/movimentacao/{id}", status_code=status.HTTP_204_NO_CONTENT)
def deletar_movimentacao(id: int):

    movimentacao_existe = True
    if not movimentacao_existe:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"Movimentação não encontrada."
        )
    print(f"Removendo a movimentação ID: {id}")
    return None