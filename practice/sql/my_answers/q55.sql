-- Q55: Quietest days of 2025  [Hard]
-- Days with zero orders don't appear in orders, so a plain GROUP BY hides them. Build a calendar of every date in 2025 with a recursive CTE, LEFT JOIN valid orders, and return the 5 dates with the fewest valid orders: day, valid_orders (fewest first, then earliest date).
-- Expected columns: day, valid_orders

