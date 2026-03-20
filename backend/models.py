from sqlalchemy import Column, Integer, String, Float, Date
from database import Base

class Movimentacao(Base):
    __tablename__ = "movimentacoes"

    id = Column(Integer, primary_key=True, index=True)
    descricao = Column(String)
    valor = Column(Float)
    tipo = Column(String) # 'entrada' ou 'saida'
    data = Column(Date)