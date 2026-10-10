from pydantic import BaseModel, EmailStr, field_validator, ConfigDict
from typing import Optional
from datetime import datetime
import re

class UsuarioBase(BaseModel):
    nome: str
    email: EmailStr

    @field_validator("nome")
    @classmethod
    def validar_nome(cls, v: str) -> str:
        v = v.strip()
        if len(v) < 2:
            raise ValueError("O nome deve ter pelo menos 2 caracteres.")
        return v

    @field_validator("email", mode="before")
    @classmethod
    def normalizar_email(cls, v: str) -> str:
        if isinstance(v, str):
            return v.strip().lower()
        return v

class UsuarioCreate(UsuarioBase):
    senha: str

    @field_validator("senha")
    @classmethod
    def validar_regras_senha(cls, v: str) -> str:
        erros = []

        # Regra 1: Mínimo 6 e máximo 14 caracteres
        if len(v) < 6 or len(v) > 14:
            erros.append("A senha deve ter entre 6 e 14 caracteres.")

        # Regra 2: Pelo menos 1 letra maiúscula
        if not any(c.isupper() for c in v):
            erros.append("A senha deve conter pelo menos uma letra maiúscula.")

        # Regra 3: Pelo menos 1 letra minúscula
        if not any(c.islower() for c in v):
            erros.append("A senha deve conter pelo menos uma letra minúscula.")

        # Regra 4: Pelo menos 1 número
        if not any(c.isdigit() for c in v):
            erros.append("A senha deve conter pelo menos um número.")

        # Regra 5: Pelo menos 1 caractere especial
        if not re.search(r"[^a-zA-Z0-9\s]", v):
            erros.append("A senha deve conter pelo menos um caractere especial (ex: !@#$%^&*).")

        if erros:
            # Retorna mensagens específicas indicando exatamente quais regras falharam
            raise ValueError("; ".join(erros))

        return v

class UsuarioLogin(BaseModel):
    email: EmailStr
    senha: str

    @field_validator("email", mode="before")
    @classmethod
    def normalizar_email(cls, v: str) -> str:
        if isinstance(v, str):
            return v.strip().lower()
        return v

class UsuarioResponse(BaseModel):
    id: int
    nome: str
    email: str
    criado_em: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    usuario: UsuarioResponse
