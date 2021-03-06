from typing import TYPE_CHECKING

from grouper.entities.pagination import PaginatedList
from grouper.entities.permission import Permission, PermissionNotFoundException
from grouper.models.permission import Permission as SQLPermission
from grouper.repositories.interfaces import PermissionRepository
from grouper.usecases.list_permissions import ListPermissionsSortKey

if TYPE_CHECKING:
    from grouper.entities.pagination import Pagination
    from grouper.graph import GroupGraph
    from grouper.models.base.session import Session
    from typing import Optional


class GraphPermissionRepository(PermissionRepository):
    """Graph-aware storage layer for permissions."""

    # Mapping from ListPermissionsSortKey to the name of an attribute on the PermissionTuple
    # returned by get_permissions() on the graph.
    SORT_FIELD = {ListPermissionsSortKey.NAME: "name", ListPermissionsSortKey.DATE: "created_on"}

    def __init__(self, graph, repository):
        # type: (GroupGraph, PermissionRepository) -> None
        self.graph = graph
        self.repository = repository

    def get_permission(self, name):
        # type: (str) -> Optional[Permission]
        return self.repository.get_permission(name)

    def disable_permission(self, name):
        # type: (str) -> None
        self.repository.disable_permission(name)

    def list_permissions(self, pagination, audited_only):
        # type: (Pagination[ListPermissionsSortKey], bool) -> PaginatedList[Permission]
        perm_tuples = self.graph.get_permissions(audited=audited_only)

        # Optionally sort.
        if pagination.sort_key != ListPermissionsSortKey.NONE:
            perm_tuples = sorted(
                perm_tuples,
                key=lambda p: getattr(p, self.SORT_FIELD[pagination.sort_key]),
                reverse=pagination.reverse_sort,
            )

        # Find the total length and then optionally slice.
        total = len(perm_tuples)
        if pagination.limit:
            perm_tuples = perm_tuples[pagination.offset : pagination.offset + pagination.limit]
        elif pagination.offset > 0:
            perm_tuples = perm_tuples[pagination.offset :]

        # Convert to the correct data transfer object.
        permissions = [
            Permission(name=p.name, description=p.description, created_on=p.created_on)
            for p in perm_tuples
        ]
        return PaginatedList[Permission](
            values=permissions, total=total, offset=pagination.offset, limit=pagination.limit
        )


class SQLPermissionRepository(PermissionRepository):
    """SQL storage layer for permissions."""

    def __init__(self, session):
        # type: (Session) -> None
        self.session = session

    def get_permission(self, name):
        # type: (str) -> Optional[Permission]
        permission = SQLPermission.get(self.session, name=name)
        if not permission:
            return None
        return Permission(
            name=permission.name,
            description=permission.description,
            created_on=permission.created_on,
        )

    def disable_permission(self, name):
        # type: (str) -> None
        permission = SQLPermission.get(self.session, name=name)
        if not permission:
            raise PermissionNotFoundException(name)
        permission.enabled = False

    def list_permissions(self, pagination, audited_only):
        # type: (Pagination[ListPermissionsSortKey], bool) -> PaginatedList[Permission]
        raise NotImplementedError()
