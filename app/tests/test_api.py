import pytest
import tempfile
import os


class TestUpload:
    """Тесты загрузки файлов"""

    @pytest.mark.asyncio
    async def test_upload_valid_csv(self, client, test_csv_file):
        with open(test_csv_file, 'rb') as f:
            content = f.read()
        files = {'files': ('test.csv', content, 'text/csv')}
        response = await client.post("/api/v1/upload", files=files)

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["total_valid"] == 5

    @pytest.mark.asyncio
    async def test_upload_invalid_file_type(self, client):
        content = b"test content"
        files = {'files': ('test.txt', content, 'text/plain')}
        response = await client.post("/api/v1/upload", files=files)

        assert response.status_code == 400
        data = response.json()
        assert "detail" in data

    @pytest.mark.asyncio
    async def test_upload_empty_file(self, client):
        content = b""
        files = {'files': ('empty.csv', content, 'text/csv')}
        response = await client.post("/api/v1/upload", files=files)

        assert response.status_code == 400
        data = response.json()
        assert "пуст" in data["detail"].lower()

    @pytest.mark.asyncio
    async def test_upload_multiple_files(self, client):
        csv_content_1 = """response_id,submitted_at,product,product_version,platform,score1,score2
RESP-A1,2024-01-15 10:30:00,Product A,1.0.0,Web,5,4
RESP-A2,2024-01-15 11:00:00,Product B,2.0.0,Android,4,3"""

        csv_content_2 = """response_id,submitted_at,product,product_version,platform,score1,score2
RESP-B1,2024-01-16 09:00:00,Product C,3.0.0,iOS,5,5
RESP-B2,2024-01-17 14:30:00,Product A,1.0.1,web,4,4"""

        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write(csv_content_1)
            file1 = f.name

        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write(csv_content_2)
            file2 = f.name

        try:
            with open(file1, 'rb') as f:
                content1 = f.read()
            with open(file2, 'rb') as f:
                content2 = f.read()

            files = [
                ('files', ('test_1.csv', content1, 'text/csv')),
                ('files', ('test_2.csv', content2, 'text/csv'))
            ]

            response = await client.post("/api/v1/upload", files=files)
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "success"
            assert data["total_valid"] == 4

        finally:
            os.unlink(file1)
            os.unlink(file2)


class TestDashboard:
    """Тесты дашборда"""

    @pytest.mark.asyncio
    async def test_dashboard_not_found(self, client):
        if os.path.exists("results/dashboard.html"):
            os.remove("results/dashboard.html")
        if os.path.exists("dashboard.html"):
            os.remove("dashboard.html")

        response = await client.get("/api/v1/dashboard")
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_dashboard_after_upload(self, client, test_csv_file):
        with open(test_csv_file, 'rb') as f:
            content = f.read()
        files = {'files': ('test.csv', content, 'text/csv')}
        await client.post("/api/v1/upload", files=files)

        response = await client.get("/api/v1/dashboard")
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]
