from typing import Any

from common.infrastructure.config.config import Settings
from common.infrastructure.config.database_config import DatabaseConfig
from common.infrastructure.config.logger_config import LoggerConfig
from idp.auth.infrastructure.config.auth_config import AuthConfig


class AppConfig(Settings):
    auth: AuthConfig
    db: DatabaseConfig
    logger: LoggerConfig

    def masked_dict(self) -> dict[str, Any]:
        return self.model_dump(
            mode="json",
            exclude={"db": {"db_password"}, "auth": {"secret_key", "algorithm"}},
        )
