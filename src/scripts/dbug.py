import typer

from fastapi import FastAPI
from uvicorn import Config, Server


def main(
 host: str = typer.Option("localhost", help="server host"),
 port: int = typer.Option(8000, help="server port"),
):
 app = FastAPI()

 @app.get("/")
 async def run_server_mode():
     return {"message": "Hello World"}

 conf = Config(app=app, host=host, port=port, debug=True)

 server = Server(conf)
 server.run()


if __name__ == "__main__":
 typer.run(main)