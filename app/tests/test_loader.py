from app.infrastructure.loaders import CSVLoader


class TestCSVLoader:
    """Тесты загрузчика CSV"""

    def test_load_valid_csv(self, temp_csv):
        csv_content = """response_id,submitted_at,product,product_version,platform,score1,score2
1,2024-01-01,Product A,1.0.0,Web,5,4
2,2024-01-02,Product B,2.0.0,Android,4,3"""
        filepath = temp_csv(csv_content)
        loader = CSVLoader()
        df = loader.load(filepath)
        assert df is not None
        assert len(df) == 2

    def test_load_csv_without_header(self, temp_csv):
        csv_content = """R2475,2024-10-04 09:38:32,payments,1.2,Web,BY,returning,3,4
R1114,2024-02-14 23:50:58,Payment,1.2,web,,new,2,3"""
        filepath = temp_csv(csv_content)
        loader = CSVLoader()
        df = loader.load(filepath)
        assert df is not None
        assert len(df) == 2

    def test_load_empty_csv(self, temp_csv):
        filepath = temp_csv("")
        loader = CSVLoader()
        df = loader.load(filepath)
        assert df is None

    def test_load_nonexistent_file(self):
        loader = CSVLoader()
        df = loader.load("nonexistent_file.csv")
        assert df is None
