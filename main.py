
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


if __name__ == "__main()__":
    mcp.run()