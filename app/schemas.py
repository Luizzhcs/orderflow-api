from pydantic import BaseModel, Field
from typing import Optional, List
from enum import Enum

class ClienteSchema(BaseModel):
    nome: str
    email: str
    senha: str
    telefone: Optional[str] = None
    
    class Config:
        from_attributes = True
        

class ProdutoSchema(BaseModel):
    nome: str
    descricao: Optional[str] = None
    preco: float
    estoque: int
    
    class Config: 
        from_attributes = True
        
        
class ItemPedidoSchema(BaseModel):
    id_produto: int
    quantidade: int = Field(ge=1)
    
    class Config: 
        from_attributes = True
        
        
class PedidoSchema(BaseModel):
    itens: List[ItemPedidoSchema] = Field (min_length=1)
    
    class Config:
        from_attributes = True
        
        
class LoginSchema(BaseModel):
    email: str
    senha: str
    
    class Config:
        from_attributes = True
        
        
class ClienteRespostaSchema(BaseModel):
    id: int
    nome: str
    email: str
    telefone: Optional[str] = None
    tipo: str
    
    class Config: 
        from_attributes = True
        
        
class ProdutoRespostaSchema(BaseModel):
    id: int
    nome: str
    descricao: Optional[str] = None
    preco: float
    estoque: int
    
    class Config: 
        from_attributes = True
        
        
class ItemPedidoRespostaSchema (BaseModel):
    id: int
    id_produto: int
    quantidade: int
    preco_unitario: float
    produto: ProdutoRespostaSchema
    
    class Config:
        from_attributes = True
        
        
class PedidoRespostaSchema(BaseModel):
    id: int
    id_cliente: int
    status: str
    valor_total: float
    itens: List[ItemPedidoRespostaSchema]
    
    class Config: 
        from_attributes = True
        
        
class StatusPedido(str, Enum):
    PROCESSANDO = "PROCESSANDO"
    ENVIADO = "ENVIADO"
    CONCLUIDO = "CONCLUIDO"
    
    
class StatusPedidoSchema(BaseModel):
    status: StatusPedido
    
    class Config:
        from_attributes = True
      
  
