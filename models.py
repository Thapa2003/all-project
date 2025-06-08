import sqlite3
import os
from datetime import datetime
from typing import List, Optional

class SoilTest:
    """Soil test data model"""
    
    def __init__(self, location: str, ph: float, nitrogen: float, phosphorus: float, 
                 potassium: float, latitude: Optional[float] = None, 
                 longitude: Optional[float] = None, notes: str = "", 
                 test_date: str = None, id: Optional[int] = None):
        self.id = id
        self.location = location
        self.latitude = latitude
        self.longitude = longitude
        self.ph = ph
        self.nitrogen = nitrogen
        self.phosphorus = phosphorus
        self.potassium = potassium
        self.notes = notes
        self.test_date = test_date or datetime.now().strftime('%Y-%m-%d')
    
    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'location': self.location,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'ph': self.ph,
            'nitrogen': self.nitrogen,
            'phosphorus': self.phosphorus,
            'potassium': self.potassium,
            'notes': self.notes,
            'testDate': self.test_date
        }
    
    @classmethod
    def from_dict(cls, data: dict):
        """Create SoilTest from dictionary"""
        return cls(
            id=data.get('id'),
            location=data['location'],
            latitude=data.get('latitude'),
            longitude=data.get('longitude'),
            ph=data['ph'],
            nitrogen=data['nitrogen'],
            phosphorus=data['phosphorus'],
            potassium=data['potassium'],
            notes=data.get('notes', ''),
            test_date=data.get('testDate')
        )

class SoilTestDB:
    """Database operations for soil tests"""
    
    def __init__(self, db_path: str = 'soil_tests.db'):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize the database with required tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS soil_tests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                location TEXT NOT NULL,
                latitude REAL,
                longitude REAL,
                ph REAL NOT NULL,
                nitrogen REAL NOT NULL,
                phosphorus REAL NOT NULL,
                potassium REAL NOT NULL,
                notes TEXT,
                test_date TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def create_test(self, soil_test: SoilTest) -> int:
        """Create a new soil test and return its ID"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO soil_tests (location, latitude, longitude, ph, nitrogen, 
                                  phosphorus, potassium, notes, test_date)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            soil_test.location,
            soil_test.latitude,
            soil_test.longitude,
            soil_test.ph,
            soil_test.nitrogen,
            soil_test.phosphorus,
            soil_test.potassium,
            soil_test.notes,
            soil_test.test_date
        ))
        
        test_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return test_id
    
    def get_all_tests(self) -> List[SoilTest]:
        """Get all soil tests"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, location, latitude, longitude, ph, nitrogen, 
                   phosphorus, potassium, notes, test_date
            FROM soil_tests
            ORDER BY test_date DESC, id DESC
        ''')
        
        rows = cursor.fetchall()
        conn.close()
        
        tests = []
        for row in rows:
            test = SoilTest(
                id=row[0],
                location=row[1],
                latitude=row[2],
                longitude=row[3],
                ph=row[4],
                nitrogen=row[5],
                phosphorus=row[6],
                potassium=row[7],
                notes=row[8],
                test_date=row[9]
            )
            tests.append(test)
        
        return tests
    
    def get_test_by_id(self, test_id: int) -> Optional[SoilTest]:
        """Get a specific soil test by ID"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, location, latitude, longitude, ph, nitrogen, 
                   phosphorus, potassium, notes, test_date
            FROM soil_tests
            WHERE id = ?
        ''', (test_id,))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return SoilTest(
                id=row[0],
                location=row[1],
                latitude=row[2],
                longitude=row[3],
                ph=row[4],
                nitrogen=row[5],
                phosphorus=row[6],
                potassium=row[7],
                notes=row[8],
                test_date=row[9]
            )
        
        return None
    
    def update_test(self, soil_test: SoilTest) -> bool:
        """Update an existing soil test"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE soil_tests 
            SET location = ?, latitude = ?, longitude = ?, ph = ?, 
                nitrogen = ?, phosphorus = ?, potassium = ?, notes = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (
            soil_test.location,
            soil_test.latitude,
            soil_test.longitude,
            soil_test.ph,
            soil_test.nitrogen,
            soil_test.phosphorus,
            soil_test.potassium,
            soil_test.notes,
            soil_test.id
        ))
        
        rows_affected = cursor.rowcount
        conn.commit()
        conn.close()
        
        return rows_affected > 0
    
    def delete_test(self, test_id: int) -> bool:
        """Delete a soil test"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM soil_tests WHERE id = ?', (test_id,))
        
        rows_affected = cursor.rowcount
        conn.commit()
        conn.close()
        
        return rows_affected > 0
    
    def test_connection(self) -> bool:
        """Test database connection"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('SELECT 1')
            conn.close()
            return True
        except Exception:
            return False
    
    def get_tests_by_location(self, location: str) -> List[SoilTest]:
        """Get tests by location (partial match)"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, location, latitude, longitude, ph, nitrogen, 
                   phosphorus, potassium, notes, test_date
            FROM soil_tests
            WHERE location LIKE ?
            ORDER BY test_date DESC
        ''', (f'%{location}%',))
        
        rows = cursor.fetchall()
        conn.close()
        
        tests = []
        for row in rows:
            test = SoilTest(
                id=row[0],
                location=row[1],
                latitude=row[2],
                longitude=row[3],
                ph=row[4],
                nitrogen=row[5],
                phosphorus=row[6],
                potassium=row[7],
                notes=row[8],
                test_date=row[9]
            )
            tests.append(test)
        
        return tests