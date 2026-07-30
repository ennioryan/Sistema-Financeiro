from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError, ResponseValidationError
from fastapi.staticfiles import StaticFiles
from database import engine, Base
from routers import categoria_router, transacao_router, meta_router, views_router
import logging

# Configurar logging básico para tracebacks no console
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("main")

# Criar tabelas no banco de dados se não existirem
Base.metadata.create_all(engine)

app = FastAPI(
    title="Finanças Pro API",
    description="API do Sistema Financeiro Pessoal",
    version="1.0.0"
)

# Exception handler para erros de validação de envio (RequestValidationError - HTTP 422)
@app.exception_handler(RequestValidationError)
async def request_validation_exception_handler(request: Request, exc: RequestValidationError):
    logger.error(f"Erro de validação na requisição: {exc.errors()}")
    return JSONResponse(
        status_code=422,
        content={
            "detail": "Os dados enviados na requisição são inválidos.",
            "errors": exc.errors()
        }
    )

# Exception handler para erros de validação de retorno (ResponseValidationError - HTTP 500)
@app.exception_handler(ResponseValidationError)
async def response_validation_exception_handler(request: Request, exc: ResponseValidationError):
    logger.error(f"Erro de validação na resposta da API: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Erro interno de validação na resposta do servidor.",
            "error_message": str(exc)
        }
    )

# Exception handler genérico para qualquer outra exceção não tratada (HTTP 500)
@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    logger.error(f"Erro interno não tratado: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Ocorreu um erro interno no servidor.",
            "error_message": str(exc),
            "error_type": exc.__class__.__name__
        }
    )

# Servir arquivos estáticos (CSS, JS, Imagens)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Incluir roteadores
app.include_router(views_router.router)
app.include_router(categoria_router.router)
app.include_router(transacao_router.router)
app.include_router(meta_router.router)