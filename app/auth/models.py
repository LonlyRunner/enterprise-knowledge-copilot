from dataclasses import dataclass


@dataclass
class User:

    id:str

    username:str

    password_hash:str

    tenant_id: str

    role: str = "employee"
