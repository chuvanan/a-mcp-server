
import csv
from mcp.server.fastmcp import FastMCP


mcp = FastMCP("Sales MCP Server")

@mcp.tool()
def get_sales_from_customer(customer_name: str) -> list[int]:
    """
    Get a list of all sales totals for a given customer
    """

    sales: list[int] = []
    with open("data/sales.csv", "r") as f:
        reader = csv.reader(f)
        for name, paid in reader:
            if name == customer_name:
                sales.append(int(paid))
    return sales



@mcp.tool()
def get_all_customers() -> list[str]:
    """
    Get a list of all unique customer names
    """
    customers: set[str] = set()
    with open("data/sales.csv", "r") as f:
        reader = csv.reader(f)
        next(reader)  # skip header
        for name, _ in reader:
            customers.add(name)
    return sorted(customers)


@mcp.tool()
def get_total_spent_by_customer(customer_name: str) -> int:
    """
    Get the total amount spent by a given customer across all sales
    """
    total = 0
    with open("data/sales.csv", "r") as f:
        reader = csv.reader(f)
        for name, paid in reader:
            if name == customer_name:
                total += int(paid)
    return total


@mcp.tool()
def get_total_sales() -> int:
    """
    Get the total amount spent by all customers combined
    """
    total = 0
    with open("data/sales.csv", "r") as f:
        reader = csv.reader(f)
        next(reader)  # skip header
        for _, paid in reader:
            total += int(paid)
    return total


@mcp.tool()
def get_top_customers(n: int = 10) -> list[dict[str, int | str]]:
    """
    Get the top N customers by total spending
    """
    totals: dict[str, int] = {}
    with open("data/sales.csv", "r") as f:
        reader = csv.reader(f)
        next(reader)  # skip header
        for name, paid in reader:
            totals[name] = totals.get(name, 0) + int(paid)
    sorted_customers = sorted(totals.items(), key=lambda x: x[1], reverse=True)
    return [{"name": name, "total_spent": total} for name, total in sorted_customers[:n]]


if __name__ == "__main__":
    mcp.run()