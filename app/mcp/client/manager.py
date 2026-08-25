from app.mcp.client.session import (
    MCPConnection,
)



class MCPClientManager:


    def __init__(self):

        self.clients = {}



    def register(
        self,
        name: str,
        client: MCPConnection,
    ):

        self.clients[name] = client



    def get(
        self,
        name: str,
    ):

        return self.clients[name]