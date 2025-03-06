import json
import os
from pathlib import Path
from typing import Optional

from sqlalchemy.orm import Session

from core.security import verify_password
from models.user import User


class AuthManager:
    """Gestionnaire d'authentification"""
    
    SESSION_FILE = Path(__file__).parent.parent.parent / '.epic_events_session'
    
    def __init__(self, db: Session):
        self.db = db

    def authenticate(self, email: str, password: str) -> Optional[User]:
        """Authentifie un utilisateur avec email et mot de passe"""
        user = self.db.query(User).filter(User.email == email).first()
        if user and verify_password(password, user.password):
            self._save_session(user)
            return user
        return None

    def _save_session(self, user: User) -> None:
        """Sauvegarde la session de l'utilisateur"""
        session_data = {
            'user_id': user.id,
            'email': user.email,
            'department': user.department.value
        }
        with open(self.SESSION_FILE, 'w') as f:
            json.dump(session_data, f)

    def get_current_user(self) -> Optional[User]:
        """Récupère l'utilisateur actuellement connecté"""
        if not self.SESSION_FILE.exists():
            return None
        
        try:
            with open(self.SESSION_FILE, 'r') as f:
                session_data = json.load(f)
                return self.db.query(User).get(session_data['user_id'])
        except:
            return None

    def logout(self) -> None:
        """Déconnecte l'utilisateur"""
        if self.SESSION_FILE.exists():
            os.remove(self.SESSION_FILE)