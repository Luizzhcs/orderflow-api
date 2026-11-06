from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.dependencies import verificar_token, verificar_admin, pegar_sessao
from app.models import Cliente, Produto, Pedido, ItemPedido
from app.schemas import PedidoSchema, PedidoRespostaSchema, StatusPedidoSchema

pedidos_router = APIRouter(prefix="/pedidos", tags=["pedidos"], dependencies=[Depends(verificar_token)])


@pedidos_router.post("/")
def criar_pedido(pedido: PedidoSchema, usuario: Cliente = Depends(verificar_token), session: Session = Depends(pegar_sessao)):
    try:
        novo_pedido = Pedido(id_cliente=usuario.id, status="PENDENTE", valor_total=0)
        session.add(novo_pedido)
        session.flush()
        
        valor_total = 0
        for item in pedido.itens:
            produto = session.query(Produto).filter(Produto.id==item.id_produto).first()
            if not produto:
                raise HTTPException(status_code=404, detail="Produto não encontrado.")
            if item.quantidade > produto.estoque:
                raise HTTPException(status_code=400, detail="Estoque insuficiente.")
            novo_item = ItemPedido(id_pedido=novo_pedido.id, id_produto=item.id_produto, quantidade=item.quantidade, preco_unitario=produto.preco)
            session.add(novo_item) 
            valor_total += item.quantidade*produto.preco
            produto.estoque -= item.quantidade
        novo_pedido.valor_total = valor_total
        session.commit()
        session.refresh(novo_pedido)
    except Exception:
        session.rollback()
        raise 
    return {
    "mensagem": "Pedido criado com sucesso!",
    "id_pedido": novo_pedido.id,
    "valor_total": novo_pedido.valor_total
}
    
    
@pedidos_router.get("/", response_model=List[PedidoRespostaSchema])
def listar_pedidos(usuario: Cliente = Depends(verificar_token), session: Session = Depends(pegar_sessao)):
    if usuario.tipo == "admin":
        pedidos = session.query(Pedido).all()
    else:
        pedidos = session.query(Pedido).filter(Pedido.id_cliente==usuario.id).all()
    return pedidos 


@pedidos_router.get("/{id_pedido}", response_model=PedidoRespostaSchema)
def listar_pedido_especifico(id_pedido: int, usuario: Cliente = Depends(verificar_token), session: Session = Depends(pegar_sessao)):
    pedido = session.query(Pedido).filter(Pedido.id == id_pedido).first()
    if not pedido:
        raise HTTPException(status_code=404, detail="Pedido não encontrado.")
    if usuario.tipo == "admin":
        return pedido

    if pedido.id_cliente == usuario.id:
        return pedido

    raise HTTPException(status_code=403, detail="Você não tem autorização para acessar este pedido.")


@pedidos_router.patch("/{id_pedido}/cancelar")
def cancelar_pedido(
    id_pedido: int,
    usuario: Cliente = Depends(verificar_token),
    session: Session = Depends(pegar_sessao)
):
    pedido = session.query(Pedido).filter(Pedido.id == id_pedido).first()

    if not pedido:
        raise HTTPException(status_code=404, detail="Pedido não encontrado.")

    if usuario.tipo != "admin" and pedido.id_cliente != usuario.id:
        raise HTTPException(status_code=403, detail="Você não tem autorização para cancelar esse pedido.")

    if pedido.status != "PENDENTE":
        raise HTTPException(status_code=400, detail="Este pedido não pode ser cancelado.")

    try:
        for item in pedido.itens:
            item.produto.estoque += item.quantidade

        pedido.status = "CANCELADO"

        session.commit()
        session.refresh(pedido)

    except Exception:
        session.rollback()
        raise

    return {
        "mensagem": "Pedido cancelado com sucesso!",
        "id_pedido": pedido.id,
        "status": pedido.status
    }
    
    
@pedidos_router.patch("/status/{id_pedido}", dependencies=[Depends(verificar_admin)])
def atualizar_status (id_pedido: int, status_schema: StatusPedidoSchema, session: Session = Depends(pegar_sessao)):
    pedido = session.query(Pedido).filter(Pedido.id==id_pedido).first()
    
    if not pedido:
        raise HTTPException(status_code=404, detail="Pedido inexistente.")
    try:
        pedido.status = status_schema.status.value
        session.commit()
        session.refresh(pedido)
    except Exception:
        session.rollback()
        raise
    return{"mensagem": "Status do pedido atualizado com sucesso.", "id_pedido": pedido.id, "status": pedido.status}   
    
    
