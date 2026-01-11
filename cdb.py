import sqlite3


class CourseDatabase:
    def __init__(self, db_name='courses.db', table_name='completed_courses'):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self.create_table(table_name)

    def create_table(self, table_name):
        with self.conn:
            self.conn.execute(f'''
                CREATE TABLE IF NOT EXISTS {table_name} (
                    id INTEGER PRIMARY KEY,
                    name TEXT NOT NULL
                )
            ''')

    def add_completed_course(self, table_name, course_id, course_name):
        with self.conn:
            self.conn.execute(f'''
                INSERT OR IGNORE INTO {table_name} (id, name)
                VALUES (?, ?)
            ''', (course_id, course_name))

    def is_course_completed(self, table_name, course_id):
        self.cursor.execute(f'SELECT 1 FROM {table_name} WHERE id = ?', (course_id,))
        return self.cursor.fetchone() is not None

    def close(self):
        self.connection.close()
