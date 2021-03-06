#
#   © Copyright 2020 Hewlett Packard Enterprise Development LP
#
#   This file was auto-generated by the Python SDK generator; DO NOT EDIT.
#

from ..resource import Resource, Collection
from ..exceptions import NimOSAPIOperationUnsupported

class ActiveDirectoryMembership(Resource):
    """
    Manages the storage array's membership with the Active Directory.

    Parameters:
    - id                  : Identifier for the Active Directory Domain.
    - description         : Description for the Active Directory Domain.
    - name                : Identifier for the Active Directory domain.
    - netbios             : Netbios name for the Active Directory domain.
    - server_list         : List of IP addresses or names for the backup domain controller.
    - computer_name       : The name of the computer account in the domain controller.
    - organizational_unit : The location for the computer account.
    - user                : Name of the Activer Directory user with Administrator's privilege.
    - password            : Password for the Active Directory user.
    - enabled             : Active Directory authentication is currently enabled.
    """

    def remove(self, password, user, force=False):
        """
        Leaves the Active Directory domain.

        Parameters:
        - id       : ID of the active directory.
        - user     : Name of the Activer Directory user with the privilege to leave the domain.
        - password : Password for the Active Directory user.
        - force    : Use this option when there is an error when leaving the domain.
        """

        return self.collection.remove(self.id, password, user, force)

    def report_status(self):
        """
        Reports the detail status of the Active Directory domain.

        Parameters:
        - id : ID of the active directory.
        """

        return self.collection.report_status(self.id)

    def test_user(self, name):
        """
        Tests whether the user exist in the Active Directory. If the user is present, then the user's group and role information is reported.

        Parameters:
        - id   : ID of the Active Directory.
        - name : Name of the Active Directory user.
        """

        return self.collection.test_user(self.id, name)

    def test_group(self, name):
        """
        Tests whether the user group exist in the Active Directory.

        Parameters:
        - id   : ID of the Active Directory.
        - name : Name of the Active Directory group.
        """

        return self.collection.test_group(self.id, name)

    def delete(self, **kwargs):
        raise NimOSAPIOperationUnsupported("delete operation not supported")

class ActiveDirectoryMembershipList(Collection):
    resource = ActiveDirectoryMembership
    resource_type = "active_directory_memberships"

    def remove(self, id, password, user, force=False):
        """
        Leaves the Active Directory domain.

        Parameters:
        - id       : ID of the active directory.
        - user     : Name of the Activer Directory user with the privilege to leave the domain.
        - password : Password for the Active Directory user.
        - force    : Use this option when there is an error when leaving the domain.
        """

        return self._client.perform_resource_action(self.resource_type, id, 'remove', id=id, password=password, user=user, force=force)

    def report_status(self, id):
        """
        Reports the detail status of the Active Directory domain.

        Parameters:
        - id : ID of the active directory.
        """

        return self._client.perform_resource_action(self.resource_type, id, 'report_status', id=id)

    def test_user(self, id, name):
        """
        Tests whether the user exist in the Active Directory. If the user is present, then the user's group and role information is reported.

        Parameters:
        - id   : ID of the Active Directory.
        - name : Name of the Active Directory user.
        """

        return self._client.perform_resource_action(self.resource_type, id, 'test_user', id=id, name=name)

    def test_group(self, id, name):
        """
        Tests whether the user group exist in the Active Directory.

        Parameters:
        - id   : ID of the Active Directory.
        - name : Name of the Active Directory group.
        """

        return self._client.perform_resource_action(self.resource_type, id, 'test_group', id=id, name=name)

    def delete(self, **kwargs):
        raise NimOSAPIOperationUnsupported("delete operation not supported")
