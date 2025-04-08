import os
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime

class Database:
    def __init__(self):
        self.conn = psycopg2.connect(
            host=os.environ.get("POSTGRES_HOST", "localhost"),
            database=os.environ.get("POSTGRES_DB", "pharmacy_tech_db"),
            user=os.environ.get("POSTGRES_USER", "postgres"),
            password=os.environ.get("POSTGRES_PASSWORD", "postgres"),
            port=os.environ.get("POSTGRES_PORT", "5432")
        )
        self.cursor = self.conn.cursor(cursor_factory=RealDictCursor)
        self.create_tables()

    def create_tables(self):
        """Create necessary tables if they don't exist"""
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS candidates (
                id SERIAL PRIMARY KEY,
                name VARCHAR(255),
                position VARCHAR(255),
                location VARCHAR(255),
                profile_link VARCHAR(255) UNIQUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS candidate_details (
                id SERIAL PRIMARY KEY,
                candidate_id INTEGER REFERENCES candidates(id),
                experience TEXT,
                certifications TEXT,
                skills TEXT,
                workplace TEXT,
                score DECIMAL(3,1),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS outreach (
                id SERIAL PRIMARY KEY,
                candidate_id INTEGER REFERENCES candidates(id),
                message_template TEXT,
                strategy TEXT,
                status VARCHAR(50) DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Add indexes for better performance
        self.cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_candidate_score ON candidate_details(score DESC)
        ''')
        
        self.cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_candidate_location ON candidates(location)
        ''')
        
        self.conn.commit()

    def insert_candidate(self, name, position, location, profile_link):
        """Insert a new candidate into the database"""
        try:
            self.cursor.execute(
                "INSERT INTO candidates (name, position, location, profile_link) VALUES (%s, %s, %s, %s) RETURNING id",
                (name, position, location, profile_link)
            )
            candidate_id = self.cursor.fetchone()['id']
            self.conn.commit()
            return candidate_id
        except psycopg2.errors.UniqueViolation:
            self.conn.rollback()
            self.cursor.execute("SELECT id FROM candidates WHERE profile_link = %s", (profile_link,))
            return self.cursor.fetchone()['id']

    def insert_candidate_details(self, candidate_id, experience, certifications, skills, workplace, score=0.0):
        """Insert candidate details"""
        try:
            self.cursor.execute(
                "INSERT INTO candidate_details (candidate_id, experience, certifications, skills, workplace, score) VALUES (%s, %s, %s, %s, %s, %s)",
                (candidate_id, experience, certifications, skills, workplace, score)
            )
            self.conn.commit()
        except Exception as e:
            self.conn.rollback()
            self.update_candidate_details(candidate_id, experience, certifications, skills, workplace)
            self.update_candidate_score(candidate_id, score)

    def update_candidate_details(self, candidate_id, experience, certifications, skills, workplace):
        """Update candidate details"""
        self.cursor.execute("""
            UPDATE candidate_details
            SET experience = %s, certifications = %s, skills = %s, workplace = %s, updated_at = %s
            WHERE candidate_id = %s
        """, (experience, certifications, skills, workplace, datetime.now(), candidate_id))
        
        if self.cursor.rowcount == 0:
            # No existing record to update, insert a new one
            self.insert_candidate_details(candidate_id, experience, certifications, skills, workplace)
        else:
            self.conn.commit()

    def update_candidate_score(self, candidate_id, score):
        """Update candidate score"""
        self.cursor.execute("""
            UPDATE candidate_details
            SET score = %s, updated_at = %s
            WHERE candidate_id = %s
        """, (score, datetime.now(), candidate_id))
        
        if self.cursor.rowcount == 0:
            # No existing record to update, insert a new one with placeholder values
            self.insert_candidate_details(candidate_id, "", "", "", "", score)
        else:
            self.conn.commit()

    def insert_outreach_strategy(self, candidate_id, message_template, strategy):
        """Insert outreach strategy for a candidate"""
        self.cursor.execute(
            "INSERT INTO outreach (candidate_id, message_template, strategy) VALUES (%s, %s, %s)",
            (candidate_id, message_template, strategy)
        )
        self.conn.commit()

    def get_candidates(self, limit=100, offset=0):
        """Get candidates with their details"""
        self.cursor.execute("""
            SELECT c.*, cd.experience, cd.certifications, cd.skills, cd.workplace, cd.score
            FROM candidates c
            LEFT JOIN candidate_details cd ON c.id = cd.candidate_id
            ORDER BY c.id DESC
            LIMIT %s OFFSET %s
        """, (limit, offset))
        return self.cursor.fetchall()

    def get_top_candidates(self, limit=10):
        """Get top candidates based on score"""
        self.cursor.execute("""
            SELECT c.*, cd.experience, cd.certifications, cd.skills, cd.workplace, cd.score
            FROM candidates c
            JOIN candidate_details cd ON c.id = cd.candidate_id
            WHERE cd.score IS NOT NULL
            ORDER BY cd.score DESC
            LIMIT %s
        """, (limit,))
        return self.cursor.fetchall()

    def get_candidate_by_id(self, candidate_id):
        """Get a specific candidate by ID"""
        self.cursor.execute("""
            SELECT c.*, cd.experience, cd.certifications, cd.skills, cd.workplace, cd.score
            FROM candidates c
            LEFT JOIN candidate_details cd ON c.id = cd.candidate_id
            WHERE c.id = %s
        """, (candidate_id,))
        return self.cursor.fetchone()

    def get_statistics(self):
        """Get database statistics"""
        stats = {}
        
        # Total candidates
        self.cursor.execute("SELECT COUNT(*) as count FROM candidates")
        stats['total_candidates'] = self.cursor.fetchone()['count']
        
        # Average score
        self.cursor.execute("SELECT AVG(score) as avg_score FROM candidate_details WHERE score IS NOT NULL")
        avg_score = self.cursor.fetchone()['avg_score']
        stats['average_score'] = avg_score if avg_score else 0
        
        # Candidates with certifications
        self.cursor.execute("""
            SELECT COUNT(*) as count FROM candidate_details
            WHERE certifications IS NOT NULL AND certifications != ''
        """)
        stats['with_certifications'] = self.cursor.fetchone()['count']
        
        # Top locations
        self.cursor.execute("""
            SELECT location, COUNT(*) as count FROM candidates
            GROUP BY location
            ORDER BY count DESC
            LIMIT 5
        """)
        top_locations = self.cursor.fetchall()
        stats['top_locations'] = [loc['location'] for loc in top_locations]
        
        # Top workplaces
        self.cursor.execute("""
            SELECT workplace, COUNT(*) as count FROM candidate_details
            WHERE workplace IS NOT NULL AND workplace != ''
            GROUP BY workplace
            ORDER BY count DESC
            LIMIT 5
        """)
        top_workplaces = self.cursor.fetchall()
        stats['top_workplaces'] = [wp['workplace'] for wp in top_workplaces]
        
        return stats

    def close(self):
        """Close database connection"""
        self.cursor.close()
        self.conn.close()