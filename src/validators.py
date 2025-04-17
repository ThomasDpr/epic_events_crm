import re
from datetime import datetime

from prompt_toolkit.validation import ValidationError, Validator

from models.user import User


class NameValidator(Validator):
    def validate(self, document):
        if not document.text:
            raise ValidationError(
                message="Le nom ne peut pas être vide",
                cursor_position=document.cursor_position
            )
        elif len(document.text) < 2:
            raise ValidationError(
                message="Le nom doit contenir au moins 2 caractères",
                cursor_position=document.cursor_position
            )

class EmailValidator(Validator):
    def __init__(self, db_session, exclude_id=None):
        self.db_session = db_session
        self.exclude_id = exclude_id
        self.pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    
    def validate(self, document):
        email = document.text
        
        if not email:
            raise ValidationError(
                message="L'email ne peut pas être vide",
                cursor_position=document.cursor_position
            )
        
        if not re.match(self.pattern, email):
            raise ValidationError(
                message="Format d'email invalide",
                cursor_position=document.cursor_position
            )
        
        query = self.db_session.query(User).filter(User.email == email)
        
        if self.exclude_id is not None:
            query = query.filter(User.id != self.exclude_id)
            
        email_exists = query.first() is not None
        if email_exists:
            raise ValidationError(
                message="Cet email existe déjà",
                cursor_position=document.cursor_position
            )

class EmployeeNumberValidator(Validator):
    def __init__(self, db_session, exclude_id=None):
        self.db_session = db_session
        self.exclude_id = exclude_id
    
    def validate(self, document):
        employee_number = document.text
        
        if not employee_number:
            raise ValidationError(
                message="Le numéro d'employé ne peut pas être vide",
                cursor_position=document.cursor_position
            )
        
    
        if not re.match(r'^\d{6}$', employee_number):
            raise ValidationError(
                message="Le numéro d'employé doit être composé exactement de 6 chiffres",
                cursor_position=document.cursor_position
            )
        
        query = self.db_session.query(User).filter(User.employee_number == employee_number)
        
        if self.exclude_id is not None:
            query = query.filter(User.id != self.exclude_id)
            
        number_exists = query.first() is not None
        if number_exists:
            raise ValidationError(
                message="Ce numéro d'employé existe déjà",
                cursor_position=document.cursor_position
            )

class PasswordComplexityValidator(Validator):
    def validate(self, document):
        password = document.text
        
        if not password:
            raise ValidationError(
                message="Le mot de passe ne peut pas être vide",
                cursor_position=document.cursor_position
            )
        
        if len(password) < 8:
            raise ValidationError(
                message="Le mot de passe doit contenir au moins 8 caractères",
                cursor_position=document.cursor_position
            )
        
        if not re.search(r'[A-Z]', password):
            raise ValidationError(
                message="Le mot de passe doit contenir au moins une majuscule",
                cursor_position=document.cursor_position
            )
        
        if not re.search(r'[a-z]', password):
            raise ValidationError(
                message="Le mot de passe doit contenir au moins une minuscule",
                cursor_position=document.cursor_position
            )
        
        if not re.search(r'[0-9]', password):
            raise ValidationError(
                message="Le mot de passe doit contenir au moins un chiffre",
                cursor_position=document.cursor_position
            )

class ClientEmailValidator(Validator):
    def __init__(self, db_session, exclude_id=None):
        self.db_session = db_session
        self.exclude_id = exclude_id
        self.pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    
    def validate(self, document):
        email = document.text
        
        if not email:
            raise ValidationError(
                message="L'email ne peut pas être vide",
                cursor_position=document.cursor_position
            )
        
        if not re.match(self.pattern, email):
            raise ValidationError(
                message="Format d'email invalide",
                cursor_position=document.cursor_position
            )
        
        from models.client import Client
        query = self.db_session.query(Client).filter(Client.email == email)
        
        if self.exclude_id is not None:
            query = query.filter(Client.id != self.exclude_id)
            
        email_exists = query.first() is not None
        if email_exists:
            raise ValidationError(
                message="Un client avec cet email existe déjà",
                cursor_position=document.cursor_position
            )

class UserExistsValidator(Validator):
    def __init__(self, db_session):
        self.db_session = db_session
        self.pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    
    def validate(self, document):
        email = document.text
        
        if not email:
            raise ValidationError(
                message="L'email ne peut pas être vide",
                cursor_position=document.cursor_position
            )
        
        if not re.match(self.pattern, email):
            raise ValidationError(
                message="Format d'email invalide",
                cursor_position=document.cursor_position
            )
        
        user_exists = self.db_session.query(User).filter(User.email == email).first() is not None
        if not user_exists:
            raise ValidationError(
                message=f"Aucun compte n'existe avec l'email '{email}'",
                cursor_position=document.cursor_position
            )

class PasswordValidator(Validator):
    def validate(self, document):
        password = document.text
        
        if not password:
            raise ValidationError(
                message="Le mot de passe ne peut pas être vide",
                cursor_position=document.cursor_position
            )

class DateTimeFormatValidator(Validator):

    
    def __init__(self, format_str="%d/%m/%Y %H:%M"):
        self.format_str = format_str
    
    def validate(self, document):
        date_str = document.text
        
        if not date_str:
            raise ValidationError(
                message="La date ne peut pas être vide",
                cursor_position=document.cursor_position
            )
        
        try:
            datetime.strptime(date_str, self.format_str)
        except ValueError:
            raise ValidationError(
                message=f"Format de date invalide. Utilisez {self.format_str.replace('%d', 'JJ').replace('%m', 'MM').replace('%Y', 'AAAA').replace('%H', 'HH').replace('%M', 'MM')}",
                cursor_position=document.cursor_position
            )


class EndDateValidator(Validator):
        
    def __init__(self, start_date, format_str="%d/%m/%Y %H:%M"):

        self.start_date = start_date
        self.format_str = format_str
    
    def validate(self, document):

        date_str = document.text
        
        if not date_str:
            raise ValidationError(
                message="La date ne peut pas être vide",
                cursor_position=document.cursor_position
            )
        
        try:
            end_date = datetime.strptime(date_str, self.format_str)
        except ValueError:
            raise ValidationError(
                message=f"Format de date invalide. Utilisez {self.format_str.replace('%d', 'JJ').replace('%m', 'MM').replace('%Y', 'AAAA').replace('%H', 'HH').replace('%M', 'MM')}",
                cursor_position=document.cursor_position
            )
            
        if end_date <= self.start_date:
            raise ValidationError(
                message="La date de fin doit être postérieure à la date de début",
                cursor_position=document.cursor_position
            )


class FutureDateValidator(Validator):
    
    def __init__(self, format_str="%d/%m/%Y %H:%M"):

        self.format_str = format_str
    
    def validate(self, document):

        date_str = document.text
        
        if not date_str:
            raise ValidationError(
                message="La date ne peut pas être vide",
                cursor_position=document.cursor_position
            )
        
        try:
            event_date = datetime.strptime(date_str, self.format_str)
        except ValueError:
            raise ValidationError(
                message=f"Format de date invalide. Utilisez {self.format_str.replace('%d', 'JJ').replace('%m', 'MM').replace('%Y', 'AAAA').replace('%H', 'HH').replace('%M', 'MM')}",
                cursor_position=document.cursor_position
            )
            
        now = datetime.now()
        if event_date <= now:
            raise ValidationError(
                message="La date doit être dans le futur",
                cursor_position=document.cursor_position
            )


class LocationValidator(Validator):
    
    def validate(self, document):
        
        location = document.text.strip()
        
        if not location:
            raise ValidationError(
                message="Le lieu ne peut pas être vide",
                cursor_position=document.cursor_position
            )
            
        if len(location) < 3:
            raise ValidationError(
                message="Le lieu doit contenir au moins 3 caractères",
                cursor_position=document.cursor_position
            )


class AttendeesValidator(Validator):
    
    def validate(self, document):

        attendees_str = document.text.strip()
        
        if not attendees_str:
            raise ValidationError(
                message="Le nombre de participants ne peut pas être vide",
                cursor_position=document.cursor_position
            )
            
        try:
            attendees = int(attendees_str)
        except ValueError:
            raise ValidationError(
                message="Le nombre de participants doit être un nombre entier",
                cursor_position=document.cursor_position
            )
            
        if attendees < 1:
            raise ValidationError(
                message="Le nombre de participants doit être au moins de 1",
                cursor_position=document.cursor_position
            )

class PhoneNumberValidator(Validator):
    
    def validate(self, document):

        phone_number = document.text.strip()
        
        if not phone_number:
            raise ValidationError(
                message="Le numéro de téléphone ne peut pas être vide",
                cursor_position=document.cursor_position
            )
        
        if not re.match(r'^\d{10}$', phone_number):
            raise ValidationError(
                message="Le numéro de téléphone doit contenir exactement 10 chiffres",
                cursor_position=document.cursor_position
            )
