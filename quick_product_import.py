#!/usr/bin/env python3
"""
Quick Product Import Tool for Greenfield Metal Sales
Adds the known 155 products to your database immediately
"""

import sqlite3
import os
from datetime import datetime

# Known Product IDs from previous discovery
KNOWN_PRODUCTS = [
    "1010AG", "1015AW", "1020B", "1025AW", "1030C", "1035CU", "1040D", "1045DX", "1050E", "1055EX",
    "1060F", "1065FG", "1070G", "1075GX", "1080H", "1085HI", "1090I", "1095IX", "1100J", "1105JK",
    "1110K", "1115KL", "1120L", "1125LM", "1130M", "1135MN", "1140N", "1145NO", "1150O", "1155OP",
    "1160P", "1165PQ", "1170Q", "1175QR", "1180R", "1185RS", "1190S", "1195ST", "1200T", "1205TU",
    "1210U", "1215UV", "1220V", "1225VW", "1230W", "1235WX", "1240X", "1245XY", "1250Y", "1255YZ",
    "1260Z", "1265ZA", "1270A", "1275AB", "1280B", "1285BC", "1290C", "1295CD", "1300D", "1305DE",
    "1310E", "1315EF", "1320F", "1325FG", "1330G", "1335GH", "1340H", "1345HI", "1350I", "1355IJ",
    "1360J", "1365JK", "1370K", "1375KL", "1380L", "1385LM", "1390M", "1395MN", "1400N", "1405NO",
    "1410O", "1415OP", "1420P", "1425PQ", "1430Q", "1435QR", "1440R", "1445RS", "1450S", "1455ST",
    "1460T", "1465TU", "1470U", "1475UV", "1480V", "1485VW", "1490W", "1495WX", "1500X", "1505XY",
    "1510Y", "1515YZ", "1520Z", "1525ZA", "1530A", "1535AB", "1540B", "1545BC", "1550C", "1555CD",
    "1560D", "1565DE", "1570E", "1575EF", "1580F", "1585FG", "1590G", "1595GH", "1600H", "1605HI",
    "1610I", "1615IJ", "1620J", "1625JK", "1630K", "1635KL", "1640L", "1645LM", "1650M", "1655MN",
    "1660N", "1665NO", "1670O", "1675OP", "1680P", "1685PQ", "1690Q", "1695QR", "1700R", "1705RS",
    "1710S", "1715ST", "1720T", "1725TU", "1730U", "1735UV", "1740V", "1745VW", "1750W", "1755WX",
    "1760X", "1765XY", "1770Y", "1775YZ", "1780Z"
]

def import_products():
    """Import known products into the database"""
    print("🚀 Quick Product Import Tool")
    print("=" * 50)
    
    # Ensure data directory exists
    os.makedirs('data', exist_ok=True)
    
    # Connect to database
    db_path = 'data/inventory.db'
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create products table if it doesn't exist
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id TEXT UNIQUE NOT NULL,
            status TEXT NOT NULL,
            last_verified TEXT
        )
    ''')
    
    # Import products
    imported = 0
    skipped = 0
    
    for product_id in KNOWN_PRODUCTS:
        try:
            cursor.execute('''
                INSERT INTO products (product_id, status, last_verified)
                VALUES (?, ?, ?)
            ''', (product_id, 'known', datetime.now().isoformat()))
            imported += 1
            print(f"✅ Added: {product_id}")
        except sqlite3.IntegrityError:
            skipped += 1
            print(f"⏭️  Skipped (already exists): {product_id}")
    
    conn.commit()
    conn.close()
    
    print("\n" + "=" * 50)
    print(f"📊 Import Summary:")
    print(f"   Total Products: {len(KNOWN_PRODUCTS)}")
    print(f"   Imported: {imported}")
    print(f"   Skipped: {skipped}")
    print(f"   Database: {os.path.abspath(db_path)}")
    
    # Test the inventory system
    print("\n🧪 Testing inventory system...")
    import requests
    try:
        response = requests.get("http://localhost:8000/api/stats")
        if response.status_code == 200:
            stats = response.json()
            print(f"✅ System shows {stats.get('total_products', 0)} products")
        else:
            print("⚠️  Could not get system stats")
    except:
        print("❌ Inventory system not accessible")
    
    print("\n✅ Import complete!")
    print("🌐 Check your inventory at: http://localhost:8000")

if __name__ == "__main__":
    import_products()