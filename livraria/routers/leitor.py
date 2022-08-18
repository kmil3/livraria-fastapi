from typing import List
from fastapi import APIRouter, Depends, Response, status, HTTPException
from ..database import SessionLocal, get_db
from .. import models, schemas
from typing import Optional
from typing import Optional

router = APIRouter(
    tags = ['Leitores'],
    prefix = '/leitores'
)

@router.get('/', response_model=List[schemas.LeitorShow])
def list_all(search : Optional[str] = "", db: SessionLocal = Depends(get_db)):
    if search != "":
        leitor = db.query(models.Leitor).filter(models.Leitor.nome.contains(search)).all()
    else:
        leitor = db.query(models.Leitor).all()
    return leitor

@router.post('/', status_code=status.HTTP_201_CREATED, response_model=schemas.LeitorShow)
def create(request: schemas.Leitor, db: SessionLocal = Depends(get_db)):
    new_leitor = models.Leitor(
        nome=request.nome
        )
    for livro_id in request.favoritos:
        livro = db.query(models.Livro).filter(models.Livro.id == livro_id).first()
        if not livro:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'leitor with id equals to {livro_id} was not found')
        new_leitor.favoritos.append(livro)

    db.add(new_leitor)
    db.commit()
    db.refresh(new_leitor)
    return new_leitor


@router.get('/{id}', status_code=status.HTTP_200_OK, response_model=schemas.LeitorShow)
def retrieve(id: int, db: SessionLocal = Depends(get_db)):
    leitor = db.query(models.Leitor).filter(models.Leitor.id == id).first()
    if not leitor:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'leitor with id equals to {id} was not found')
    return leitor

@router.delete('/{id}')
def destroy(id: int, db: SessionLocal = Depends(get_db)):
    query = db.query(models.Leitor).filter(models.Leitor.id == id)
    if not query.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'leitor with id equals to {id} was not found')
    
    query.first().favoritos = []
    
    query.delete(synchronize_session=False)

    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@router.put('/{id}', status_code=status.HTTP_202_ACCEPTED, response_model=schemas.LeitorShow)
def update(id: int, request: schemas.Leitor, db: SessionLocal = Depends(get_db)):
    query = db.query(models.Leitor).filter(models.Leitor.id == id)
    
    query.update( {
        'nome' : request.nome
    }, synchronize_session=False )
    
    leitor = query.first()
    leitor.favoritos = []

    for livro_id in request.favoritos:
        livro = db.query(models.Livro).filter(models.Livro.id == livro_id).first()
        if not livro:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'leitor with id equals to {livro_id} was not found')
        leitor.favoritos.append(livro)

    db.commit()
    return query.first()