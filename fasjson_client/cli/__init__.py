import logging
from functools import partial
from importlib import import_module

import click


DEFAULT_FASJSON_URL = "https://fasjson.os.fedoraproject.org"

log = logging.getLogger(__name__)


def _setup_logging(verbose, quiet):
    """Setup this script's output."""
    logging.basicConfig(level=logging.WARNING, format="%(message)s")
    if verbose:
        loglevel = logging.DEBUG
    elif quiet:
        loglevel = logging.WARNING
    else:
        loglevel = logging.INFO
    log.setLevel(loglevel)


def _get_import_error_handler(e):
    def _raise_error(msg):
        raise click.ClickException(msg)

    func = partial(
        _raise_error, "This command needs additional dependencies: {}".format(e)
    )
    func.__doc__ = "Unavailable: {}".format(e)
    return func


def _register_subcommand(group, module_name, command_name=None):
    command_name = command_name or module_name.replace("_", "-")
    try:
        module = import_module("fasjson_client.cli.{}".format(module_name))
        command = getattr(module, module_name)
    except ImportError as e:
        command = _get_import_error_handler(e)
    group.command(command_name)(command)


@click.group()
@click.option(
    "--url", default=DEFAULT_FASJSON_URL, help="URL to the FASJSON instance",
)
@click.option("--verbose", is_flag=True, default=False, help="Print more information")
@click.option("--quiet", is_flag=True, default=False, help="Print less information")
@click.pass_context
def cli(ctx, url, verbose, quiet):
    """Make API calls to FASJSON from the command line."""
    ctx.ensure_object(dict)
    ctx.obj["url"] = url

    if verbose and quiet:
        raise click.UsageError("You can't have --verbose and --quiet at the same time.")
    _setup_logging(verbose, quiet)


_register_subcommand(cli, "get_cert")


if __name__ == "__main__":
    cli()