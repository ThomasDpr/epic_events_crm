# src/tests/test_security.py
from core.security import hash_password, validate_password, verify_password


def test_password_hashing():
    # Test de hachage et vérification
    password = "TestPassword123"
    
    # Validation du mot de passe
    validation_error = validate_password(password)
    if validation_error:
        print(f"Erreur de validation: {validation_error}")
        return
    
    # Hash du mot de passe
    hashed = hash_password(password)
    print(f"Mot de passe haché: {hashed}")
    
    # Vérification du mot de passe
    assert verify_password(password, hashed)
    print("Vérification réussie avec le bon mot de passe")
    
    # Test avec un mauvais mot de passe
    assert not verify_password("WrongPassword123", hashed)
    print("Vérification échouée avec un mauvais mot de passe (comme prévu)")

if __name__ == "__main__":
    test_password_hashing()