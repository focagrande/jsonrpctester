import os
import json
import random

import click
import requests

from pygments import highlight
from pygments.lexers import JsonLexer
from pygments.formatters import TerminalFormatter


class Repo(object):
    def __init__(self, repo_file=None):
        self.repo_file = repo_file

        with open(repo_file) as f:
            data = f.read()        
            self.repo = json.loads(data)
            
def prepare_request(payload):

    return {
        'jsonrpc': '2.0',
        'id': random.randint(0, 1000),
        'method': payload['method'],
        'params': payload['params']
    }

def pygmentize(s):
    return highlight(json.dumps(s, indent=2), JsonLexer(), TerminalFormatter())

@click.pass_obj
def listkeys(repo, object_type):
    for k in repo.repo[object_type].keys():
        click.echo(k)


@click.group()
@click.option('--repo-file', envvar='REPO_FILE', default='./jsonrpcrepo.json', help='Path to repository')
@click.pass_context
def cli(ctx, repo_file):
    ctx.obj = Repo(repo_file)


@cli.command()
@click.pass_obj
def targets(repo):
    """List targets"""   
    listkeys('targets')


@cli.command()
@click.pass_obj
def payloads(repo):
    """List payloads"""
    listkeys('payloads')


@cli.command()
@click.argument('object-type', type=click.Choice(['targets', 'payloads']), required=True)
@click.argument('object-name', required=True)
@click.pass_obj
def show(repo, object_type, object_name):
    """Display definiton of target or payload"""

    try:
        data = repo.repo[object_type][object_name]
    except KeyError:
        click.echo('{} not found in {}'.format(object_name, object_type))
    else:
        click.echo(pygmentize(data))


@cli.command()
@click.option('--verbose', is_flag=True, help='Display request')
@click.argument('target', required=True)
@click.argument('payload', required=True)
@click.pass_obj
def call(repo, verbose, target, payload):
    """Call target with given payload"""

    try:
        url = repo.repo['targets'][target]['url']
        headers = repo.repo['targets'][target]['headers']
    except KeyError:
        click.echo('{} not found in targets'.format(target))
        return None

    try:
        data = prepare_request(repo.repo['payloads'][payload])
    except KeyError:
        click.echo('{} not found in payloads'.format(payload))
        return None

    if verbose:
        click.echo('REQUEST>>>')
        click.echo(pygmentize(data))

    r = requests.post(url, data=json.dumps(data), headers=headers)
    click.echo('<<<RESPONSE:')
    click.echo(pygmentize(r.json()))


if __name__ == '__main__':
    cli()