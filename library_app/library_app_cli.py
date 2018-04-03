import click

from .config import Config

config = click.make_pass_decorator(Config, ensure=True)


@click.group(cls=AliasHandler)
@click.option('--verbose', '-v', is_flag=True, help='Alias for --debug.')
@click.option('--debug', '-d', is_flag=True, help='Print log messages.')
@click.pass_context
@config
def cli(config, verbose, debug):
    """
    RoseCloud Workspace Management CLI
    """
    config._verbose = verbose or debug


@cli.command()
@click.argument('directory', type=click.Path(), default='.')
@config
def init(config, directory):
    """
    Initialize a RoseCloud Workspace.

    :param config: Config object passed in by Click\n
    :param directory: Path to directory to initialize\n
    :return: None
    """
    from .init.initializer import Initializer
    initializer = Initializer(config, directory)
    initializer.execute()


@cli.command()
@click.argument('directory', type=click.Path(), default='.')
@config
def build(config, directory):
    """
    Build the RoseCloud Workspace.
    This will create all directories listed under the `workspaces` key.
    It will name each directory using the `name` key and copy the directory
    under the `path` argument. These directories will be listed as Gitlab subgroups.

    It will create directories listed under the `resources` key.
    These directories will do the same thing as above; however, they will
    be listed as repositories rather than Gitlab subgroups.

    :param config: Config object passed in by Click\n
    :param directory: Path to directory to build\n
    :return: None
    """
    from .builder.builder import Builder
    builder = Builder(config, directory)
    builder.execute()


@cli.command()
@click.argument('directory', type=click.Path(), default='.')
@config
def deploy(config, directory):
    """
    Deploy the RoseCloud Workspace to Gitlab.
    This creates the group on gitlab. All workspaces are subgroups.
    All directories under a workspace is a repository. Resources is a repository.

    :param config: Config object passed in by Click\n
    :param directory: Path to directory to deploy\n
    :return: None
    """
    from .deploy.deployer import Deployer
    deployer = Deployer(config, directory)
    deployer.execute()


@cli.command()
@click.argument('restore_directory', type=click.Path(exists=True))
@click.argument('group_name')
@click.argument('prefixes', nargs=-1, required=False)
@click.option('--token', '-t', required=True, help='Gitlab token.')
@click.option('--user', '-u', help='Username of a particular user to restore.', default=None)
@click.option('--stage-mode', '-s', is_flag=True, help='Run this ada-stage.')
@config
def restore(config, restore_directory, group_name, prefixes, token, user, stage_mode):
    """
    Admin restore utility.

    It will attempt to recreate the repository from the backups as a
    subrepository of the group. The group_name specified must be exactly
    the way it is on Gitlab.

    If prefixes are provided, the client will only consider repository
    to restore matching the list of prefixes.

    The token must be specified as this does not assume to be reading from
    an rc workspace with a `roseconfig.json`.

    If a user is specified, then only the repositories AFTER prefixes filtering
    (if any) matching that user will be restored. If this is not specified,
    all repositories found will be restored AFTER prefixes filtering (if any).

    This assumes that all projects follow RoseCloud convention of
    `repo_type-username.git`. It also assumes the user running this is the master
    of the group. Otherwise, no projects will be pushed as the user does not have
    write access.

    restore_directory has the following structure:
    restore_directory
        assignment1-all.git
        assignment1-dus.git
        assignment1-lamd.git
        assignment1-mikhaidn.git
        assignment1-testcsse-1.git
        assignment1-testcsse-2.git
        assignment1-testcsse-3.git
        assignment1-testcsse-4.git
        assignment1-zhangq2.git

    where the `.git` are the repository's `.git` configuration directory.

    :param config: Config object passed in by Click\n
    :param restore_directory: Directory containing the unzip files from backup\n
    :param group_name: The Gitlab group name needing to be restored\n
    :param prefixes: prefixes used to match\n
    :param token: Token to authenticate Gitlab access\n
    :param user: specific user to restore\n
    :param stage_mode: Run this one ada-stage\n
    :return: None
    """
    from .restore.restorer import Restorer
    restorer = Restorer(config, restore_directory, group_name, prefixes, token, user, stage_mode)
    restorer.execute()


@cli.command()
@click.argument('source_file')
@click.argument('destination_directories', nargs=-1, required=True)
@click.option('--name', '-n', help='Copy the file with a different name into the destination directory.')
@click.option('--force', '-f', is_flag=True, help='Copy file ignoring any potential conflicts.')
@click.option('--interactive', '-i', is_flag=True, help='Prompt when attempting to overwrite existing files.')
@config
def copy(config, source_file, destination_directories, name, force, interactive):
    """
    RoseCloud copy utility.

    Copy a source_file into a destination_directories.

    If neither the force nor interactive flag are enabled, it will
    copy all files in which there are no conflicts in name but will
    intentionally fail for those with conflict. If both are enabled,
    the force flag is effectively ignored. If the force flag is enabled,
    the CLI will override all files with conflicts without prompt.
    If the interactive flag is enabled, the CLI will prompt the user
    for each file conflict.

    :param config: Config object passed in by Click\n
    :param source_file: File to copy\n
    :param destination_directories: Directories to copy file to\n
    :param name: Name to save the file in the destination directory\n
    :param force: Flag to force copy all files regardless of conflicts\n
    :param interactive: Flag to interactively copy conflicting files. Has precedence over force\n
    :return: None
    """
    from .utils.copier import Copier
    copier = Copier(config, source_file, destination_directories, name, force, interactive)
    copier.execute()


@cli.command()
@click.argument('file_pattern')
@click.argument('search_directories', nargs=-1, required=True)
@click.option('--force', '-f', is_flag=True, help='Copy file ignoring any potential conflicts.')
@click.option('--interactive', '-i', is_flag=True, help='Prompt when attempting to overwrite existing files.')
@config
def remove(config, file_pattern, search_directories, force, interactive):
    """
    RoseCloud remove utility.

    Remove a file_pattern in a given set of directories. It will recursively
    search the search_directories for any files or directories that matches.

    If neither the force nor interactive flag are enabled, it will do a
    dry-run and only log what it matches. If both are enabled, the
    force flag is effectively ignored. If the force is enabled, all files will
    be removed without prompt. If the interactive flag is enabled, all files
    matched will prompt the user for confirmation before performing any actions.

    :param config: Config object passed in by Click\n
    :param file_pattern: File pattern to delete\n
    :param search_directories: Directories to scan for file_pattern\n
    :param force: Flag to force delete all matches\n
    :param interactive: Flag to interactively delete all matches. Has precedence over force\n
    :return: None
    """
    from .utils.remover import Remover
    remover = Remover(config, file_pattern, search_directories, force, interactive)
    remover.execute()


@cli.command()
@click.argument('directory', default='.')
@config
def ping(config, directory):
    """
    RoseCloud Ping Utility.

    This relies on the `roseconfig.json` with `gitlab.url` field.
    It will ping this url and print a success message if 200 (ok)
    and an error message if anything else.

    :param config: Config object passed in by Click\n
    :param directory: Path to directory rc workspace\n
    :return: None
    """
    from .utils.pinger import Pinger
    pinger = Pinger(config, directory)
    pinger.execute()


cli.add_command(git)


@cli.command()
@click.option('--string', default='world', help='Thing to greet')
@click.option('--repeat', default=1, type=int, help='How many times to greet')
@click.argument('out', type=click.File('w'), default='-', required=False)
@config
def say(config, string, repeat, out):
    """
    This is a help message for the cli. Only first sentence shown in `rc --help`.

    This line will be shown if user runs `rc say --help`.
    """
    if config._verbose:
        click.echo('We are in verbose mode')
    click.echo('home directory is {}'.format(config.home_directory))
    for x in range(repeat):
        click.echo('hello {}!'.format(string), file=out)