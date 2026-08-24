import jwt
from datetime import datetime,timedelta



class JWTService:


    def __init__(
        self,
        secret:str,
    ):

        self.secret=secret



    def create_token(
        self,
        user_id:str,
    ):


        payload={

            "sub":
            user_id,


            "exp":
            datetime.utcnow()
            +
            timedelta(hours=2)

        }


        return jwt.encode(
            payload,
            self.secret,
            algorithm="HS256"
        )