from typing import List
from typing import Optional
import html
from fastapi import Request


class LoginForm:
    def __init__(self, request: Request):
        self.request: Request = request
        self.errors: List = []
        self.username: Optional[str]
        self.password: Optional[str]

    async def load_data(self):
        form = await self.request.form()
        self.username = form.get("username")
        if self.username is not None:
            self.username = html.escape(form.get("username"))
        self.password = form.get("password")
        if self.password is not None:
            self.password = html.escape(form.get("password"))
        ##print(" user name "+self.username+ " contraseña: "+self.password)
        
    async def is_valid(self):
        if not self.username:
            self.errors.append("Usuario es requerido")
        if not self.password or not len(self.password) >= 4:
            self.errors.append("Una contraseña valida es requerida")
        if not self.errors:
            return True
        return False
