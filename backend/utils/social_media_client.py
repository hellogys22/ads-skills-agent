"""HTTP client wrappers for Instagram, Facebook, and YouTube APIs."""

import logging
from typing import Any, Optional

import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

logger = logging.getLogger(__name__)

_TIMEOUT = httpx.Timeout(30.0, connect=10.0)


class _BaseClient:
    def __init__(self, base_url: str) -> None:
        self._base_url = base_url
        self._http = httpx.AsyncClient(base_url=base_url, timeout=_TIMEOUT)

    async def aclose(self) -> None:
        await self._http.aclose()

    @retry(wait=wait_exponential(multiplier=1, min=2, max=20), stop=stop_after_attempt(3))
    async def _get(self, path: str, params: Optional[dict] = None) -> dict[str, Any]:
        resp = await self._http.get(path, params=params)
        resp.raise_for_status()
        return resp.json()

    @retry(wait=wait_exponential(multiplier=1, min=2, max=20), stop=stop_after_attempt(3))
    async def _post(self, path: str, data: Optional[dict] = None, params: Optional[dict] = None) -> dict[str, Any]:
        resp = await self._http.post(path, data=data, params=params)
        resp.raise_for_status()
        return resp.json()

    @retry(wait=wait_exponential(multiplier=1, min=2, max=20), stop=stop_after_attempt(3))
    async def _delete(self, path: str, params: Optional[dict] = None) -> dict[str, Any]:
        resp = await self._http.delete(path, params=params)
        resp.raise_for_status()
        return resp.json()


# ── Instagram Graph API v18 ────────────────────────────────────────────────────

class InstagramClient(_BaseClient):
    """Wrapper for the Instagram Graph API."""

    BASE_URL = "https://graph.instagram.com/v18.0"

    def __init__(self, app_id: str, app_secret: str, access_token: str) -> None:
        super().__init__(self.BASE_URL)
        self.app_id = app_id
        self.app_secret = app_secret
        self.access_token = access_token

    def _token_params(self, extra: Optional[dict] = None) -> dict:
        p = {"access_token": self.access_token}
        if extra:
            p.update(extra)
        return p

    async def get_user_profile(self) -> dict[str, Any]:
        return await self._get("/me", params=self._token_params({"fields": "id,username,account_type"}))

    async def create_media_container(
        self,
        image_url: str,
        caption: str,
        media_type: str = "IMAGE",
    ) -> dict[str, Any]:
        """Step 1 of the two-step publish flow: create a container."""
        params = self._token_params(
            {"image_url": image_url, "caption": caption, "media_type": media_type}
        )
        return await self._post("/me/media", params=params)

    async def publish_media(self, creation_id: str) -> dict[str, Any]:
        """Step 2: publish the media container."""
        return await self._post(
            "/me/media_publish",
            params=self._token_params({"creation_id": creation_id}),
        )

    async def get_media_list(self, limit: int = 10) -> dict[str, Any]:
        return await self._get(
            "/me/media",
            params=self._token_params({"fields": "id,caption,media_type,timestamp,like_count,comments_count", "limit": limit}),
        )

    async def get_media_insights(self, media_id: str, metrics: list[str]) -> dict[str, Any]:
        return await self._get(
            f"/{media_id}/insights",
            params=self._token_params({"metric": ",".join(metrics)}),
        )

    async def get_account_insights(self, metrics: list[str], period: str = "day") -> dict[str, Any]:
        return await self._get(
            "/me/insights",
            params=self._token_params({"metric": ",".join(metrics), "period": period}),
        )

    async def get_comments(self, media_id: str, limit: int = 20) -> dict[str, Any]:
        return await self._get(
            f"/{media_id}/comments",
            params=self._token_params({"fields": "id,text,timestamp,username", "limit": limit}),
        )

    async def reply_to_comment(self, comment_id: str, message: str) -> dict[str, Any]:
        return await self._post(
            f"/{comment_id}/replies",
            params=self._token_params({"message": message}),
        )

    async def delete_media(self, media_id: str) -> dict[str, Any]:
        return await self._delete(f"/{media_id}", params=self._token_params())

    async def refresh_long_lived_token(self) -> dict[str, Any]:
        return await self._get(
            "/refresh_access_token",
            params={"grant_type": "ig_refresh_token", "access_token": self.access_token},
        )


# ── Facebook Graph API ─────────────────────────────────────────────────────────

class FacebookClient(_BaseClient):
    """Wrapper for the Facebook Graph API."""

    BASE_URL = "https://graph.facebook.com/v18.0"

    def __init__(self, app_id: str, app_secret: str, page_id: str, page_access_token: str) -> None:
        super().__init__(self.BASE_URL)
        self.app_id = app_id
        self.app_secret = app_secret
        self.page_id = page_id
        self.page_access_token = page_access_token

    def _token_params(self, extra: Optional[dict] = None) -> dict:
        p = {"access_token": self.page_access_token}
        if extra:
            p.update(extra)
        return p

    async def get_page_info(self) -> dict[str, Any]:
        return await self._get(
            f"/{self.page_id}",
            params=self._token_params({"fields": "id,name,fan_count,followers_count"}),
        )

    async def create_post(self, message: str, link: Optional[str] = None) -> dict[str, Any]:
        data: dict[str, Any] = {"message": message}
        if link:
            data["link"] = link
        return await self._post(f"/{self.page_id}/feed", params=self._token_params(data))

    async def create_photo_post(self, image_url: str, caption: str) -> dict[str, Any]:
        return await self._post(
            f"/{self.page_id}/photos",
            params=self._token_params({"url": image_url, "caption": caption}),
        )

    async def get_page_posts(self, limit: int = 10) -> dict[str, Any]:
        return await self._get(
            f"/{self.page_id}/posts",
            params=self._token_params(
                {"fields": "id,message,created_time,likes.summary(true),comments.summary(true)", "limit": limit}
            ),
        )

    async def get_post_insights(self, post_id: str) -> dict[str, Any]:
        metrics = "post_impressions,post_reach,post_engaged_users,post_clicks"
        return await self._get(
            f"/{post_id}/insights",
            params=self._token_params({"metric": metrics}),
        )

    async def delete_post(self, post_id: str) -> dict[str, Any]:
        return await self._delete(f"/{post_id}", params=self._token_params())


# ── YouTube Data API v3 ────────────────────────────────────────────────────────

class YouTubeClient(_BaseClient):
    """Wrapper for the YouTube Data API v3."""

    BASE_URL = "https://www.googleapis.com/youtube/v3"

    def __init__(self, api_key: str, access_token: Optional[str] = None) -> None:
        super().__init__(self.BASE_URL)
        self.api_key = api_key
        self.access_token = access_token

    def _key_params(self, extra: Optional[dict] = None) -> dict:
        p: dict[str, Any] = {"key": self.api_key}
        if extra:
            p.update(extra)
        return p

    def _auth_headers(self) -> dict:
        if self.access_token:
            return {"Authorization": f"Bearer {self.access_token}"}
        return {}

    async def search_videos(self, query: str, max_results: int = 10) -> dict[str, Any]:
        params = self._key_params(
            {"part": "snippet", "q": query, "type": "video", "maxResults": max_results}
        )
        return await self._get("/search", params=params)

    async def get_video_details(self, video_id: str) -> dict[str, Any]:
        params = self._key_params(
            {"part": "snippet,statistics,contentDetails", "id": video_id}
        )
        return await self._get("/videos", params=params)

    async def get_channel_stats(self, channel_id: str) -> dict[str, Any]:
        params = self._key_params(
            {"part": "statistics,snippet", "id": channel_id}
        )
        return await self._get("/channels", params=params)

    async def get_video_categories(self, region_code: str = "US") -> dict[str, Any]:
        return await self._get(
            "/videoCategories",
            params=self._key_params({"part": "snippet", "regionCode": region_code}),
        )

    async def upload_video(
        self,
        title: str,
        description: str,
        video_path: str,
        category_id: str = "22",
        privacy_status: str = "public",
    ) -> dict[str, Any]:
        """Upload a video file using resumable upload (multipart)."""
        import aiofiles

        if not self.access_token:
            raise ValueError("access_token required for video uploads")

        metadata = {
            "snippet": {
                "title": title,
                "description": description,
                "categoryId": category_id,
            },
            "status": {"privacyStatus": privacy_status},
        }
        # Upload video via httpx multipart
        async with aiofiles.open(video_path, "rb") as fh:
            video_bytes = await fh.read()

        resp = await self._http.post(
            "https://www.googleapis.com/upload/youtube/v3/videos",
            params={"part": "snippet,status", "uploadType": "multipart"},
            headers={**self._auth_headers(), "Content-Type": "multipart/related"},
            content=video_bytes,
        )
        resp.raise_for_status()
        return resp.json()

    async def update_video(self, video_id: str, title: str, description: str) -> dict[str, Any]:
        import json

        payload = {
            "id": video_id,
            "snippet": {"title": title, "description": description, "categoryId": "22"},
        }
        resp = await self._http.put(
            "/videos",
            params=self._key_params({"part": "snippet"}),
            headers=self._auth_headers(),
            content=json.dumps(payload),
        )
        resp.raise_for_status()
        return resp.json()

    async def delete_video(self, video_id: str) -> bool:
        resp = await self._http.delete(
            f"/videos",
            params=self._key_params({"id": video_id}),
            headers=self._auth_headers(),
        )
        return resp.status_code == 204
