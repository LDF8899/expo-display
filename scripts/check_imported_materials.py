import sqlite3


conn = sqlite3.connect("expo.db")

print("module counts")
for row in conn.execute(
    """
    SELECT p.name, ci.module_key, COUNT(*)
    FROM projects p
    JOIN content_items ci ON ci.project_id = p.id
    WHERE ci.enabled = 1
    GROUP BY p.id, ci.module_key
    ORDER BY p.id, ci.module_key
    """
):
    print(row)

print("\nshort titles")
for row in conn.execute(
    """
    SELECT p.name, ci.module_key, ci.title, LENGTH(ci.summary)
    FROM content_items ci
    JOIN projects p ON p.id = ci.project_id
    WHERE ci.code LIKE 'MAT-%' AND LENGTH(ci.title) <= 2
    ORDER BY ci.project_id, ci.sort_order
    LIMIT 30
    """
):
    print(row)

print("\nsamples")
for row in conn.execute(
    """
    SELECT p.name, ci.module_key, ci.title, SUBSTR(ci.summary, 1, 80)
    FROM content_items ci
    JOIN projects p ON p.id = ci.project_id
    WHERE ci.code LIKE 'MAT-%'
    ORDER BY ci.project_id, ci.sort_order
    LIMIT 120
    """
):
    print(row)

print("\nasset counts")
print("assets", conn.execute("SELECT COUNT(*) FROM assets WHERE storage_key LIKE 'imported-materials/%'").fetchone()[0])
print("content_item_assets", conn.execute("SELECT COUNT(*) FROM content_item_assets WHERE url LIKE '/uploads/imported-materials/%'").fetchone()[0])

print("\ncoverage")
print("mat_total", conn.execute("SELECT COUNT(*) FROM content_items WHERE code LIKE 'MAT-%'").fetchone()[0])
print(
    "mat_without_assets",
    conn.execute(
        """
        SELECT COUNT(*)
        FROM content_items ci
        WHERE ci.code LIKE 'MAT-%'
          AND NOT EXISTS (SELECT 1 FROM content_item_assets cia WHERE cia.content_item_id = ci.id)
        """
    ).fetchone()[0],
)
print("market_total", conn.execute("SELECT COUNT(*) FROM achievement_market_items").fetchone()[0])
for row in conn.execute("SELECT category_key, COUNT(*) FROM achievement_market_items GROUP BY category_key ORDER BY category_key"):
    print("market_category", row)
print(
    "market_without_images",
    conn.execute(
        """
        SELECT COUNT(*)
        FROM pages p
        JOIN achievement_market_items ami ON ami.page_id = p.id
        WHERE p.image_url = ''
        """
    ).fetchone()[0],
)
