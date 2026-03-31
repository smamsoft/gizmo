# gizmo_client_v2.py

import os
import logging
from typing import Dict, Any, Optional

import httpx

from gizmo_client.auth import get_gizmo_token
from gizmo_endpoints import GIZMO_V2

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("GIZMO_CLIENT_V2")


class GizmoClientV2:
    def __init__(self):
        server = os.getenv("GIZMO_SERVER")
        if not server:
            raise RuntimeError("GIZMO_SERVER is not configured in .env")

        self.base_url = server.rstrip("/")
        self.token: Optional[str] = None

    async def _ensure_token(self) -> None:
        if not self.token:
            logger.info("[GIZMO V2] Obtaining JWT token...")
            self.token = await get_gizmo_token()

    async def execute(
        self,
        endpoint_key: str,
        path_params: Optional[Dict[str, Any]] = None,
        query_params: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        if endpoint_key not in GIZMO_V2:
            logger.error(f"Endpoint key '{endpoint_key}' not found in GIZMO_V2 mapping.")
            return {"error": "Invalid endpoint key"}

        method, path = GIZMO_V2[endpoint_key]

        if path_params:
            path = path.format(**path_params)

        url = f"{self.base_url}{path}"

        await self._ensure_token()

        headers: Dict[str, str] = {
            "Authorization": f"Bearer {self.token}",
            "Accept": "application/json",
            "Content-Type": "application/json",
        }

        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                logger.info(f"[GIZMO V2] Executing: {method} {url}")

                resp = await client.request(
                    method=method,
                    url=url,
                    params=query_params,
                    json=json_data,
                    headers=headers,
                )

                # لو 401، جرّب تجديد التوكن مرة
                if resp.status_code == 401:
                    logger.error("[GIZMO V2] 401 Unauthorized, refreshing token...")
                    self.token = await get_gizmo_token()
                    headers["Authorization"] = f"Bearer {self.token}"
                    resp = await client.request(
                        method=method,
                        url=url,
                        params=query_params,
                        json=json_data,
                        headers=headers,
                    )

                if resp.status_code in (200, 201, 204):
                    if resp.text:
                        try:
                            return resp.json()
                        except Exception:
                            return {"raw": resp.text}
                    return {"status": "success"}
                else:
                    logger.error(f"[GIZMO V2] Error {resp.status_code}: {resp.text}")
                    return {
                        "error": f"HTTP {resp.status_code}",
                        "details": resp.text,
                    }

        except Exception as e:
            logger.error(f"[GIZMO V2] Exception during request: {e}")
            return {"error": "Connection Failed", "details": str(e)}


gizmo_v2 = GizmoClientV2()
