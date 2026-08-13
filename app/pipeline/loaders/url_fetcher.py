import ipaddress
import socket
from urllib.parse import urlparse

import httpx
from fastapi import HTTPException, status

from app.core.constants import MAX_URL_CONTENT_SIZE, URL_FETCH_TIMEOUT_SECONDS, WEB_CONTENT_TYPE

ALLOWED_SCHEMES = {"http", "https"}


class UrlFetcher:
    """Fetches a URL's body with SSRF guards. Note: DNS is resolved once here for
    validation and again by httpx when connecting, so a DNS-rebinding attacker could
    still slip past this check between the two lookups. Acceptable for now; revisit
    (e.g. pin the resolved IP for the actual connection) before handling untrusted
    multi-tenant traffic at scale.
    """

    def fetch(self, url: str) -> bytes:
        self._validate_safe(url)

        try:
            with httpx.stream(
                "GET",
                url,
                timeout=URL_FETCH_TIMEOUT_SECONDS,
                follow_redirects=False,
            ) as response:
                self._validate_status(response)
                self._validate_content_type(response)
                return self._read_capped(response)
        except httpx.HTTPError as ex:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to fetch URL: {ex}",
            ) from ex

    def _validate_safe(self, url: str) -> None:
        parsed = urlparse(url)

        if parsed.scheme not in ALLOWED_SCHEMES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only http and https URLs are supported.",
            )

        if not parsed.hostname:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="URL is missing a hostname.",
            )

        self._validate_not_private(parsed.hostname)

    def _validate_not_private(self, hostname: str) -> None:
        try:
            resolved_ips = {info[4][0] for info in socket.getaddrinfo(hostname, None)}
        except socket.gaierror as ex:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Could not resolve URL hostname.",
            ) from ex

        for ip in resolved_ips:
            address = ipaddress.ip_address(ip)
            if (
                address.is_private
                or address.is_loopback
                or address.is_link_local
                or address.is_reserved
                or address.is_multicast
            ):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="URL resolves to a disallowed network address.",
                )

    def _validate_status(self, response: httpx.Response) -> None:
        if response.status_code >= 300:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"URL returned an unsupported status code: {response.status_code}",
            )

    def _validate_content_type(self, response: httpx.Response) -> None:
        content_type = response.headers.get("content-type", "")
        if WEB_CONTENT_TYPE not in content_type:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="URL did not return HTML content.",
            )

    def _read_capped(self, response: httpx.Response) -> bytes:
        chunks: list[bytes] = []
        total_size = 0

        for chunk in response.iter_bytes():
            total_size += len(chunk)
            if total_size > MAX_URL_CONTENT_SIZE:
                raise HTTPException(
                    status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                    detail="Page content exceeds maximum size.",
                )
            chunks.append(chunk)

        return b"".join(chunks)
