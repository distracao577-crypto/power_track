from pydantic import BaseModel, field_validator
from datetime import date
from typing import Optional

# Este é o modelo que o Frontend envia (Task 2.1)
class MovimentacaoBase(BaseModel):
    valor: float
    tipo: str          # 'entrada' ou 'saida'
    data: date         # Formato esperado: 'AAAA-MM-DD'
    descricao: str

    @field_validator('valor')
    def valor_positivo(cls, v):
        if v <= 0:
            raise ValueError('O valor deve ser maior que zero')
        return v

# Este é o modelo que o Backend devolve (já com o ID do banco)
class Movimentacao(MovimentacaoBase):
    id: int

    class Config:
        from_attributes = True
