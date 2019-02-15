import argparse
import logging
import sys
from typing import TYPE_CHECKING

from grouper import __version__
from grouper.ctl import dump_sql, group, oneoff, service_account, shell, sync_db, user, user_proxy
from grouper.ctl.base import CtlCommand
from grouper.ctl.permission import PermissionCommand  # noqa: F401
from grouper.plugin import initialize_plugins
from grouper.plugin.exceptions import PluginsDirectoryDoesNotExist
from grouper.settings import default_settings_path, settings
from grouper.util import get_loglevel

if TYPE_CHECKING:
    from grouper.models.base.session import Session
    from typing import Dict, List, Optional, Type

sa_log = logging.getLogger("sqlalchemy.engine.base.Engine")


def main(sys_argv=sys.argv, start_config_thread=True, session=None):
    # type: (List[str], bool, Optional[Session]) -> None
    description_msg = "Grouper Control"
    parser = argparse.ArgumentParser(description=description_msg)

    parser.add_argument(
        "-c", "--config", default=default_settings_path(), help="Path to config file."
    )
    parser.add_argument(
        "-v", "--verbose", action="count", default=0, help="Increase logging verbosity."
    )
    parser.add_argument(
        "-q", "--quiet", action="count", default=0, help="Decrease logging verbosity."
    )
    parser.add_argument(
        "-V",
        "--version",
        action="version",
        version="%%(prog)s %s" % __version__,
        help="Display version information.",
    )

    subparsers = parser.add_subparsers(dest="command")

    for subcommand_module in [
        dump_sql,
        group,
        oneoff,
        service_account,
        shell,
        sync_db,
        user,
        user_proxy,
    ]:
        subcommand_module.add_parser(subparsers)  # type: ignore

    subcommand = {}  # type: Dict[str, Type[CtlCommand]]
    for subcommand_class in CtlCommand.__subclasses__():
        subcommand_name = subcommand_class.add_parser(subparsers)
        # https://github.com/python/mypy/issues/4717
        subcommand[subcommand_name] = subcommand_class  # type: ignore

    args = parser.parse_args(sys_argv[1:])

    if start_config_thread:
        settings.update_from_config(args.config)
        settings.start_config_thread(args.config)

    log_level = get_loglevel(args, base=logging.INFO)
    logging.basicConfig(level=log_level, format=settings.log_format)

    try:
        initialize_plugins(settings.plugin_dirs, settings.plugin_module_paths, "grouper-ctl")
    except PluginsDirectoryDoesNotExist as e:
        logging.fatal("Plugin directory does not exist: {}".format(e))
        sys.exit(1)

    if log_level < 0:
        sa_log.setLevel(logging.INFO)

    # Old-style subcommands store a func in callable when setting up their arguments.  New-style
    # subcommands initialized their arguments above and map a subcommand name to a class.
    if getattr(args, "func", None):
        args.func(args)
    else:
        subcommand[args.command](session).run(args)
