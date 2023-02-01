from fastapi import Depends, HTTPException, APIRouter
from pydantic import BaseModel
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm


router = APIRouter()

oauth2 = OAuth2PasswordBearer(tokenUrl='login')

#Modelos
class User(BaseModel):
  username: str
  name: str
  lastname: str
  disabled: bool

class UserDB(User):
  password: str


#Base de Datos
users_db = {
  'pepesancho': {
    'username': 'pepesancho',
    'name': 'pepe',
    'lastname': 'sancho',
    'disabled': False,
    'password': '123456'
  },
  'cosmefulanito': {
    'username': 'cosmefulanito',
    'name': 'cosme',
    'lastname': 'fulanito',
    'disabled': True,
    'password': '654321'
  }
}

#Algoritmos
def search_user(username: str):
  if username in users_db:
    return User(**users_db[username])

def search_user_db(username: str):
  if username in users_db:
    return UserDB(**users_db[username])

async def current_user(token: str = Depends(oauth2)):
  user = search_user(token)
  if not user:
    raise HTTPException(status_code=401, detail='Autorizacion invalida.', headers={'WWW-Authenticate': 'Bearer'})

  if user.disabled:
    raise HTTPException(status_code=400, detail='Usuario inactivo.')

  return user


#CRUD
@router.post('/login')
async def login(form: OAuth2PasswordRequestForm = Depends()):
  user_db = users_db.get(form.username)
  if not user_db:
    raise HTTPException(status_code=400, detail='Usuario incorrecto!')
  
  user = search_user_db(form.username)
  if not form.password == user.password:
    raise HTTPException(status_code=400, detail='Contraseña incorrecta!')

  return {'access_token': user.username, 'token_type': 'bearer'}

@router.get('/users/me')
async def me(user: User = Depends(current_user)):
  return user

