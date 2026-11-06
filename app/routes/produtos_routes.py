from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List


from app.dependencies import pegar_sessao, verificar_admin, verificar_token
from app.schemas import ProdutoSchema, ProdutoRespostaSchema
from app.models import Produto


produtos_router = APIRouter(prefix="/produtos", tags=["produtos"], dependencies=[Depends(verificar_token)])

@produtos_router.post("/", dependencies=[Depends(verificar_admin)])
def cadastrar_produto(produto_schema: ProdutoSchema,session: Session = Depends(pegar_sessao)):
    novo_produto = Produto(nome=produto_schema.nome, descricao=produto_schema.descricao, preco=produto_schema.preco, estoque=produto_schema.estoque)
    session.add(novo_produto)
    session.commit()
    return{"mensagem": "Produto cadastrado com sucesso!"} 


@produtos_router.get("/", response_model=List[ProdutoRespostaSchema])
def listar_produtos (session: Session = Depends(pegar_sessao)):
    lista_produtos = session.query(Produto).all()
    return lista_produtos 


@produtos_router.get("/{id_produto}", response_model=ProdutoRespostaSchema)
def buscar_produto_unico(id_produto: int, session: Session = Depends(pegar_sessao)):
   produto = session.query(Produto).filter(Produto.id == id_produto).first()
   if not produto:
       raise HTTPException(status_code=404, detail="Produto não encontrado.")
   return produto


@produtos_router.put("/{id_produto}", dependencies=[Depends(verificar_admin)], response_model=ProdutoRespostaSchema)
def atualizar_produto(id_produto: int, produto_schema: ProdutoSchema, session: Session = Depends(pegar_sessao)):
    produto_atualizado = session.query(Produto).filter(Produto.id==id_produto).first()
    if not produto_atualizado:
        raise HTTPException(status_code=404, detail="Produto não encontrado.")
    produto_atualizado.nome = produto_schema.nome
    produto_atualizado.descricao = produto_schema.descricao
    produto_atualizado.preco = produto_schema.preco
    produto_atualizado.estoque = produto_schema.estoque
    session.commit()
    session.refresh(produto_atualizado)
    return produto_atualizado


@produtos_router.delete("/{id_produto}", dependencies=[Depends(verificar_admin)])
def deletar_produto(id_produto: int, session: Session = Depends(pegar_sessao)):
    produto_deletado = session.query(Produto).filter(Produto.id==id_produto).first()
    if not produto_deletado:
        raise HTTPException(status_code=404, detail="Produto não encontrado.")
    session.delete(produto_deletado)
    session.commit()
    return {"mensagem": "Produto deletado com sucesso."} 


