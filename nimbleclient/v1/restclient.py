#
#   © Copyright 2020 Hewlett Packard Enterprise Development LP
#

import logging
import uuid
import requests
import json
import time
import datetime

from nimbleclient.exceptions import NimOSAuthenticationError, NimOSAPIError, NimOSClientJobTimeoutError
from ..__init__ import __version__

requests.packages.urllib3.disable_warnings(requests.packages.urllib3.exceptions.InsecureRequestWarning)


class SessionManager:
    """Tracks current NimOS REST sessions in order to reuse them"""

    _SESSIONS = {}


class NimOSAPIClient:
    """NimOS REST API Client session"""

    _ENDPOINTS = {
        # This endpoint list was auto-generated by the Python SDK generator; DO NOT EDIT.
        'versions': 'versions',
        'application_categories': 'v1/application_categories',
        'chap_users': 'v1/chap_users',
        'master_key': 'v1/master_key',
        'alarms': 'v1/alarms',
        'volumes': 'v1/volumes',
        'shelves': 'v1/shelves',
        'support': 'v1/support',
        'key_managers': 'v1/key_managers',
        'protection_templates': 'v1/protection_templates',
        'folders': 'v1/folders',
        'tokens': 'v1/tokens',
        'fibre_channel_interfaces': 'v1/fibre_channel_interfaces',
        'network_interfaces': 'v1/network_interfaces',
        'arrays': 'v1/arrays',
        'fibre_channel_configs': 'v1/fibre_channel_configs',
        'initiators': 'v1/initiators',
        'performance_policies': 'v1/performance_policies',
        'space_domains': 'v1/space_domains',
        'snapshot_collections': 'v1/snapshot_collections',
        'replication_partners': 'v1/replication_partners',
        'events': 'v1/events',
        'snapshots': 'v1/snapshots',
        'application_servers': 'v1/application_servers',
        'user_policies': 'v1/user_policies',
        'user_groups': 'v1/user_groups',
        'subnets': 'v1/subnets',
        'controllers': 'v1/controllers',
        'fibre_channel_sessions': 'v1/fibre_channel_sessions',
        'users': 'v1/users',
        'protection_schedules': 'v1/protection_schedules',
        'initiator_groups': 'v1/initiator_groups',
        'access_control_records': 'v1/access_control_records',
        'active_directory_memberships': 'v1/active_directory_memberships',
        'fibre_channel_ports': 'v1/fibre_channel_ports',
        'protocol_endpoints': 'v1/protocol_endpoints',
        'witnesses': 'v1/witnesses',
        'jobs': 'v1/jobs',
        'audit_log': 'v1/audit_log',
        'pools': 'v1/pools',
        'volume_collections': 'v1/volume_collections',
        'disks': 'v1/disks',
        'fibre_channel_initiator_aliases': 'v1/fibre_channel_initiator_aliases',
        'groups': 'v1/groups',
        'software_versions': 'v1/software_versions',
        'network_configs': 'v1/network_configs',
    }

    def __init__(self, hostname, username, password, job_timeout=60, port=5392):
        """Initialize a session to the NimOS REST API."""

        connection_hash = str(uuid.uuid3(uuid.NAMESPACE_OID, f'{hostname}{port}{username}{password}'))

        self.hostname = hostname
        self.port = port
        self.job_timeout = job_timeout

        self.__auth = {
            'data': {
                'username': username,
                'password': password,
                'app_name': f'NimOS Python SDK v{__version__}'
            }
        }
        logging.debug("NimOSAPIClient created with [hostname: %s], [job_timeout: %s seconds], [port: %s], [SDK Version: %s]",
                      hostname, job_timeout, port, f'v{__version__}')

        self.__connection_hash = connection_hash

        if connection_hash in SessionManager._SESSIONS:
            self.session_id, self.session_token = SessionManager._SESSIONS[connection_hash]
            self.connected = True
            self._headers = {'X-Auth-Token': str(self.session_token)}

        else:
            self._headers = {}
            self.session_token = None
            self.session_id = None
            self.connected = self._connect()

    def _connect(self):
        """Perform NimOS authentication and session token retrieval."""

        try:
            response = requests.post(
                f"https://{self.hostname}:{self.port}/{self._ENDPOINTS['tokens']}",
                json=self.__auth,
                verify=False
            )

            sessiondata = response.json()

            if 'messages' in sessiondata and sessiondata['messages'][0]['code'] == 'SM_http_unauthorized':
                raise NimOSAuthenticationError("Invalid credentials")

            sessiondata = sessiondata['data']

            if 'session_token' not in sessiondata:
                raise NimOSAuthenticationError("Invalid credentials")

            self.session_token = sessiondata['session_token']
            self.session_id = sessiondata['id']
            self._headers = {'X-Auth-Token': str(self.session_token)}

            SessionManager._SESSIONS[self.__connection_hash] = (self.session_id, self.session_token)

            return True

        except requests.ConnectionError as error:
            logging.exception(error)
            raise ConnectionError(f"Error connecting to {self.hostname}")

    def _refresh_connection(self):
        """Checks status of NimOS session and reconnects if necessary."""

        try:
            response = requests.get(
                f"https://{self.hostname}:{self.port}/{self._ENDPOINTS['tokens']}/{self.session_id}",
                headers=self._headers,
                verify=False
            ).json()

            if 'messages' in response and response['messages'][0]['severity'] == 'error':
                self._connect()

        except requests.ConnectionError as error:
            logging.exception(error)
            raise ConnectionError(f"Error reconnecting to {self.hostname}")

    def close_connection(self):
        """Closes NimOS session (deletes user token)"""

        try:
            requests.delete(
                f"https://{self.hostname}:{self.port}/{self._ENDPOINTS['tokens']}/{self.session_id}",
                headers=self._headers,
                verify=False
            )

            del SessionManager._SESSIONS[self.__connection_hash]

        except requests.exceptions.RequestException as error:
            logging.exception(error)
            raise ConnectionError("Error closing connection")

    @classmethod
    def build_advanced_criteria(self, operator, criteria):
        """Constructs advanced criteria and returns JSON object."""

        return {
            'data': {
                '_constructor': 'AdvancedCriteria',
                'operator': operator,
                'criteria': criteria,
            },
            'operationType': 'fetch'
        }

    def get(self, endpoint, filter=None, limit=None, from_id=None, **params):
        """Wrapper for GET requests with filters and advanced criteria"""

        # Set the url if limit and/or from_id (pagination) is requested
        url = f'https://{self.hostname}:{self.port}/{endpoint}'

        if limit is not None:
            url = f'{url}?pageSize={limit}'

        if from_id is not None:
            url = f"{url}{'&' if limit is not None else '?'}id%3E{from_id}"

        try:
            # Init response data and query for more paginated data records if available
            response_data = []
            while 1:
                if filter is not None:
                    response = requests.post(
                        url,
                        params=params,
                        json=filter,
                        headers=self._headers,
                        verify=False
                    )
                else:
                    response = requests.get(
                        url,
                        params=params,
                        headers=self._headers,
                        verify=False
                    )

                if response.status_code >= 400:
                    if 'SM_http_unauthorized' in str(response.content):
                        self._refresh_connection()
                    else:
                        raise NimOSAPIError(response.json())

                response = response.json()

                # Check for errors if any in the response (Treat partial response as an error)
                if 'messages' in response:
                    raise NimOSAPIError(response['messages'])

                # Get response
                if 'totalRows' not in response:
                    return response

                # Append to the resultant data and continue to read more
                response_data.extend(response["data"])

                # When limit/pageSize is requested, then break and return the response.
                if limit is not None:
                    break

                # No more records to read, stop here
                if 'data' in response and len(response['data']) == 0:
                    break

                # Add break condition when 'endRow' is equal to 'totalRows'.
                # This is to handle 'controllers' list() operation in particular.
                # The 'controllers' endpoint doesn't support 'startRow' or 'endRow' as valid query parameters in the URL.
                if response['endRow'] == response['totalRows']:
                    break

                # Set next start row index to continue reading more records
                if 'startRow' in params:
                    params['startRow'] += len(response["data"])
                else:
                    params['startRow'] = len(response["data"])

                logging.debug(f"[read_records_count: {len(response_data)}], [total_rows: {response['totalRows']}], [next_start_row: {params['startRow']}]")

            logging.debug(f'Retrieved {len(response_data)} record(s)')
            return response_data

        except requests.exceptions.RequestException as error:
            logging.exception(error)
            raise ConnectionError(f"Error retrieving data from {self.hostname}")

    def delete(self, endpoint, job_timeout=None):
        """Wrapper for DELETE requests"""

        logging.debug("job_timeout: [%s seconds]", job_timeout if job_timeout is not None else self.job_timeout)
        try:
            while 1:
                response = requests.delete(
                    f'https://{self.hostname}:{self.port}/{endpoint}',
                    headers=self._headers,
                    verify=False
                )

                if response.status_code >= 400:
                    if 'SM_http_unauthorized' in str(response.content):
                        self._refresh_connection()
                    else:
                        raise NimOSAPIError(response.json())
                elif response.status_code == 202:
                    # Handle async job response
                    job_response = response.json()
                    if 'messages' in job_response and job_response['messages'][0]['code'] == 'SM_async_job_id':
                        logging.debug("Got async job response: %s", json.dumps(job_response['messages'], indent=4))
                        return self.job_handler(job_response['messages'][0]['arguments']['job_id'], job_timeout)
                    else:
                        break
                else:
                    break

            return response.json()

        except requests.exceptions.RequestException as error:
            logging.exception(error)
            raise ConnectionError(f"Error communicating with {self.hostname}")

    def put(self, endpoint, job_timeout=None, **payload):
        """Wrapper for PUT requests."""

        logging.debug("job_timeout: [%s seconds]", job_timeout if job_timeout is not None else self.job_timeout)

        # Translate metadata dict to REST key-value pairs.
        # Ex: {'k1': 'k1', 'k2': 'v2'} ==> [{'key': 'k1', 'value': 'v1'}, {'key': 'k2', 'value': 'v2'}]
        if 'metadata' in payload:
            payload['metadata'] = [{'key': key, 'value': payload['metadata'][key]} for key in payload['metadata']]

        try:
            while 1:
                response = requests.put(
                    f'https://{self.hostname}:{self.port}/{endpoint}',
                    headers=self._headers,
                    json={'data': payload},
                    verify=False
                )

                if response.status_code >= 400:
                    if 'SM_http_unauthorized' in str(response.content):
                        self._refresh_connection()
                    else:
                        raise NimOSAPIError(response.json())
                elif response.status_code == 202:
                    # Handle async job response
                    job_response = response.json()
                    if 'messages' in job_response and job_response['messages'][0]['code'] == 'SM_async_job_id':
                        logging.debug("Got async job response: %s", json.dumps(job_response['messages'], indent=4))
                        return self.job_handler(job_response['messages'][0]['arguments']['job_id'], job_timeout)
                    else:
                        break
                else:
                    break

            return response.json()

        except requests.exceptions.RequestException as error:
            logging.exception(error)
            raise ConnectionError(f"Error communicating with {self.hostname}")

    def post(self, endpoint, job_timeout=None, **params):
        """Wrapper for POST requests"""

        logging.debug("job_timeout: [%s seconds]", job_timeout if job_timeout is not None else self.job_timeout)

        # Translate metadata dict to REST key-value pairs.
        # Ex: {'k1': 'k1', 'k2': 'v2'} ==> [{'key': 'k1', 'value': 'v1'}, {'key': 'k2', 'value': 'v2'}]
        if 'metadata' in params:
            params['metadata'] = [{'key': key, 'value': params['metadata'][key]} for key in params['metadata']]

        try:
            while 1:
                response = requests.post(
                    f'https://{self.hostname}:{self.port}/{endpoint}',
                    headers=self._headers,
                    json={'data': params},
                    verify=False
                )

                if response.status_code >= 400:
                    if 'SM_http_unauthorized' in str(response.content):
                        self._refresh_connection()
                    else:
                        raise NimOSAPIError(response.json())
                elif response.status_code == 202:
                    # Handle async job response
                    job_response = response.json()
                    if 'messages' in job_response and job_response['messages'][0]['code'] == 'SM_async_job_id':
                        logging.debug("Got async job response: %s", json.dumps(job_response['messages'], indent=4))
                        return self.job_handler(job_response['messages'][0]['arguments']['job_id'], job_timeout)
                    else:
                        break
                else:
                    break

            response = response.json()
            return response

        except requests.exceptions.RequestException as error:
            logging.exception(error)
            raise ConnectionError(f"Error communicating with {self.hostname}")

    def get_resource(self, resource, ident, **params):
        if resource not in self._ENDPOINTS:
            raise ValueError(f"Unknown resource {resource}")

        resp = self.get(f"{self._ENDPOINTS[resource]}/{ident}", **params)
        return resp['data'] if 'data' in resp else resp

    def list_resources(self, resource, detail=False, filter=None, limit=None, from_id=None, **params):
        if resource not in self._ENDPOINTS:
            raise ValueError(f"Unknown resource {resource}")

        # Build advanced criteria filter if requested
        if filter is not None:
            filter = self.build_advanced_criteria(filter['operator'], filter['criteria'])

        resp = self.get(f"{self._ENDPOINTS[resource]}{'/detail' if detail else ''}", filter, limit, from_id, **params)
        return resp['data'] if 'data' in resp else resp

    def create_resource(self, resource, **params):
        if resource not in self._ENDPOINTS:
            raise ValueError(f"Unknown resource {resource}")

        resp = self.post(self._ENDPOINTS[resource], **params)
        return resp['data'] if 'data' in resp else resp

    def delete_resource(self, resource, ident, job_timeout=None):
        if resource not in self._ENDPOINTS:
            raise ValueError(f"Unknown resource {resource}")

        resp = self.delete(f"{self._ENDPOINTS[resource]}/{ident}", job_timeout)
        return resp['data'] if 'data' in resp else resp

    def update_resource(self, resource, ident, **params):
        if resource not in self._ENDPOINTS:
            raise ValueError(f"Unknown resource {resource}")

        resp = self.put(f"{self._ENDPOINTS[resource]}/{ident}", **params)
        return resp['data'] if 'data' in resp else resp

    def perform_resource_action(self, resource, ident, action, **params):
        if resource not in self._ENDPOINTS:
            raise ValueError(f"Unknown resource {resource}")

        resp = self.post(f"{self._ENDPOINTS[resource]}/{ident}/actions/{action}", **params)
        return resp['data'] if 'data' in resp else resp

    def perform_bulk_resource_action(self, resource, action, **params):
        if resource not in self._ENDPOINTS:
            raise ValueError(f"Unknown resource {resource}")

        resp = self.post(f"{self._ENDPOINTS[resource]}/actions/{action}", **params)
        return resp['data'] if 'data' in resp else resp

    def job_handler(self, job_id, job_timeout, retry_interval=5):

        # Use global/default job timeout if unspecified in the request
        timeout_sec = job_timeout if job_timeout is not None else self.job_timeout

        now = datetime.datetime.now()
        expiry_time = now + datetime.timedelta(0, timeout_sec)
        logging.debug(f"job_id: [{job_id}], job_timeout: [{timeout_sec} seconds], current_time: [{now}], job_retry_expiry_time: [{expiry_time}], retry_interval: [{retry_interval} seconds]")
        while 1:
            try:
                # Get job status from Array
                response = self.get_resource('jobs', job_id)
                logging.debug("JOB STATUS RESPONSE: %s", json.dumps(response, indent=4))
                if (response['state'] == 'done'):
                    logging.info("Job with id '%s' completed with status '%s'", job_id, response['result'])
                    break

                if datetime.datetime.now().time() > expiry_time.time():
                    logging.error("Job status retry timeout has expired after [%s] seconds, returning with client timeout exception", timeout_sec)
                    raise NimOSClientJobTimeoutError(response)
                else:
                    #  Sleep n Wait
                    if timeout_sec < retry_interval:
                        logging.debug("Sleeping for [%s seconds] before next retry attempt ...", timeout_sec)
                        time.sleep(timeout_sec)
                    else:
                        logging.debug("Sleeping for [%s seconds] before next retry attempt ...", retry_interval)
                        time.sleep(retry_interval)

            except requests.exceptions.RequestException as error:
                logging.exception(error)
                raise ConnectionError(f"Error communicating with {self.hostname}")

        return response
