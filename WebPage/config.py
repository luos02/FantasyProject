import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'una_clave_secreta_muy_segura' #This was done by chat gpt, don't judge me.
#                                                                                atte: Luis <3