from typing import Dict, List, Optional
import sqlite3


class TicketDatabase:
    def __init__(self, db_path: str = "tickets.db"):
        self.db_path = db_path
        self.init_db()

    def init_db(self):
        """Инициализация базы данных"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tickets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                username TEXT,
                first_name TEXT,
                last_name TEXT,
                full_name TEXT NOT NULL,
                department TEXT NOT NULL,
                contact TEXT NOT NULL,
                photo TEXT,
                inventory_number TEXT,
                category TEXT NOT NULL,
                issue_type TEXT NOT NULL,
                problem TEXT NOT NULL,
                description TEXT,
                status TEXT DEFAULT 'open',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        conn.commit()
        conn.close()

    def create_ticket(self, user_id: int, username: str, first_name: str,
                      last_name: str, full_name: str, department: str,
                      contact: str, photo: str, inventory_number: str,
                      category: str, issue_type: str, problem: str,
                      description: str = None) -> int:
        """Создание новой заявки"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO tickets 
            (user_id, username, first_name, last_name, full_name, department, 
             contact, photo, inventory_number, category, issue_type, problem, description)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (user_id, username, first_name, last_name, full_name, department,
              contact, photo, inventory_number, category, issue_type, problem, description))

        ticket_id = cursor.lastrowid
        conn.commit()
        conn.close()

        return ticket_id

    def get_ticket(self, ticket_id: int) -> Optional[Dict]:
        """Получение заявки по ID"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('SELECT * FROM tickets WHERE id = ?', (ticket_id,))
        row = cursor.fetchone()
        conn.close()

        if row:
            return {
                'id': row[0],
                'user_id': row[1],
                'username': row[2],
                'first_name': row[3],
                'last_name': row[4],
                'full_name': row[5],
                'department': row[6],
                'contact': row[7],
                'photo': row[8],
                'inventory_number': row[9],
                'category': row[10],
                'issue_type': row[11],
                'problem': row[12],
                'description': row[13],
                'status': row[14],
                'created_at': row[15],
                'updated_at': row[16]
            }
        return None

    def update_ticket_status(self, ticket_id: int, status: str):
        """Обновление статуса заявки"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            UPDATE tickets 
            SET status = ?, updated_at = CURRENT_TIMESTAMP 
            WHERE id = ?
        ''', (status, ticket_id))

        conn.commit()
        conn.close()

    def get_user_tickets(self, user_id: int) -> List[Dict]:
        """Получение заявок пользователя"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('SELECT * FROM tickets WHERE user_id = ? ORDER BY created_at DESC', (user_id,))
        rows = cursor.fetchall()
        conn.close()

        tickets = []
        for row in rows:
            tickets.append({
                'id': row[0],
                'user_id': row[1],
                'username': row[2],
                'first_name': row[3],
                'last_name': row[4],
                'full_name': row[5],
                'department': row[6],
                'contact': row[7],
                'photo': row[8],
                'inventory_number': row[9],
                'category': row[10],
                'issue_type': row[11],
                'problem': row[12],
                'description': row[13],
                'status': row[14],
                'created_at': row[15],
                'updated_at': row[16]
            })

        return tickets