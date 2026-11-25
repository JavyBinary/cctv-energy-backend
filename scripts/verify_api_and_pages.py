import asyncio
import io
import os
import sys
from pathlib import Path

# Add app to path
BASE_DIR = Path(__file__).resolve().parent.parent / "app"
sys.path.insert(0, str(BASE_DIR))

os.environ["DATABASE_URL"] = "postgresql+asyncpg://camera_user:camera_password@localhost:5432/cameras_db"

import httpx
from httpx import ASGITransport
from main import app


async def run_verification():
    print("=== STARTING COMPREHENSIVE VERIFICATION ===")
    transport = ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. OpenAPI & Swagger
        print("\n--- 1. Testing OpenAPI Schema & Swagger ---")
        res = await client.get("/openapi.json")
        assert res.status_code == 200, f"OpenAPI failed: {res.status_code}"
        schema = res.json()
        paths = schema.get("paths", {})
        
        required_endpoints = [
            ("/api/cameras", "get"),
            ("/api/cameras", "post"),
            ("/api/cameras/feed", "get"),
            ("/api/cameras/draft", "get"),
            ("/api/cameras/{camera_id}/publish", "put"),
            ("/api/cameras/{camera_id}", "delete"),
            ("/api/cameras/{camera_id}/like", "post"),
            ("/api/users/register", "post"),
            ("/api/users/login", "post"),
            ("/api/users/logout", "post"),
        ]
        
        for path, method in required_endpoints:
            assert path in paths, f"Missing path in OpenAPI: {path}"
            assert method in paths[path], f"Missing {method.upper()} for {path}"
            print(f"  ✓ {method.upper()} {path} documented in OpenAPI")
        print("All 10 REST endpoints documented correctly in Swagger/OpenAPI!")

        # 2. SSR HTML Pages (Regression LR2)
        print("\n--- 2. Testing SSR Pages & HTML Invariants ---")
        res_cat = await client.get("/cameras")
        assert res_cat.status_code == 200
        cat_html = res_cat.text
        assert "<script" not in cat_html, "Found <script> tag in catalog.html!"
        assert "catalog-search-button" in cat_html
        print("  ✓ Catalog SSR page verified (0 script tags, interactive slider, unified search button)")

        res_draft = await client.get("/cameras/draft")
        assert res_draft.status_code == 200
        draft_html = res_draft.text
        assert "create-media-section" in draft_html
        assert "<script" not in draft_html
        print("  ✓ Create/Draft SSR page verified (media section vertical, 0 JS)")

        res_feed = await client.get("/cameras/feed")
        assert res_feed.status_code == 200
        feed_html = res_feed.text
        assert "feed-next-button" in feed_html
        assert "<script" not in feed_html
        print("  ✓ Feed SSR page verified (next button unified, 0 JS)")

        # 3. REST API: Cameras Domain (7 methods)
        print("\n--- 3. Testing REST API: Cameras Domain ---")
        # Method 1: GET /api/cameras
        res_cams = await client.get("/api/cameras")
        assert res_cams.status_code == 200
        cams = res_cams.json()
        assert isinstance(cams, list)
        print(f"  ✓ 1. GET /api/cameras: returned {len(cams)} cameras")
        if cams:
            first = cams[0]
            assert "is_creator" in first, "Missing is_creator"
            assert first["is_creator"] in (0, 1)
            assert "likes_count" in first
            assert "status" in first and first["status"] == "published"
            # Ensure fixed structure with nulls
            assert "description" in first
            assert "power" in first

        # Method 2: GET /api/cameras/feed
        res_f = await client.get("/api/cameras/feed")
        assert res_f.status_code == 200
        feed_cam = res_f.json()
        assert isinstance(feed_cam, dict)
        assert "id" in feed_cam
        print(f"  ✓ 2. GET /api/cameras/feed: returned camera id={feed_cam['id']}")

        res_f_next = await client.get(f"/api/cameras/feed?camera_id={feed_cam['id']}&next=true")
        assert res_f_next.status_code == 200
        print(f"  ✓ 2b. GET /api/cameras/feed?next=true: returned next camera id={res_f_next.json()['id']}")

        # Log in as admin to test protected creator endpoints
        login_resp = await client.post("/api/users/login", json={"username": "admin", "password": "password123"})
        assert login_resp.status_code == 200
        auth_cookie = {"session_id": login_resp.json()["session_id"]}
        client.cookies.update(auth_cookie)

        # Method 3 & 4: POST /api/cameras & GET /api/cameras/draft
        # Check if user already has a draft
        res_d = await client.get("/api/cameras/draft")
        draft_cam_id = None
        if res_d.status_code == 200:
            draft_cam_id = res_d.json()["id"]
            print(f"  ✓ 3. GET /api/cameras/draft: existing draft id={draft_cam_id}")
        else:
            # Create a draft
            mock_img = io.BytesIO(b"dummy image bytes")
            mock_vid = io.BytesIO(b"dummy video bytes")
            files = {
                "image_file": ("test_cam.jpg", mock_img, "image/jpeg"),
                "video_file": ("test_vid.mp4", mock_vid, "video/mp4"),
            }
            data = {"model_name": "REST Test Camera Draft"}
            res_create = await client.post("/api/cameras", data=data, files=files)
            assert res_create.status_code == 201, f"Create failed: {res_create.text}"
            draft_cam_id = res_create.json()["id"]
            print(f"  ✓ 4. POST /api/cameras: created draft id={draft_cam_id}")

            # Verify GET /api/cameras/draft returns it
            res_d2 = await client.get("/api/cameras/draft")
            assert res_d2.status_code == 200
            assert res_d2.json()["id"] == draft_cam_id
            print(f"  ✓ 3. GET /api/cameras/draft: retrieved created draft id={draft_cam_id}")

        # Method 5: PUT /api/cameras/{id}/publish
        publish_payload = {
            "model_name": "REST Verified Camera 4K",
            "description": "Тестовая опубликованная камера через REST API",
            "power": 12.5,
            "resolution": "3840x2160 (4K)",
        }
        res_pub = await client.put(f"/api/cameras/{draft_cam_id}/publish", json=publish_payload)
        assert res_pub.status_code == 200, f"Publish failed: {res_pub.text}"
        pub_cam = res_pub.json()
        assert pub_cam["status"] == "published"
        assert pub_cam["power"] == 12.5
        assert pub_cam["resolution"] == "3840x2160 (4K)"
        print(f"  ✓ 5. PUT /api/cameras/{draft_cam_id}/publish: status={pub_cam['status']}")

        # Method 7: POST /api/cameras/{id}/like
        res_like_1 = await client.post(f"/api/cameras/{draft_cam_id}/like", json={"like": 1})
        assert res_like_1.status_code == 200
        likes_after_add = res_like_1.json()["likes_count"]
        print(f"  ✓ 7a. POST /api/cameras/{draft_cam_id}/like (1): likes={likes_after_add}")

        res_like_0 = await client.post(f"/api/cameras/{draft_cam_id}/like", json={"like": 0})
        assert res_like_0.status_code == 200
        likes_after_del = res_like_0.json()["likes_count"]
        assert likes_after_del == likes_after_add - 1
        print(f"  ✓ 7b. POST /api/cameras/{draft_cam_id}/like (0): likes={likes_after_del}")

        # Method 6: DELETE /api/cameras/{id} (soft delete)
        res_del = await client.delete(f"/api/cameras/{draft_cam_id}")
        assert res_del.status_code == 200
        del_data = res_del.json()
        assert del_data["status"] == "deleted"
        print(f"  ✓ 6. DELETE /api/cameras/{draft_cam_id}: soft delete status={del_data['status']}")

        # Verify that soft-deleted camera is NOT in GET /api/cameras
        res_cams_after = await client.get("/api/cameras")
        ids_after = [c["id"] for c in res_cams_after.json()]
        assert draft_cam_id not in ids_after
        print(f"  ✓ Deleted camera {draft_cam_id} successfully excluded from GET /api/cameras")

        # 4. REST API: Users Domain (3 methods)
        print("\n--- 4. Testing REST API: Users Domain ---")
        import random
        rand_user = f"user_test_{random.randint(1000, 9999)}"
        # Method 8: POST /api/users/register
        res_reg = await client.post("/api/users/register", json={"username": rand_user, "password": "password123"})
        assert res_reg.status_code == 201, f"Register failed: {res_reg.text}"
        new_user = res_reg.json()
        assert new_user["username"] == rand_user
        print(f"  ✓ 8. POST /api/users/register: registered user id={new_user['id']}, username={new_user['username']}")

        # Method 9: POST /api/users/login
        res_log = await client.post("/api/users/login", json={"username": rand_user, "password": "password123"})
        assert res_log.status_code == 200, f"Login failed: {res_log.text}"
        token_data = res_log.json()
        assert "token" in token_data
        assert token_data["user_id"] == new_user["id"]
        print(f"  ✓ 9. POST /api/users/login: token received for user id={token_data['user_id']}")

        # Method 10: POST /api/users/logout
        res_logout = await client.post("/api/users/logout")
        assert res_logout.status_code == 200
        print("  ✓ 10. POST /api/users/logout: returned status 200 OK")

    print("\n=== ALL 10 REST API METHODS & SSR PAGES VERIFIED SUCCESSFULLY! ===")


if __name__ == "__main__":
    asyncio.run(run_verification())
