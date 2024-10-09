# vim: tw=100 foldmethod=indent

import logging
import os
from dataclasses import dataclass, fields, field
from typing import List, Optional, Dict
from typing import Optional, List
from pathlib import Path
from configparser import ConfigParser
from configparser import ExtendedInterpolation
from alise.parse_args import args

logger = logging.getLogger(__name__)


class MyConfigParser(ConfigParser):
    def getlist(self, section, option, fallback=None):
        if not fallback:
            value = self.get(section, option)
        else:
            value = self.get(section, option, fallback=fallback)
        lines = list(filter(None, (x.strip() for x in value.splitlines())))
        rv = []
        for line in lines:
            #  logger.info(F"line: {l}")
            for e in line.split(","):
                f = e.rstrip(" ").lstrip(" ")
                rv.append(f)
        return rv


def to_bool(bool_str):
    """Convert a string to bool.
    Raise an Exception if the string cannot be converted.
    """
    if bool_str.lower() in ["true", "yes", "yes, do as i say!"]:
        return True
    if bool_str.lower() in ["false", "no"]:
        return False
    # FIXME: consider defining and using your own exceptions
    # pylint: disable = broad-exception-raised, raise-missing-from
    raise Exception(f"Error converting to bool: unrecognised boolean value {bool_str}.")


def to_int(int_str):
    """Convert a string to int.
    Raise an Exception if the string cannot be converted.
    """
    try:
        return int(int_str)
    except ValueError:
        # FIXME: consider defining and using your own exceptions
        # pylint: disable = broad-exception-raised, raise-missing-from
        raise Exception(f"Error converting to int: unrecognised integer value {int_str}.")


def to_list(list_str):
    """Convert a string containing comma-separated strings to list of strings.
    Raise an Exception if the string cannot be converted.
    """
    try:
        return list(set(list_str.split()))
    except ValueError:
        # FIXME: consider defining and using your own exceptions
        # pylint: disable = broad-exception-raised, raise-missing-from
        raise Exception(f"Error converting to list: unrecognised list value {list_str}.")


def reload_parser():
    """Reload configuration from disk.

    Config locations, by priority (first one wins)
    """
    files = []

    # basename = os.path.basename(sys.argv[0]).rstrip(".py")
    basename = "alise"
    dirname = os.path.dirname(__file__)

    # If the program has arguments with a config: prefer it:
    try:
        config_from_cmdline = args.get("config")
        if config_from_cmdline is not None:
            files += [Path()]
    except AttributeError:
        pass

    #  # If the caller of the library has provided a configfile: prefer it:
    #  logger.debug(f"Files: {files}")
    #  try:
    #      globalconf_conf_file = Path(globalconfig.config["CONFIGFILE"])
    #      logger.debug(
    #          f"Trying config of globalconfig: {globalconfig.config['']}"
    #      )
    #      if globalconf_conf_file.exists():
    #          files.insert(0, globalconf_conf_file)
    #  except KeyError:
    #      pass
    #
    files += [
        Path(f"./.config/{basename}.conf"),
        Path(f"/etc/{basename}.conf"),
        Path(f"/etc/{basename}/{basename}.conf"),
        Path(f"{dirname}/{basename}.conf"),
    ]

    config_loaded = False
    cp = ConfigParser(interpolation=ExtendedInterpolation())
    for f in files:
        # print(F"tryng to load config: {f}")
        try:
            if f.exists():
                logger.info("Using this config file: %s", f)
                cp.read(f)
                config_loaded = True
                break
        except PermissionError:
            pass
    if not config_loaded:
        filelist = [str(f) for f in files]
        filestring = "\n    ".join(filelist)
        logger.warning("Warning: Could not read any config file from \n    %s", filestring)
        # sys.exit(4)
    return cp


#  @dataclass
#  class ConfigListOfSections:
#      @classmethod
#      def load(cls, config: ConfigParser):
#          """Loads all config sub-sections that start with the given section name"""
#          sections = {}
#          for field in fields(cls):
#              try:
#                  field_type = field.type.__args__[0]  # assume Optional[ConfigSection]
#              except:
#                  field_type = field.type
#              field_name = field.name
#              subsection = field_type.__section__name__()
#              if subsection in config:
#                  sections[field_name] = field_type.load(config)
#              else:
#                  logger.debug(f"Missing config section [{subsection}].")
#          return cls(**sections)
#
#      def to_dict(self) -> dict:
#          """Converts the config to a dict"""
#          return {
#              field.name: getattr(self, field.name).to_dict()
#              for field in fields(self)
#              if field is not None
#          }
#
#
#  @dataclass
#  class ConfigBackends(ConfigListOfSections):
#      """Collection of config sections for all backends"""
#
#      local_unix: ConfigLocalUnix = field(default_factory=ConfigLocalUnix)
#      ldap: ConfigLdap = field(default_factory=ConfigLdap)
#      bwidm: ConfigBwIdm = field(default_factory=ConfigBwIdm)


@dataclass
class ConfigSection:
    @classmethod
    def __section__name__(cls) -> str:
        return "DEFAULT"

    @classmethod
    def load(cls, config: ConfigParser, section_name: Optional[str] = None):
        """Sets only the fields that are present in the config file"""
        try:
            if section_name is None:
                section_name = cls.__section__name__()
            field_names = set(f.name for f in fields(cls))
            return cls(**{k: v for k, v in {**config[section_name]}.items() if k in field_names})
        except KeyError:
            # logger.debug(
            #     "Missing config section %s, using default values.", cls.__section__name__()
            # )
            return cls()

    def __post_init__(self):
        """Converts some of the fields to the correct type"""
        for field in fields(self):
            value = getattr(self, field.name)
            if value is None:
                continue
            field_type = field.type
            if hasattr(field.type, "__module__") and field.type.__module__ == "typing":
                if field.type.__str__().startswith(
                    "typing.Optional"
                ) or field.type.__str__().startswith("typing.Union"):
                    field_type = field.type.__args__[0]  # pyright: ignore
                elif field.type.__str__().startswith("typing.List"):
                    field_type = list  # treat as a list
                else:
                    return  # no conversion
            # if the field does not have the hinted type, convert it if possible
            if not isinstance(value, field_type):  # pyright: ignore
                if field_type == int:
                    setattr(self, field.name, to_int(value))
                if field_type == bool:
                    setattr(self, field.name, to_bool(value))
                if field_type in [List, List[str], list]:
                    setattr(self, field.name, to_list(value))

    def to_dict(self) -> dict:
        """Converts the config to a dict"""
        return {field.name: getattr(self, field.name) for field in fields(self)}


@dataclass
class ConfigTest(ConfigSection):
    """Config section for messages. Selects which information will be logged"""

    your_config: Optional[str] = None
    lists_example: list = field(default_factory=list)

    @classmethod
    def __section__name__(cls):  # pyright: ignore[reportIncompatibleMethodOverride]
        return "test"


@dataclass
class ConfigMessages(ConfigSection):
    """Config section for messages. Selects which information will be logged"""

    log_file: Optional[str] = None
    log_level: Optional[str] = None
    log_to_console: str = ""
    log_name_changes: bool = True
    log_primary_group_definition: bool = True
    log_username_creation: bool = False

    @classmethod
    def __section__name__(cls):  # pyright: ignore[reportIncompatibleMethodOverride]
        return "messages"


@dataclass
class ConfigOIDC(ConfigSection):
    """Config section for OIDC. Selects which information will be logged"""

    oidc_config: Optional[str] = ".env"

    @classmethod
    def __section__name__(cls):  # pyright: ignore[reportIncompatibleMethodOverride]
        return "oidc"


@dataclass
class ConfigDatabase(ConfigSection):
    """Config section for database settings"""

    db_name: str = "alise"

    @classmethod
    def __section__name__(cls):  # pyright: ignore[reportIncompatibleMethodOverride]
        return "database"


@dataclass
class ConfigOPConf(ConfigSection):
    """Config section for authorisation of one OP."""

    op_url: str = ""
    client_id: str = ""
    client_secret: str = ""
    claims: list = field(default_factory=list)
    internal: bool = False
    scopes: list = field(default_factory=list)
    username_claim: str = "sub"

    def get_info(self) -> dict:
        """Returns a dict with the info for this OP"""
        op_info = {
            "op_url": self.op_url,
            "scopes": self.scopes,
        }
        if self.audience and self.audience != "":
            op_info["audience"] = self.audience
        return op_info


@dataclass
class ConfigAuth:
    """All authorisation configs for all supported OPs."""

    all_op_authz: Dict[str, ConfigOPConf] = field(default_factory=dict)

    @classmethod
    def load(cls, config: ConfigParser):
        """Loads all config sub-sections that start with the given section name"""
        subsection_prefix = "auth"
        # all_op_authz = {}
        cls.all_op_authz = {}
        for section in config.sections():
            if section.startswith(f"{subsection_prefix}."):
                config_name = section.replace(subsection_prefix + ".", "")
                op_config = ConfigOPConf.load(config, section_name=section)
                cls.all_op_authz[config_name] = op_config
        return cls(cls.all_op_authz)

    def to_dict(self) -> dict:
        """Converts the config to a dict"""
        return {k: v.to_dict() for k, v in self.all_op_authz.items()}

    def get_op_names(self) -> List:
        return self.all_op_authz.keys()

    def get_op_config(self, config_name) -> ConfigOPConf:
        """Returns the ConfigOPConf object for OP given in user_infos.

        Args:
            user_infos: (flaat) UserInfo object

        Returns:
            Optional[OPAuthZ]: OPAuthZ object
        """
        return self.all_op_authz.get(config_name)


@dataclass
class Configuration:
    """All configuration settings for the alise"""

    messages: ConfigMessages = field(default_factory=ConfigMessages)
    oidc: ConfigOIDC = field(default_factory=ConfigOIDC)
    database: ConfigDatabase = field(default_factory=ConfigDatabase)
    test: ConfigTest = field(default_factory=ConfigTest)
    auth: ConfigAuth = field(default_factory=ConfigAuth)

    @classmethod
    def load(cls, config: ConfigParser):
        """Loads all config settings from the given config parser"""
        return cls(**{f.name: f.type.load(config) for f in fields(cls)})


# Load config on import
CONFIG = Configuration.load(reload_parser())
