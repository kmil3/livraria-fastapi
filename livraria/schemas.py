from typing import List
from pydantic import BaseModel

class Editora(BaseModel):
    nome: str
    site: str

    class Config():
        orm_mode = True

class Autor(BaseModel):
    nome: str
    class Config():
        orm_mode = True


class Categoria(BaseModel):
    descricao: str

    class Config():
        orm_mode = True


class Livro(BaseModel):
    titulo: str
    ISBN: str
    quantidade: int
    preco: float
    editora_id: int
    categoria_id: int
    autores: List[int] = []

class Leitor(BaseModel):
    nome:str
    favoritos: List[int] = []

class LivroShow(BaseModel):
    id: int
    titulo: str
    ISBN: str
    quantidade: int
    preco: float
    editora: Editora
    categoria: Categoria
    autores: List[Autor] = []

    class Config():
        orm_mode = True


class LeitorShow(BaseModel):
    nome: str
    favoritos: List[LivroShow] = []
    
    class Config():
        orm_mode = True