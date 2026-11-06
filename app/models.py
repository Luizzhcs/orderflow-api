import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import relationship

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

db = create_engine(DATABASE_URL)
Base = declarative_base()


class Cliente (Base):
    __tablename__ = "cliente"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    nome = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True)
    senha = Column(String, nullable=False)
    telefone = Column(String, nullable=True)
    tipo = Column(String, nullable=False, server_default="cliente")
    pedidos = relationship("Pedido", back_populates="cliente")
    

class Produto (Base):
    __tablename__ = "produto"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    nome = Column(String, nullable=False)
    descricao = Column(String, nullable=True)
    preco = Column(Float, nullable=False)
    estoque = Column(Integer, nullable=False)
    itens_pedido = relationship("ItemPedido", back_populates="produto")
    
    
class Pedido (Base):
    __tablename__ = "pedido"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    id_cliente = Column(Integer, ForeignKey("cliente.id"), nullable=False)
    status = Column(String, nullable=False)
    valor_total = Column(Float, nullable=False)
    cliente = relationship("Cliente", back_populates="pedidos")
    itens = relationship("ItemPedido", back_populates="pedido")
    
    
class ItemPedido (Base):
    __tablename__ = "item_pedido"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    id_pedido = Column(Integer, ForeignKey("pedido.id"), nullable=False)
    id_produto = Column(Integer, ForeignKey("produto.id"), nullable=False)
    quantidade = Column(Integer, nullable=False)
    preco_unitario = Column(Float, nullable=False)
    pedido = relationship("Pedido", back_populates="itens")
    produto = relationship("Produto", back_populates="itens_pedido")