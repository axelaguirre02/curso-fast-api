from fastapi import APIRouter, HTTPException
from db.schemas.user import user_schema, users_schema
from db.models.user import User
from db.client import client
from bson import ObjectId


router = APIRouter(prefix='/users', tags=['users'], responses={404: {'message': 'No se ha encontrado.'}})


#CRUD
@router.get('/', response_model=list[User]) 
async def users():
  return users_schema(client.local.users.find()) 

@router.get('/{id}') #Path
async def user(id: str):
  return search_user('_id', ObjectId(id)) 

@router.get('/') #Query
async def user(id: str):
  return search_user('_id', ObjectId(id))

@router.post('/', response_model=User, status_code=201)
async def user(user: User):
  if type(search_user('email', user.email)) == User:
    raise HTTPException(status_code= 404, detail='El usuario ya existe.') 

  user_dict = dict(user)
  del user_dict['id']

  id = client.local.users.insert_one(user_dict).inserted_id

  new_user = user_schema(client.local.users.find_one({'_id': id})) 

  return User(**new_user)
  
@router.put('/', response_model=User)
async def user(user: User):

  try:
    user_dict = dict(user)
    del user_dict['id']

    client.local.users.find_one_and_replace({'_id': ObjectId(user.id)}, user_dict)
  except:
    return {'error': 'No se ha actualizado el usuario correctamente.'}

  return search_user('_id', ObjectId(user.id))

@router.delete('/{id}', status_code=204)
async def user(id: str): 
  
  found = client.local.users.find_one_and_delete({'_id': ObjectId(id)}) 
 
  if not found:
    return {'error': 'No se pudo borrar al usuario, corrobore que el usuario exista o que la informacion sea la correcta.'}


#Algoritmos
def search_user(field: str, key):
  try:
    user = client.local.users.find_one({field: key})
    return User(**user_schema(user)) 
  except:
    return {'error': 'El email o nombre de usuario ya esta en uso.'}

