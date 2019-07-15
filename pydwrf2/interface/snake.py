import click
import os
    
@click.group()
def cli():
    pass

def path(name):
    module_path = os.path.dirname(__file__)
    paths = dict(config="snake/config.yaml",
                 Snakefile="snake/Snakefile")
    return os.path.join(module_path, paths[name])

@cli.command()
def file():
    print(path("Snakefile"))
    
@cli.command()
def config():
    print(path("config"))

if __name__=="__main__":
    cli()