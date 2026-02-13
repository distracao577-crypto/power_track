from pydantic import BaseModel, field_serializer, field_validator, Field
from datetime import datetime
from datetime import date



class Movimentacao(BaseModel):
    # ... outros campos ...
    data: datetime = Field(default_factory=datetime.now) 

class MovimentacaoBase(BaseModel):
    id: int
    valor: float
    data: date
    descricao: str

# configurando a data para dia, mes e ano
class Config:
        json_encoders = {
            date: lambda v: v.strftime('%d/%m/%Y')
        }

class Movimentacao(MovimentacaoBase):
    id: int
    tipo: str

class Config:
     orm_mode = True
     