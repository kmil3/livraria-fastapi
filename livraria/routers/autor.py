from fastapi import APIRouter, Depends, Response, status, HTTPException
from ..database import SessionLocal, get_db
from .. import models, schemas
from typing import Optional

router = APIRouter(
    tags = ['Autores'],
    prefix = '/autores'
)

@router.get('/')
def list_all(search : Optional[str] = "", db: SessionLocal = Depends(get_db)):
    if search != "":
        autor = db.query(models.Autor).filter(models.Autor.nome.contains(search)).all()
    else:
        autor = db.query(models.Autor).all()
    return autor

@router.post('/', status_code=status.HTTP_201_CREATED)
def create(request: schemas.Autor, db: SessionLocal = Depends(get_db)):
    new_autor = models.Autor(nome=request.nome)
    db.add(new_autor)
    db.commit()
    db.refresh(new_autor)
    return new_autor

@router.get('/{id}', status_code=status.HTTP_200_OK)
def retrieve(id: int, db: SessionLocal = Depends(get_db)):
    autor = db.query(models.Autor).filter(models.Autor.id == id).first()
    if not autor:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'autor with id equals to {id} was not found')
    return autor

@router.delete('/{id}')
def destroy(id: int, db: SessionLocal = Depends(get_db)):
    query = db.query(models.Autor).filter(models.Autor.id == id)
    if not query.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'autor with id equals to {id} was not found')
    query.delete(synchronize_session=False)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@router.put('/{id}', status_code=status.HTTP_202_ACCEPTED)
def update(id: int, request: schemas.Autor, db: SessionLocal = Depends(get_db)):
    query = db.query(models.Autor).filter(models.Autor.id == id)
    if not query.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'autor with id equals to {id} was not found')
    query.update( request.dict(), synchronize_session=False )
    db.commit()
    return query.first()