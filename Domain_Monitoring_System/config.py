import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'mysecretkey')  # Change for production
    SESSION_TYPE = 'filesystem'
    SESSION_PERMANENT = False
