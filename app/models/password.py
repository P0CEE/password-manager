from app import db
from datetime import datetime, timedelta
import secrets

class Password(db.Model):
    __tablename__ = 'passwords'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    site_name = db.Column(db.String(255), nullable=False)
    username = db.Column(db.String(255), nullable=True)
    encrypted_password = db.Column(db.Text, nullable=False)
    encryption_iv = db.Column(db.Text, nullable=False)
    encryption_key = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = db.relationship('User', backref=db.backref('passwords', lazy=True))
    shares = db.relationship('PasswordShare', backref='password', lazy=True, cascade="all, delete-orphan")

    def __repr__(self):
        return f'<Password {self.site_name}>'


class PasswordShare(db.Model):
    __tablename__ = 'password_shares'

    id = db.Column(db.Integer, primary_key=True)
    password_id = db.Column(db.Integer, db.ForeignKey('passwords.id'), nullable=False)
    share_token = db.Column(db.String(64), nullable=False, unique=True, index=True)
    expires_at = db.Column(db.DateTime, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    @staticmethod
    def create_share(password_id, expiration_hours=24):
        """Crée un nouveau partage pour un mot de passe avec un token unique"""
        share = PasswordShare(
            password_id=password_id,
            share_token=secrets.token_urlsafe(32),  
            expires_at=datetime.utcnow() + timedelta(hours=expiration_hours)
        )
        db.session.add(share)
        db.session.commit()
        return share
    
    @staticmethod
    def get_by_token(token):
        """Récupère un partage par son token s'il est valide"""
        share = PasswordShare.query.filter_by(share_token=token).first()
        if share and share.expires_at > datetime.utcnow():
            return share
        return None

    def is_expired(self):
        """Vérifie si le partage a expiré"""
        return self.expires_at <= datetime.utcnow()
        
    def __repr__(self):
        return f'<PasswordShare {self.id}>'
