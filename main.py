import csv
import logging
from pathlib import Path

from mcp.server.fastmcp import FastMCP

logger = logging.getLogger(__name__)

DATA_FILE = Path(__file__).parent / "data" / "sales.csv"
EXPECTED_HEADER = ["Customer", "Amount"]

mcp = FastMCP("Sales MCP Server")

# Cache: (file mtime ns, parsed rows). Invalidated when the CSV is modified.
_cache: tuple[int, list[tuple[str, int]]] | None = None


def _normalize_customer_name(customer_name: str) -> str:
    return customer_name.strip().casefold()


def _load_sales() -> list[tuple[str, int]]:
    """
    Load sales records from the CSV file as (customer, amount) tuples.

    Results are cached and only re-read when the file's modification
    time changes. Malformed data rows are skipped with a warning.
    """
    global _cache

    if not DATA_FILE.exists():
        raise FileNotFoundError(f"Sales data file not found: {DATA_FILE}")

    mtime = DATA_FILE.stat().st_mtime_ns
    if _cache is not None and _cache[0] == mtime:
        return _cache[1]

    records: list[tuple[str, int]] = []
    with open(DATA_FILE, "r", newline="", encoding="utf-8") as f:
        reader = csv.reader(f)
        header = next(reader, None)
        if header != EXPECTED_HEADER:
            raise ValueError(
                f"Expected CSV header {EXPECTED_HEADER!r}, got {header!r}"
            )

        for line_num, row in enumerate(reader, start=2):
            if len(row) != 2:
                logger.warning("Skipping malformed row %d: %r", line_num, row)
                continue
            name, paid = row
            name = name.strip()
            if not name:
                logger.warning("Skipping row %d with blank customer name", line_num)
                continue

            try:
                amount = int(paid)
            except ValueError:
                logger.warning(
                    "Skipping row %d with invalid amount: %r", line_num, row
                )
                continue

            if amount < 0:
                logger.warning("Skipping row %d with negative amount: %r", line_num, row)
                continue

            records.append((name, amount))

    _cache = (mtime, records)
    return records


@mcp.tool()
def get_sales_from_customer(customer_name: str) -> list[int]:
    """
    Get a list of all sales totals for a given customer
    """
    normalized_customer_name = _normalize_customer_name(customer_name)
    sales = [
        paid
        for name, paid in _load_sales()
        if _normalize_customer_name(name) == normalized_customer_name
    ]
    if not sales:
        raise ValueError(
            f"No sales found for customer {customer_name!r}. "
            "Use get_all_customers to list valid names."
        )
    return sales


@mcp.tool()
def get_all_customers() -> list[str]:
    """
    Get a list of all unique customer names
    """
    return sorted({name for name, _ in _load_sales()})


@mcp.tool()
def get_total_spent_by_customer(customer_name: str) -> int:
    """
    Get the total amount spent by a given customer across all sales
    """
    return sum(get_sales_from_customer(customer_name))


@mcp.tool()
def get_total_sales() -> int:
    """
    Get the total amount spent by all customers combined
    """
    return sum(paid for _, paid in _load_sales())


@mcp.tool()
def get_top_customers(n: int = 10) -> list[dict[str, int | str]]:
    """
    Get the top N customers by total spending
    """
    if n < 1:
        raise ValueError(f"n must be a positive integer, got {n}")

    totals: dict[str, int] = {}
    for name, paid in _load_sales():
        totals[name] = totals.get(name, 0) + paid
    sorted_customers = sorted(totals.items(), key=lambda x: x[1], reverse=True)
    return [
        {"name": name, "total_spent": total}
        for name, total in sorted_customers[:n]
    ]


@mcp.tool()
def get_customer_stats(customer_name: str) -> dict[str, int | float | str]:
    """
    Get sales statistics for a given customer: number of sales,
    mean sale amount, and total spent.
    """
    sales = get_sales_from_customer(customer_name)
    return {
        "name": customer_name,
        "count": len(sales),
        "mean": sum(sales) / len(sales),
        "total": sum(sales),
    }


if __name__ == "__main__":
    mcp.run()
