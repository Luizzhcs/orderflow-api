from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from jose import jwt, JWTError
from datetime import datetime, timedelta, timezone
from fastapi.security import OAuth2PasswordRequestForm

from app.models import Cliente
from app.schemas import ClienteSchema, LoginSchema
from app.dependencies import pegar_sessao, verificar_token, verificar_refresh_token
from app.security import bcrypt_context, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES, SECRET_KEY



clientes_router = APIRouter(prefix="/clientes", tags=["clientes"])


def criar_token(id_usuario, duracao_token=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES), tipo_token="access"):
   data_expiracao = datetime.now(timezone.utc) + duracao_token
   dic_info = {"sub": str(id_usuario), "exp": data_expiracao, "type": tipo_token }
   jwt_codificado = jwt.encode(dic_info, SECRET_KEY, ALGORITHM)
   return jwt_codificado


@clientes_router.post("/")
def cadastrar_cliente(cliente_schema: ClienteSchema, session: Session = Depends(pegar_sessao)):
      cliente_existente = session.query(Cliente).filter(Cliente.email==cliente_schema.email).first()
      if cliente_existente:
         raise HTTPException(status_code=400, detail="Email já cadastrado.")
      senha_criptografada = bcrypt_context.hash(cliente_schema.senha)
      novo_cliente = Cliente(nome=cliente_schema.nome, email=cliente_schema.email, senha=senha_criptografada, telefone=cliente_schema.telefone)
      session.add(novo_cliente)
      session.commit()
      return{"mensagem":"Cliente cadastrado com sucesso!"} 
   
   
@clientes_router.post("/login")
def login(login_schema: LoginSchema, session: Session = Depends(pegar_sessao)):
   cliente = session.query(Cliente).filter(Cliente.email==login_schema.email).first()
   if not cliente:
      raise HTTPException(status_code=401, detail="Email ou senha inválidos.")
   if not bcrypt_context.verify(login_schema.senha, cliente.senha):
      raise HTTPException(status_code=401, detail="Email ou senha inválidos.") 
   access_token = criar_token(cliente.id)
   refresh_token = criar_token(cliente.id, duracao_token=timedelta(days=7), tipo_token="refresh")
   
   return{"access_token": access_token, "refresh_token": refresh_token, "token_type": "Bearer"}
   
   
@clientes_router.post("/login-form")
def login_form(dados_formulario: OAuth2PasswordRequestForm = Depends(), session: Session = Depends(pegar_sessao)):
   cliente = session.query(Cliente).filter(Cliente.email==dados_formulario.username).first()
   if not cliente:
      raise HTTPException(status_code=401, detail="Email ou senha inválidos.")
   if not bcrypt_context.verify(dados_formulario.password, cliente.senha):
      raise HTTPException(status_code=401, detail="Email ou senha inválidos.") 
   access_token = criar_token(cliente.id)
   
   return{"access_token": access_token, "token_type": "Bearer"}
   
   
@clientes_router.post("/refresh")
def use_refresh_token(cliente: Cliente = Depends(verificar_refresh_token)):
    access_token = criar_token(cliente.id)
    return {"access_token": access_token, "token_type": "Bearer"}