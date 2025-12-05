from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class User:
    id: Optional[int]
    username: str
    email: str
    role: str
    is_active: bool = True
    is_verified: bool = False
    created_at: Optional[datetime] = None
    
    def is_admin(self) -> bool:
        return self.role == "admin"
    
    def can_access_admin_panel(self) -> bool:
        return self.is_admin() and self.is_active