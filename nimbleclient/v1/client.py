#
#   © Copyright 2020 Hewlett Packard Enterprise Development LP
#
#   This file was auto-generated by the Python SDK generator; DO NOT EDIT.
#

from .restclient import NimOSAPIClient
from .api.versions import VersionList
from .api.application_categories import ApplicationCategoryList
from .api.chap_users import ChapUserList
from .api.master_key import MasterKeyList
from .api.alarms import AlarmList
from .api.volumes import VolumeList
from .api.shelves import ShelfList
from .api.key_managers import KeyManagerList
from .api.protection_templates import ProtectionTemplateList
from .api.folders import FolderList
from .api.tokens import TokenList
from .api.fibre_channel_interfaces import FibreChannelInterfaceList
from .api.network_interfaces import NetworkInterfaceList
from .api.arrays import ArrayList
from .api.fibre_channel_configs import FibreChannelConfigList
from .api.initiators import InitiatorList
from .api.performance_policies import PerformancePolicyList
from .api.space_domains import SpaceDomainList
from .api.snapshot_collections import SnapshotCollectionList
from .api.replication_partners import ReplicationPartnerList
from .api.events import EventList
from .api.snapshots import SnapshotList
from .api.application_servers import ApplicationServerList
from .api.user_policies import UserPolicyList
from .api.user_groups import UserGroupList
from .api.subnets import SubnetList
from .api.controllers import ControllerList
from .api.fibre_channel_sessions import FibreChannelSessionList
from .api.users import UserList
from .api.protection_schedules import ProtectionScheduleList
from .api.initiator_groups import InitiatorGroupList
from .api.access_control_records import AccessControlRecordList
from .api.active_directory_memberships import ActiveDirectoryMembershipList
from .api.fibre_channel_ports import FibreChannelPortList
from .api.protocol_endpoints import ProtocolEndpointList
from .api.witnesses import WitnessList
from .api.jobs import JobList
from .api.audit_log import AuditLogList
from .api.pools import PoolList
from .api.volume_collections import VolumeCollectionList
from .api.disks import DiskList
from .api.fibre_channel_initiator_aliases import FibreChannelInitiatorAliasList
from .api.groups import GroupList
from .api.software_versions import SoftwareVersionList
from .api.network_configs import NetworkConfigList

class Client:
    def __init__(self, hostname, username, password, port=5392):
        self._client = NimOSAPIClient(hostname, username, password, port)

    @property
    def versions(self):
        return VersionList(self._client)

    @property
    def application_categories(self):
        return ApplicationCategoryList(self._client)

    @property
    def chap_users(self):
        return ChapUserList(self._client)

    @property
    def master_key(self):
        return MasterKeyList(self._client)

    @property
    def alarms(self):
        return AlarmList(self._client)

    @property
    def volumes(self):
        return VolumeList(self._client)

    @property
    def shelves(self):
        return ShelfList(self._client)

    @property
    def key_managers(self):
        return KeyManagerList(self._client)

    @property
    def protection_templates(self):
        return ProtectionTemplateList(self._client)

    @property
    def folders(self):
        return FolderList(self._client)

    @property
    def tokens(self):
        return TokenList(self._client)

    @property
    def fibre_channel_interfaces(self):
        return FibreChannelInterfaceList(self._client)

    @property
    def network_interfaces(self):
        return NetworkInterfaceList(self._client)

    @property
    def arrays(self):
        return ArrayList(self._client)

    @property
    def fibre_channel_configs(self):
        return FibreChannelConfigList(self._client)

    @property
    def initiators(self):
        return InitiatorList(self._client)

    @property
    def performance_policies(self):
        return PerformancePolicyList(self._client)

    @property
    def space_domains(self):
        return SpaceDomainList(self._client)

    @property
    def snapshot_collections(self):
        return SnapshotCollectionList(self._client)

    @property
    def replication_partners(self):
        return ReplicationPartnerList(self._client)

    @property
    def events(self):
        return EventList(self._client)

    @property
    def snapshots(self):
        return SnapshotList(self._client)

    @property
    def application_servers(self):
        return ApplicationServerList(self._client)

    @property
    def user_policies(self):
        return UserPolicyList(self._client)

    @property
    def user_groups(self):
        return UserGroupList(self._client)

    @property
    def subnets(self):
        return SubnetList(self._client)

    @property
    def controllers(self):
        return ControllerList(self._client)

    @property
    def fibre_channel_sessions(self):
        return FibreChannelSessionList(self._client)

    @property
    def users(self):
        return UserList(self._client)

    @property
    def protection_schedules(self):
        return ProtectionScheduleList(self._client)

    @property
    def initiator_groups(self):
        return InitiatorGroupList(self._client)

    @property
    def access_control_records(self):
        return AccessControlRecordList(self._client)

    @property
    def active_directory_memberships(self):
        return ActiveDirectoryMembershipList(self._client)

    @property
    def fibre_channel_ports(self):
        return FibreChannelPortList(self._client)

    @property
    def protocol_endpoints(self):
        return ProtocolEndpointList(self._client)

    @property
    def witnesses(self):
        return WitnessList(self._client)

    @property
    def jobs(self):
        return JobList(self._client)

    @property
    def audit_log(self):
        return AuditLogList(self._client)

    @property
    def pools(self):
        return PoolList(self._client)

    @property
    def volume_collections(self):
        return VolumeCollectionList(self._client)

    @property
    def disks(self):
        return DiskList(self._client)

    @property
    def fibre_channel_initiator_aliases(self):
        return FibreChannelInitiatorAliasList(self._client)

    @property
    def groups(self):
        return GroupList(self._client)

    @property
    def software_versions(self):
        return SoftwareVersionList(self._client)

    @property
    def network_configs(self):
        return NetworkConfigList(self._client)
