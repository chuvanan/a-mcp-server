import pytest

import main


SAMPLE_CSV = """\
Customer,Amount
Alice,100
Bob,200
Alice,300
Carol,50
"""


@pytest.fixture
def sales_file(tmp_path, monkeypatch):
    """Point the server at a small temp CSV and reset the cache."""
    data_file = tmp_path / "sales.csv"
    data_file.write_text(SAMPLE_CSV)
    monkeypatch.setattr(main, "DATA_FILE", data_file)
    monkeypatch.setattr(main, "_cache", None)
    return data_file


class TestGetAllCustomers:
    def test_returns_sorted_unique_names(self, sales_file):
        assert main.get_all_customers() == ["Alice", "Bob", "Carol"]


class TestGetSalesFromCustomer:
    def test_returns_all_sales(self, sales_file):
        assert main.get_sales_from_customer("Alice") == [100, 300]

    def test_lookup_is_case_insensitive_and_strips_input(self, sales_file):
        assert main.get_sales_from_customer(" alice ") == [100, 300]

    def test_unknown_customer_raises(self, sales_file):
        with pytest.raises(ValueError, match="No sales found"):
            main.get_sales_from_customer("Nobody")


class TestGetTotalSpentByCustomer:
    def test_sums_sales(self, sales_file):
        assert main.get_total_spent_by_customer("Alice") == 400

    def test_unknown_customer_raises(self, sales_file):
        with pytest.raises(ValueError, match="No sales found"):
            main.get_total_spent_by_customer("Nobody")


class TestGetTotalSales:
    def test_sums_all_sales(self, sales_file):
        assert main.get_total_sales() == 650


class TestGetTopCustomers:
    def test_orders_by_total_spent(self, sales_file):
        assert main.get_top_customers(2) == [
            {"name": "Alice", "total_spent": 400},
            {"name": "Bob", "total_spent": 200},
        ]

    def test_n_larger_than_customer_count(self, sales_file):
        assert len(main.get_top_customers(100)) == 3

    @pytest.mark.parametrize("n", [0, -5])
    def test_invalid_n_raises(self, sales_file, n):
        with pytest.raises(ValueError, match="positive integer"):
            main.get_top_customers(n)


class TestGetCustomerStats:
    def test_returns_count_mean_total(self, sales_file):
        assert main.get_customer_stats("Alice") == {
            "name": "Alice",
            "count": 2,
            "mean": 200.0,
            "total": 400,
        }

    def test_unknown_customer_raises(self, sales_file):
        with pytest.raises(ValueError, match="No sales found"):
            main.get_customer_stats("Nobody")


class TestLoadSales:
    def test_missing_file_raises(self, tmp_path, monkeypatch):
        monkeypatch.setattr(main, "DATA_FILE", tmp_path / "missing.csv")
        monkeypatch.setattr(main, "_cache", None)
        with pytest.raises(FileNotFoundError, match="missing.csv"):
            main._load_sales()

    def test_invalid_header_raises(self, sales_file):
        sales_file.write_text("Name,Amount\nAlice,100\n")
        with pytest.raises(ValueError, match="Expected CSV header"):
            main._load_sales()

    def test_skips_malformed_rows(self, sales_file, caplog):
        sales_file.write_text(
            "Customer,Amount\n"
            "Alice,100\n"
            "BadRowWithOneColumn\n"
            "Bob,not_a_number\n"
            ",100\n"
            "Dave,-5\n"
            "Carol,50\n"
        )
        with caplog.at_level("WARNING"):
            records = main._load_sales()
        assert records == [("Alice", 100), ("Carol", 50)]
        assert len(caplog.records) == 4

    def test_strips_whitespace_from_names(self, sales_file):
        sales_file.write_text("Customer,Amount\n Alice ,100\n")
        assert main._load_sales() == [("Alice", 100)]

    def test_cache_reused_when_file_unchanged(self, sales_file):
        first = main._load_sales()
        assert main._load_sales() is first

    def test_cache_invalidated_on_modification(self, sales_file):
        main._load_sales()
        sales_file.write_text("Customer,Amount\nDave,999\n")
        # Force a different mtime in case writes happen within timer resolution.
        import os

        mtime = sales_file.stat().st_mtime
        os.utime(sales_file, (mtime + 1, mtime + 1))
        assert main._load_sales() == [("Dave", 999)]
