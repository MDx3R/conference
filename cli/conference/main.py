from bootstrap.config import AppConfig
from bootstrap.utils import log_config
from common.infrastructure.app.app import App
from common.infrastructure.database.sqlalchemy.database import Database
from common.infrastructure.di.container.container import CommonContainer
from common.infrastructure.logger.logging.logger_factory import LoggerFactory
from common.infrastructure.server.fastapi.server import FastAPIServer
from idp.auth.infrastructure.app.app import TokenApp
from idp.auth.infrastructure.di.container.container import TokenContainer
from idp.identity.infrastructure.di.container.container import IdentityContainer

from conference.conference.infrastructure.app.app import ConferenceApp
from conference.conference.infrastructure.di.container.container import (
    ConferenceContainer,
)
from conference.participant.infrastructure.app.app import ParticipantApp
from conference.participant.infrastructure.di.container.container import (
    ParticipantContainer,
)


def main() -> App:
    config = AppConfig.load()

    logger = LoggerFactory.create(None, config.env, config.logger)
    logger.info("logger initialized")

    log_config(logger, config)

    logger.info("initializing database...")
    database = Database.create(config.db, logger)
    logger.info("database initialized")

    logger.info("setting up FastAPI server...")
    server = FastAPIServer(logger)
    server.on_tear_down(database.shutdown)
    logger.info("FastAPI server setup complete")

    common_container = CommonContainer(config=config, database=database)
    uuid_generator = common_container.uuid_generator
    query_executor = common_container.query_executor
    unit_of_work = common_container.unit_of_work
    clock = common_container.clock

    identity_container = IdentityContainer(
        uuid_generator=uuid_generator,
        query_executor=query_executor,
        token_introspector=None,
    )

    token_container = TokenContainer(
        auth_config=config.auth,
        clock=clock,
        uuid_generator=uuid_generator,
        token_generator=common_container.token_generator,
        query_executor=query_executor,
        identity_repository=identity_container.identity_repository,
    )

    identity_container.token_introspector.override(token_container.token_introspector)

    conference_container = ConferenceContainer(
        uuid_generator=uuid_generator,
        query_executor=query_executor,
        unit_of_work=unit_of_work,
    )

    participant_container = ParticipantContainer(
        query_executor=query_executor,
        unit_of_work=unit_of_work,
        identity_service=identity_container.identity_service,
    )

    logger.info("building application...")

    app = App(logger, server)
    app.add_app(
        TokenApp(token_container, server),
        ConferenceApp(conference_container, server),
        ParticipantApp(participant_container, server),
    )

    app.configure()

    logger.info("application initialized")

    return app


if __name__ == "__main__":
    service = main()
    logger = service.get_logger()
    logger.info("service is starting")
    service.run()
    logger.info("service stopped")
else:
    service = main()
    logger = service.get_logger()
    logger.info("service is starting with ASGI web server")

    app = service.get_server().get_app()
