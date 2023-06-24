"""
@author: Arno
@created: 2022-04-21
@modified: 2023-05-20

Request URL Helper to get response from API 
"""
import json
import logging
import ssl
import time
from http import HTTPStatus
from typing import Any, Callable, Literal, Union, overload

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

import config
from src.errors.reqerrors import RemoteError

log = logging.getLogger(__name__)


class RequestHelper:
    """
    Functions to help requesting response from an API
    """

    def __init__(self):
        self.session = self._init_session()
        self.view_update_waiting_time: Callable[[int], None]

    @staticmethod
    def _init_session():
        """Initialization of the session"""
        session = requests.Session()
        # session.headers.update({'Accept': 'application/json'})
        retry = Retry(
            total=config.REQUESTS_RETRIES,
            backoff_factor=1.5,
            respect_retry_after_header=False,  # False: show sleep time via this class
            status_forcelist=[502, 503, 504],
        )
        adapter = HTTPAdapter(max_retries=retry)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        return session

    def update_header(self, params: dict):
        """Update the header of the session

        params = dictionary with parameters for the header
        """
        self.session.headers.update(params)

    def get_request_response(self, url: str, stream=False) -> dict:
        """general request url function

        url = api url for request
        """
        resp = {}
        response = requests.Response
        request_timeout = 60
        verify = True
        requests.packages.urllib3.disable_warnings()  # type: ignore
        log.debug(f"Querying {url}")

        while True:
            try:
                response = self.session.get(
                    url, timeout=request_timeout, stream=stream, verify=verify
                )
                if response.status_code == HTTPStatus.TOO_MANY_REQUESTS:  # 429
                    if "Retry-After" in response.headers.keys():
                        sleep_time = int(response.headers["Retry-After"]) + 1
                        self.sleep_print_time(sleep_time)
                    else:
                        break  # raise requests.exceptions.RequestException
                else:
                    break
            except requests.exceptions.SSLError as e:
                log.exception("1 Requests SSL Error:", e)
                verify = False  # raise
                # todo: Download ssl certification and try again
                # serverHost = 'proton.alcor.exchange'
                # serverPort = '443'
                # serverAddress = (serverHost, serverPort)
                # cert = ssl.get_server_certificate(serverAddress)
                # cacet.pem = requests.certs.where()
            except ssl.SSLCertVerificationError as e:
                log.exception("2 SSL Certification Error:", e)
                verify = False  # raise
            except requests.exceptions.RequestException as e:
                log.exception("3 Request exception:", e)
                # raise
            except Exception as e:
                log.exception("4 Exception:", e)
                # raise

        try:
            # get json from response, with type dict (mostly) or type list (Alcor exchange)
            resp_unknown = response.json()

            # when return type is a list, convert to dict
            if isinstance(resp_unknown, list):
                resp.update({"result": resp_unknown})
            else:
                resp = resp_unknown

        except Exception as e:
            print("JSON Exception: ", e)

        try:
            response.raise_for_status()
            resp.update({"status_code": response.status_code})

        except requests.exceptions.HTTPError as e:
            print("No status Exception: ", e)

            # check if error key is in result dictionary
            if "error" in resp:
                resp.update({"status_code": "error"})
            else:
                resp.update({"status_code": "no status"})

        except Exception as e:
            print("Other Exception: ", e)  # , response.json())
            # raise
            resp.update({"status_code": "error"})
            resp.update({"prices": []})

        return resp

    def api_url_params(self, url: str, params: dict, api_url_has_params=False):
        """
        Add params to the url

        url = url to be extended with parameters
        params = dictionary of parameters
        api_url_has_params = bool to extend url with '?' or '&'
        """
        if params:
            # if api_url contains already params and there is already a '?' avoid
            # adding second '?' (api_url += '&' if '?' in api_url else '?'); causes
            # issues with request parametes (usually for endpoints with required
            # arguments passed as parameters)
            url += "&" if api_url_has_params else "?"
            for key, value in params.items():
                if type(value) == bool:
                    value = str(value).lower()

                url += f"{key}={value}&"
            url = url[:-1]
        return url

    def attach_view_update_waiting_time(
        self, fn_waiting_time: Callable[[int], None]
    ) -> None:
        """Set the viewers waiting time function to the coinprice program"""
        self.view_update_waiting_time = fn_waiting_time

    def sleep_print_time(self, sleeping_time: int):
        """
        Sleep and print countdown timer
        Used for a 429 response retry-after

        sleeping_time = total time to sleep in seconds
        """
        for i in range(sleeping_time, 0, -1):
            self.view_update_waiting_time(i)
            time.sleep(1)


# ****************************************************


def request_get(
    url: str,
    timeout: int = config.REQUESTS_TIMEOUT,
    handle_429: bool = False,
    backoff_in_seconds: Union[int, float] = 0,
) -> Union[dict, list]:
    """
    May raise:
    - UnableToDecryptRemoteData from request_get
    - Remote error if the get request fails
    """
    log.debug(f"Querying {url}")
    # TODO make this a bit more smart. Perhaps conditional on the type of request.
    # Not all requests would need repeated attempts
    response = retry_calls(
        retries=config.REQUESTS_RETRIES,
        location="",
        handle_429=handle_429,
        backoff_in_seconds=backoff_in_seconds,
        url=url,
        timeout=timeout,
    )

    if response.status_code != HTTPStatus.OK:
        raise RemoteError(f"{url} returned status: {response.status_code}")

    try:
        result = json.loads(response.text)
    except json.decoder.JSONDecodeError as e:
        raise RemoteError(f"{url} returned malformed json. Error: {e!s}") from e

    return result


def request_get_dict(
    url: str,
    timeout: int = config.REQUESTS_TIMEOUT,
    handle_429: bool = False,
    backoff_in_seconds: Union[int, float] = 0,
) -> dict:
    """Like request_get, but the endpoint only returns a dict

    May raise:
    - UnableToDecryptRemoteData from request_get
    - Remote error if the get request fails
    """
    response = request_get(url, timeout, handle_429, backoff_in_seconds)
    assert isinstance(response, dict)
    return response


def retry_calls(
    retries: int,
    location: str,
    handle_429: bool,
    backoff_in_seconds: Union[int, float],
    url: str,
    timeout: int,
    **kwargs: Any,
) -> Any:
    """Calls a function that deals with external apis for a given number of times
    untils it fails or until it succeeds.

    If it fails with an acceptable error then we wait for a bit until the next try.

    Can also handle to many request (429) errors with a specific backoff in seconds if required.

    - Raises RemoteError if there is something wrong with contacting the remote
    """
    tries = retries
    while True:
        try:
            result = requests.get(url=url, timeout=timeout, **kwargs)

            if handle_429 and result.status_code == HTTPStatus.TOO_MANY_REQUESTS:
                if tries == 0:
                    raise RemoteError(
                        f"{location} query for {url} failed after {retries} tries",
                    )

                if "Retry-After" in result.headers.keys():
                    sleep_time = int(result.headers["Retry-After"]) + 1
                    # self.sleep_print_time(sleep_time)
                    log.debug(
                        f"In retry_call for {location}-{url}. Got 429. Retrying after "
                        f"{sleep_time} seconds",
                    )
                    time.sleep(sleep_time)
                else:
                    log.debug(
                        f"In retry_call for {location}-{url}. Got 429. Backing off for "
                        f"{backoff_in_seconds} seconds",
                    )
                    time.sleep(backoff_in_seconds)
                tries -= 1
                continue

            return result

        except requests.exceptions.RequestException as e:
            tries -= 1
            log.debug(
                f"In retry_call for {location}-{url}. Got error {e!s} "
                f"Trying again ... with {tries} tries left",
            )
            if tries == 0:
                raise RemoteError(
                    "{} query for {} failed after {} tries. Reason: {}".format(
                        location,
                        url,
                        retries,
                        e,
                    )
                ) from e


@overload
def query_file(url: str, is_json: Literal[True]) -> dict[str, Any]:
    ...


@overload
def query_file(url: str, is_json: Literal[False]) -> str:
    ...


def query_file(url: str, is_json: bool = False) -> Union[str, dict[str, Any]]:
    """
    Query the given file url and return the contents of the file
    May raise:
    - RemoteError if it was not possible to query the remote or the file is not a valid json file
    and is_json is set to true.
    """
    try:
        response = requests.get(url=url, timeout=config.REQUESTS_TIMEOUT)
    except requests.exceptions.RequestException as e:
        raise RemoteError(f"Failed to query file {url} due to: {e!s}") from e

    if response.status_code != HTTPStatus.OK:
        raise RemoteError(
            f"File query for {url} failed with status code "
            f"{response.status_code} and text: {response.text}",
        )

    if is_json is True:
        try:
            return response.json()
        except json.decoder.JSONDecodeError as e:
            raise RemoteError(f"Queried file {url} is not a valid json file") from e

    return response.text
