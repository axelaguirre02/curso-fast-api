from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi import HTTPException, Depends, APIRouter
from passlib.context import CryptContext
from datetime import datetime, timedelta
from pydantic import BaseModel
from jose import jwt, JWTError


ALGORITHM = 'HS256'
ACCESS_TOKEN_DURATION = 1
SECRET_KEY = '09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7'

router = APIRouter()

oauth2 = OAuth2PasswordBearer(tokenUrl='login-jwt')

crypt = CryptContext(schemes=['bcrypt'])


class User(BaseModel):
  username: str
  name: str
  last_name: str
  disabled: bool

class UserDB(User):
  password: str


users_db = {
  'pepesancho': {
    'username': 'pepesancho',
    'name': 'pepe',
    'last_name': 'sancho',
    'disabled': True,
    'password': '123456'
  },
  'cosmefulanito': {
    'username': 'cosmefulanito',
    'name': 'cosme',
    'last_name': 'fulanito',
    'disabled': False,
    'password': '654321'
  }
}

def search_user(username: str):
  if username in users_db:
    return User(**users_db[username])

def search_user_db(username: str):
  if username in users_db:
    return UserDB(**users_db[username])

async def auth_user(token: str = Depends(oauth2)): 

  exception = HTTPException(status_code=401, detail="Datos de autenticacion invalidos.", headers={'WWW-Authenticate': 'Bearer'})

  try:
    username = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM]).get('sub')
    if username is None:
      raise exception

  except JWTError:    
    raise exception
    
  return search_user(username)
    
async def current_user(user: User = Depends(auth_user)):
  if user.disabled:
    raise HTTPException(status_code= 400, detail="Usuario inactivo.")

  return user


@router.post('/login-jwt')
async def login_jwt(form: OAuth2PasswordRequestForm = Depends()):
  user_db = users_db.get(form.username)
  if not user_db:
    raise HTTPException(status_code=400, detail='Usuario incorrecto.')

  user = search_user_db(form.username)

  if not crypt.verify(form.password, user.password):
    raise HTTPException(status_code=400, detail='Contraseña incorrecta.')


  access_token = {'sub': user.username, 'exp': datetime.now() + timedelta(minutes=ACCESS_TOKEN_DURATION)} 


  return {'access_token': jwt.encode(access_token, SECRET_KEY, algorithm=ALGORITHM), 'token_type': 'bearer'}


@router.get('/users/me')
async def me(user: User = Depends(current_user)):
  return user

