from typing import Any

from dependency_injector import containers, providers
from idp.identity.application.services.identity_service import IdentityService
from idp.identity.application.usecases.command.create_identity_use_case import (
    CreateIdentityUseCase,
)
from idp.identity.domain.factories.identity_factory import IdentityFactory
from idp.identity.infrastructure.database.postgres.sqlalchemy.repositories.identity_repository import (
    IdentityRepository,
)


class IdentityContainer(containers.DeclarativeContainer):
    uuid_generator: providers.Dependency[Any] = providers.Dependency()
    query_executor: providers.Dependency[Any] = providers.Dependency()
    password_hasher: providers.Dependency[Any] = providers.Dependency()

    identity_factory = providers.Singleton(IdentityFactory, uuid_generator)
    identity_repository = providers.Singleton(IdentityRepository, query_executor)

    identity_service = providers.Singleton(
        IdentityService,
        identity_repository=identity_repository,
        identity_factory=identity_factory,
        password_hasher=password_hasher,
    )
    create_identity_use_case = providers.Singleton(
        CreateIdentityUseCase, identity_service
    )
