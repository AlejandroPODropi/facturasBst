"""
Router para endpoints de usuarios.
Maneja la creación, consulta y actualización de usuarios del sistema.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from src.database import get_db
from src.models import User
from src.schemas import UserCreate, UserUpdate, User as UserSchema

router = APIRouter()


@router.post("/", response_model=UserSchema, status_code=status.HTTP_201_CREATED)
async def create_user(user: UserCreate, db: Session = Depends(get_db)):
    """
    Crear un nuevo usuario en el sistema.
    
    Args:
        user: Datos del usuario a crear
        db: Sesión de base de datos
        
    Returns:
        UserSchema: Usuario creado
        
    Raises:
        HTTPException: Si el email ya existe
    """
    # Verificar si el email ya existe
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El email ya está registrado en el sistema"
        )
    
    # Crear nuevo usuario
    db_user = User(**user.dict())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return db_user


@router.get("/", response_model=List[UserSchema])
async def get_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Obtener lista de usuarios con paginación.
    
    Args:
        skip: Número de registros a omitir
        limit: Número máximo de registros a retornar
        db: Sesión de base de datos
        
    Returns:
        List[UserSchema]: Lista de usuarios
    """
    users = db.query(User).offset(skip).limit(limit).all()
    return users


@router.get("/{user_id}", response_model=UserSchema)
async def get_user(user_id: int, db: Session = Depends(get_db)):
    """
    Obtener un usuario específico por ID.
    
    Args:
        user_id: ID del usuario
        db: Sesión de base de datos
        
    Returns:
        UserSchema: Usuario encontrado
        
    Raises:
        HTTPException: Si el usuario no existe
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )
    return user


@router.put("/{user_id}", response_model=UserSchema)
async def update_user(
    user_id: int,
    user_update: UserUpdate,
    db: Session = Depends(get_db)
):
    """
    Actualizar un usuario existente.
    
    Args:
        user_id: ID del usuario a actualizar
        user_update: Datos a actualizar
        db: Sesión de base de datos
        
    Returns:
        UserSchema: Usuario actualizado
        
    Raises:
        HTTPException: Si el usuario no existe o el email ya está en uso
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )
    
    # Verificar si el nuevo email ya existe (si se está actualizando)
    if user_update.email and user_update.email != user.email:
        existing_user = db.query(User).filter(User.email == user_update.email).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El email ya está registrado en el sistema"
            )
    
    # Actualizar campos
    update_data = user_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(user, field, value)
    
    db.commit()
    db.refresh(user)
    
    return user


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id: int, db: Session = Depends(get_db)):
    """
    Eliminar un usuario del sistema.
    
    Args:
        user_id: ID del usuario a eliminar
        db: Sesión de base de datos
        
    Raises:
        HTTPException: Si el usuario no existe
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )
    
    db.delete(user)
    db.commit()
