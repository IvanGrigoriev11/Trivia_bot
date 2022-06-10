import psycopg
import typer
import os


DB_NAME = "postgres"


def main(
        dbname: str = typer.Argument(..., help="The name of the database which you are calling"),
        host: str = typer.Option(
            "localhost",
            help="""
            Enter host IP. If you skip this parameter, the localhost to be chosen automatically.
            """
        ),
        port: int = typer.Option(
            5432,
            help="""
            Type the number of port. 5432 is set by default.
            """
        )
):

    if dbname == DB_NAME:
        user = os.environ["USER_FOR_DATABASE"]
        password = os.environ["PASSWORD_FOR_DB"]

        # Connect to an existing database
        connection = psycopg.connect(
            host=host,
            dbname=dbname,
            user=user,
            password=password,
            port=port)
        print("All were done")
        connection.close()
    else:
        print("Database not found")


if __name__ == "__main__":
    typer.run(main)
