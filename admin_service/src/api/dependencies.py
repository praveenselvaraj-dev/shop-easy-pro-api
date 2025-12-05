from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from src.infrastructure.database.connection import get_db
from src.config.security import decode_token

from src.infrastructure.repositories.admin_repository_Impl import AdminRepositoryImpl
from src.domain.services.admin_service import AdminService
from sqlalchemy.orm import Session
security = HTTPBearer()


def get_admin_repo(db: Session = Depends(get_db)):
    return AdminRepositoryImpl(db)

def get_admin_service(repo: AdminRepositoryImpl = Depends(get_admin_repo)):
    return AdminService(repo)
