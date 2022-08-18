from typing import List
from fastapi import APIRouter, Depends, Response, status, HTTPException
from ..database import SessionLocal, get_db
from .. import models, schemas
from typing import Optional


router = APIRouter(
    tags = ['Livros'],
    prefix = '/livros'
)

@router.get('/', response_model=List[schemas.LivroShow])
def list_all(search : Optional[str] = "", categoria: Optional[int] = 0, editora: Optional[int] = 0, maxpreco: Optional[float] = 0, db: SessionLocal = Depends(get_db)):
    livros = db.query(models.Livro).all()
    
    if search != "":
        livros = db.query(models.Livro).filter(models.Livro.titulo.contains(search)).all()
    
    if categoria != 0:
        livros = db.query(models.Livro).filter(models.Livro.categoria_id == categoria).all()
    
    if editora != 0:
        livros = db.query(models.Livro).filter(models.Livro.editora_id == editora).all()
    
    if maxpreco != 0:
        livros = db.query(models.Livro).filter(models.Livro.preco <= maxpreco).all()
    
    return livros

@router.post('/', status_code=status.HTTP_201_CREATED, response_model=schemas.LivroShow)
def create(request: schemas.Livro, db: SessionLocal = Depends(get_db)):
    query = db.query(models.Editora).filter(models.Editora.id == request.editora_id)
    if not query.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'editora with id equals to {request.editora_id} was not found')

    query = db.query(models.Categoria).filter(models.Categoria.id == request.categoria_id)
    if not query.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'categoria with id equals to {request.categoria_id} was not found')

    new_livro = models.Livro(
        titulo = request.titulo,
        ISBN = request.ISBN,
        quantidade = request.quantidade,
        preco = request.preco,
        editora_id = request.editora_id,
        categoria_id = request.categoria_id
    )

    for autor_id in request.autores:
        autor = db.query(models.Autor).filter(models.Autor.id == autor_id).first()
        if not autor:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'autor with id equals to {autor_id} was not found')
        new_livro.autores.append(autor)

    db.add(new_livro)
    db.commit()
    db.refresh(new_livro)
    return new_livro

@router.get('/{id}', status_code=status.HTTP_200_OK, response_model=schemas.LivroShow)
def retrieve(id: int, db: SessionLocal = Depends(get_db)):
    livro = db.query(models.Livro).filter(models.Livro.id == id).first()
    if not livro:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'livro with id equals to {id} was not found')
    return livro

@router.delete('/{id}')
def destroy(id: int, db: SessionLocal = Depends(get_db)):
    query = db.query(models.Livro).filter(models.Livro.id == id)
    if not query.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'livro with id equals to {id} was not found')
    
    query.first().autores = []

    query.delete(synchronize_session=False)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@router.put('/{id}', status_code=status.HTTP_202_ACCEPTED, response_model=schemas.LivroShow)
def update(id: int, request: schemas.Livro, db: SessionLocal = Depends(get_db)):
    query = db.query(models.Livro).filter(models.Livro.id == id)
    query.update( request.dict(), synchronize_session=False )
    query.update( {
        'titulo' : request.titulo, 
        'ISBN' : request.ISBN,
        'quantidade' : request.quantidade,
        'preco': request.preco,
        'editora_id' : request.editora_id,
        'categoria_id' : request.categoria_id
    }, synchronize_session=False )
    
    livro = query.first()
    livro.autores = []

    for autor_id in request.autores:
        autor = db.query(models.Autor).filter(models.Autor.id == autor_id).first()
        if not autor:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'autor with id equals to {autor_id} was not found')
        
        livro.autores.append(autor)

    db.commit()
    return query.first()