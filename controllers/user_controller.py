from services.user_service import UserService
from flask import Request,Response
import json

class UserController:

    @classmethod
    def get_user(cls,request:Request):
        user_id= request.args.get('line_user_id')
        user = UserService.get_user(user_id)
        return user.to_dict()
