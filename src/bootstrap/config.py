from common.infrastructure.config.config import Settings
from common.infrastructure.config.database_config import DatabaseConfig
from common.infrastructure.config.logger_config import LoggerConfig
from idp.auth.infrastructure.config.auth_config import AuthConfig


class AppConfig(Settings):
    auth: AuthConfig
    db: DatabaseConfig
    logger: LoggerConfig
