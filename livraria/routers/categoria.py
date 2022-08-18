from fastapi import APIRouter, Depends, Response, status, HTTPException
from ..database import SessionLocal, get_db
from .. import models, schemas
from typing import Optional

router = APIRouter(
    tags = ['Categorias'],
    prefix = '/categorias'
)

@router.get('/')
def list_all(search : Optional[str] = "", db: SessionLocal = Depends(get_db)):
    if search != "":
        categoria = db.query(models.Categoria).filter(models.Categoria.descricao.contains(search)).all()
    else:
        categoria = db.query(models.Categoria).all()
    return categoria

@router.post('/', status_code=status.HTTP_201_CREATED)
def create(request: schemas.Categoria, db: SessionLocal = Depends(get_db)):
    new_categoria = models.Categoria(descricao=request.descricao)
    db.add(new_categoria)
    db.commit()
    db.refresh(new_categoria)
    return new_categoria

@router.get('/{id}', status_code=status.HTTP_200_OK)
def retrieve(id: int, db: SessionLocal = Depends(get_db)):
    categoria = db.query(models.Categoria).filter(models.Categoria.id == id).first()
    if not categoria:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'categoria with id equals to {id} was not found')
    return categoria

@router.delete('/{id}')
def destroy(id: int, db: SessionLocal = Depends(get_db)):
    query = db.query(models.categoria).filter(models.Categoria.id == id)
    if not query.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'categoria with id equals to {id} was not found')
    query.delete(synchronize_session=False)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@router.put('/{id}', status_code=status.HTTP_202_ACCEPTED)
def update(id: int, request: schemas.Categoria, db: SessionLocal = Depends(get_db)):
    query = db.query(models.Categoria).filter(models.Categoria.id == id)
    if not query.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'categoria with id equals to {id} was not found')
    query.update( request.dict(), synchronize_session=False )
    db.commit()
    return query.first()