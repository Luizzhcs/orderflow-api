
from sqlalchemy.orm import sessionmaker, Session
from fastapi import HTTPException, Depends
from jose import jwt, JWTError

from app.models import Cliente, db
from app.security import SECRET_KEY, ALGORITHM, oauth2_schema


def pegar_sessao():
    SessionLocal = sessionmaker(bind=db)
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


def verificar_token(
    token: str = Depends(oauth2_schema),
    session: Session = Depends(pegar_sessao)
):
    try:
        dic_info = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        if dic_info.get("type") != "access":
            raise HTTPException(
                status_code=401,
                detail="Tipo de token inválido."
            )

        id_usuario = int(dic_info.get("sub"))

        if not id_usuario:
            raise HTTPException(
                status_code=401,
                detail="Token inválido."
            )

    except (JWTError, ValueError, TypeError):
        raise HTTPException(
            status_code=401,
            detail="Token inválido ou expirado."
        )

    usuario = session.query(Cliente).filter(
        Cliente.id == id_usuario
    ).first()

    if not usuario:
        raise HTTPException(
            status_code=401,
            detail="Cliente não encontrado."
        )

    return usuario


def verificar_refresh_token(
    token: str = Depends(oauth2_schema),
    session: Session = Depends(pegar_sessao)
):
    try:
        dic_info = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        if dic_info.get("type") != "refresh":
            raise HTTPException(
                status_code=401,
                detail="Token de renovação inválido."
            )

        id_usuario = int(dic_info.get("sub"))

        if not id_usuario:
            raise HTTPException(
                status_code=401,
                detail="Token inválido."
            )

    except (JWTError, ValueError, TypeError):
        raise HTTPException(
            status_code=401,
            detail="Token inválido ou expirado."
        )

    usuario = session.query(Cliente).filter(
        Cliente.id == id_usuario
    ).first()

    if not usuario:
        raise HTTPException(
            status_code=401,
            detail="Cliente não encontrado."
        )

    return usuario


def verificar_admin(usuario: Cliente = Depends(verificar_token)):
    if usuario.tipo != "admin":
        raise HTTPException(
            status_code=403,
            detail="Acesso permitido apenas para administradores."
        )

    return usuario
