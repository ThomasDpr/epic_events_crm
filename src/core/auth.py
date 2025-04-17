import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Optional

import jwt
from sqlalchemy.orm import Session

from core.security import verify_password
from models.user import User


class AuthManager:
    """Gestionnaire d'authentification"""
    
    TOKEN_FILE = Path(__file__).parent.parent.parent / '.epic_events_token'
    # Clé secrète pour signer les tokens JWT - récupérée depuis les variables d'environnement
    SECRET_KEY = os.getenv("JWT_SECRET_KEY", "epic_events_secret_key")
    # Durée de validité du token en secondes (24 heures par défaut)
    TOKEN_EXPIRY = int(os.getenv("JWT_TOKEN_EXPIRY", 86400))
    
    def __init__(self, db: Session):
        self.db = db

    def authenticate(self, email: str, password: str) -> Optional[User]:
        """Authentifie un utilisateur avec email et mot de passe"""
        user = self.db.query(User).filter(User.email == email).first()
        if user and verify_password(password, user.password):
            self._save_token(user)
            return user
        return None

    def _generate_token(self, user: User) -> str:
        """Génère un token JWT pour l'utilisateur"""
        payload = {
            'user_id': user.id,
            'email': user.email,
            'department': user.department.value,
            'exp': datetime.utcnow() + timedelta(seconds=self.TOKEN_EXPIRY),
            'iat': datetime.utcnow()
        }
        return jwt.encode(payload, self.SECRET_KEY, algorithm='HS256')

    def _save_token(self, user: User) -> None:
        """Sauvegarde le token JWT dans un fichier"""
        token = self._generate_token(user)
        with open(self.TOKEN_FILE, 'w') as f:
            f.write(token)

    def _decode_token(self, token: str) -> Optional[Dict]:
        """Décode un token JWT et vérifie sa validité"""
        try:
            return jwt.decode(token, self.SECRET_KEY, algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            # Token expiré
            return None
        except jwt.InvalidTokenError:
            # Token invalide
            return None

    def get_current_user(self) -> Optional[User]:
        """Récupère l'utilisateur actuellement connecté à partir du token"""
        if not self.TOKEN_FILE.exists():
            return None
        
        try:
            with open(self.TOKEN_FILE, 'r') as f:
                token = f.read().strip()
                
            payload = self._decode_token(token)
            if not payload:
                # Token invalide ou expiré
                self.logout()
                return None
                
            return self.db.query(User).get(payload['user_id'])
        except Exception as e:
            print(f"Erreur lors de la récupération de l'utilisateur: {str(e)}")
            return None

    def logout(self) -> None:
        """Déconnecte l'utilisateur en supprimant le token"""
        if self.TOKEN_FILE.exists():
            os.remove(self.TOKEN_FILE)
            
    def check_permission(self, required_department=None) -> bool:
        """Vérifie si l'utilisateur a les permissions nécessaires"""
        user = self.get_current_user()
        if not user:
            return False
            
        if required_department and user.department.value != required_department:
            return False
            
        return True