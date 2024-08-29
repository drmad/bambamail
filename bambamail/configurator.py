import os, sys
import yaml
from pathlib import Path
from typing import Optional

class Configurator:
    ''' Reads a configuration yaml searching in various directories '''

    _configuration_file = None

    _CONFIG_FILE_PATHS = [
        Path(os.getcwd(), '.bambamail.yaml'),
    ]

    # Default configuration
    _default_configuration: dict = dict(
        host = (
            'Listening host address for incoming SMTP connections',
            'localhost'
        ),
        port = (
            'Listening port for incoming SMTP connections',
            10587
        ),
        maildir_path = (
            'Maildir path',
            '.Maildir',
        ),
        execute_on_receive = (
            'Program to execute when a new message are received, defined as a list.\nCase-insensitive mail headers can be used surrounding them with %\n(like "%subject%")',
            None,
        ),
        clear_maildir_on_start = (
            'Clear the Maildir directory when BambaMail starts',
            True,
        ),
        log_file = (
            "File path for saving the log. 'null' doesn't save a log file",
            None
        ),
        # No es error, necesitamos una lista acá para hackearla después.
        pid_file = [
            "File path where the process PID is stored",
            'bambamail.pid'
        ]
    )

    _configuration: dict = {}

    def __init__(self):
        # Hack: En la configuración por defecto, 'pid_file' está relativo, pero
        # no será corregido, asi que lo corregimos a mano
        self._default_configuration['pid_file'][1] = '.Maildir/bambamail.pid'

        for path in self._CONFIG_FILE_PATHS:
            if os.path.exists(path):
                self.read_from_file(path)
                break

    def read_from_file(self, configuration_file: Path | str) -> None:
        ''' Reads configuration from a YAML file '''
        self._configuration_file = configuration_file

        with open(self._configuration_file) as f:
            self._configuration = yaml.safe_load(f)

        # Modificamos los paths relativos
        if self._configuration:
            for key in 'maildir_path':
                if key in self._configuration and self._configuration[key]:
                    self._configuration[key] = self.prefix_relative_path(self._configuration[key])

            for key in 'log_path', 'pid_file':
                if key in self._configuration and self._configuration[key]:
                    print(key)
                    self._configuration[key] = self.prefix_relative_path(
                        self._configuration[key],
                        relative_to_maildir = True
                    )

    def get_configuration_file(self) -> Path | str | None:
        '''Returns the configuration file used for initialize this instance'''
        return self._configuration_file

    def prefix_relative_path (
        self,
        path: Path | str,
        relative_to_maildir: bool = False
    ) -> str | Path:
        '''Prefixes relative paths with the configuration o Maildir file path.

        If there is not a configuration file, uses CWD as base path.'''

        # Solo trabajamos con rutas relativas
        if os.path.isabs(path):
            return path

        # Si no hay un fichero de configuración, usamos su ruta, sino
        # será el CWD
        if self._configuration_file:
            base_path = os.path.dirname(self._configuration_file)
        else:
            base_path = os.getcwd()

        if relative_to_maildir:
            base_path = self.maildir_path

        return Path(base_path, path)


    def path_relative_to_configuration_file(self, path: Path | str) -> str | Path:
        '''Prefixes relative paths with the configuration file path,
        or CWD if there is none.'''

        # Solo trabajamos con rutas relativas
        if os.path.isabs(path):
            return path

        # Si no hay un fichero de configuración, usamos su ruta, sino
        # será el CWD
        if self._configuration_file:
            base_path = os.path.dirname(self._configuration_file)
        else:
            base_path = os.getcwd()

        return Path(base_path, path)

    def dump(self) -> None:
        ''' Generates a commented YAML configuration file '''
        text = []
        text.extend((
            '# Default BambaMail configuration file.',
            '',
            '# Non-absolute Maildir path is relative to config file, all other non-absolute',
            '# paths are relative to Maildir.',
            ''
        ))

        for variable, info in self._default_configuration.items():
            if '\n' in info[0]:
                for line in info[0].split('\n'):
                    text.append('# ' + line)
            else:
                text.append('# ' + info[0])

            text.append(yaml.dump({variable: info[1]}))

        print ('\n'.join(text))

    def __getattr__(self, name):
        if name in self._configuration:
            return self._configuration[name]

        if name in self._default_configuration:
            return self._default_configuration[name][1]

        raise AttributeError(f"Unknow '{name}' configuration attribute")
