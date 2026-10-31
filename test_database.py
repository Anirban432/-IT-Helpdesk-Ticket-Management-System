"""SQLite schema smoke test; run with: python test_database.py"""
import sqlite3

conn = sqlite3.connect(':memory:')
conn.execute('''CREATE TABLE tickets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    requester TEXT NOT NULL, email TEXT NOT NULL, title TEXT NOT NULL,
    description TEXT NOT NULL, category TEXT NOT NULL, priority TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'Open', assigned_to TEXT DEFAULT '',
    resolution TEXT DEFAULT '', created_at TEXT NOT NULL, updated_at TEXT NOT NULL
)''')
conn.execute('''CREATE TABLE ticket_notes (
    id INTEGER PRIMARY KEY AUTOINCREMENT, ticket_id INTEGER NOT NULL,
    note TEXT NOT NULL, author TEXT NOT NULL, created_at TEXT NOT NULL,
    FOREIGN KEY(ticket_id) REFERENCES tickets(id) ON DELETE CASCADE
)''')
cur = conn.execute('''INSERT INTO tickets
    (requester,email,title,description,category,priority,status,assigned_to,created_at,updated_at)
    VALUES (?,?,?,?,?,?, 'Open',?,?,?)''',
    ('Demo User','demo@example.com','Wi-Fi issue','Cannot connect','Network','High','','2026-10-31','2026-10-31'))
ticket_id = cur.lastrowid
conn.execute('INSERT INTO ticket_notes(ticket_id,note,author,created_at) VALUES(?,?,?,?)',
             (ticket_id,'Checked adapter and IP configuration','Demo Technician','2026-10-31'))
assert conn.execute('SELECT status FROM tickets WHERE id=?',(ticket_id,)).fetchone()[0] == 'Open'
assert conn.execute('SELECT COUNT(*) FROM ticket_notes WHERE ticket_id=?',(ticket_id,)).fetchone()[0] == 1
conn.execute("UPDATE tickets SET status='Resolved' WHERE id=?",(ticket_id,))
assert conn.execute('SELECT status FROM tickets WHERE id=?',(ticket_id,)).fetchone()[0] == 'Resolved'
conn.close()
print('PASS: ticket creation, notes, status update and SQLite schema.')
