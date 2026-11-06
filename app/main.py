from fastapi import FastAPI

from app.routes.clientes_routes import clientes_router
from app.routes.produtos_routes import produtos_router
from app.routes.pedidos_routes import pedidos_router


app = FastAPI(title="OrderFlow API", description="API para gerenciamento de pedidos e vendas", version="1.0.0")
app.include_router(clientes_router)
app.include_router(produtos_router)
app.include_router(pedidos_router)