import sqlite3
import json
from datetime import datetime, date
from typing import List, Dict, Optional, Any


class Database:
    _connection: Optional[sqlite3.Connection] = None
    _db_path: str = ""

    @classmethod
    def init(cls, db_path: str):
        cls._db_path = db_path
        cls._connection = sqlite3.connect(db_path)
        cls._connection.row_factory = sqlite3.Row
        cls._create_tables()

    @classmethod
    def _create_tables(cls):
        cursor = cls._connection.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS medications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                dosage TEXT NOT NULL,
                notes TEXT,
                times_json TEXT NOT NULL,
                created_at TEXT NOT NULL,
                active INTEGER NOT NULL DEFAULT 1
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS medication_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                medication_id INTEGER NOT NULL,
                medication_name TEXT NOT NULL,
                dosage TEXT NOT NULL,
                scheduled_time TEXT NOT NULL,
                taken_time TEXT,
                status TEXT NOT NULL,
                notes TEXT,
                FOREIGN KEY (medication_id) REFERENCES medications(id)
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS blood_pressure (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                systolic INTEGER NOT NULL,
                diastolic INTEGER NOT NULL,
                pulse INTEGER,
                measurement_time TEXT NOT NULL,
                notes TEXT
            )
        """)
        cls._connection.commit()

    @classmethod
    def get_conn(cls) -> sqlite3.Connection:
        if cls._connection is None:
            cls._connection = sqlite3.connect(cls._db_path)
            cls._connection.row_factory = sqlite3.Row
        return cls._connection

    @classmethod
    def close(cls):
        if cls._connection:
            cls._connection.close()
            cls._connection = None

    # ============ 药品 ============
    @classmethod
    def add_medication(cls, name: str, dosage: str, notes: str, times: List[str]) -> int:
        conn = cls.get_conn()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO medications (name, dosage, notes, times_json, created_at, active) VALUES (?, ?, ?, ?, ?, ?)",
            (name, dosage, notes, json.dumps(times, ensure_ascii=False),
             datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 1)
        )
        conn.commit()
        return cursor.lastrowid

    @classmethod
    def update_medication(cls, med_id: int, name: str, dosage: str, notes: str, times: List[str]):
        conn = cls.get_conn()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE medications SET name=?, dosage=?, notes=?, times_json=? WHERE id=?",
            (name, dosage, notes, json.dumps(times, ensure_ascii=False), med_id)
        )
        conn.commit()

    @classmethod
    def delete_medication(cls, med_id: int):
        conn = cls.get_conn()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM medications WHERE id=?", (med_id,))
        conn.commit()

    @classmethod
    def get_all_medications(cls) -> List[Dict[str, Any]]:
        conn = cls.get_conn()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM medications WHERE active=1 ORDER BY id DESC")
        rows = cursor.fetchall()
        result = []
        for r in rows:
            d = dict(r)
            d["times"] = json.loads(d["times_json"]) if d["times_json"] else []
            del d["times_json"]
            result.append(d)
        return result

    @classmethod
    def get_medication(cls, med_id: int) -> Optional[Dict[str, Any]]:
        conn = cls.get_conn()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM medications WHERE id=?", (med_id,))
        row = cursor.fetchone()
        if row:
            d = dict(row)
            d["times"] = json.loads(d["times_json"]) if d["times_json"] else []
            del d["times_json"]
            return d
        return None

    # ============ 服药记录 ============
    @classmethod
    def add_medication_record(cls, medication_id: int, medication_name: str,
                               dosage: str, scheduled_time: str, status: str,
                               taken_time: Optional[str] = None, notes: str = "") -> int:
        conn = cls.get_conn()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO medication_records (medication_id, medication_name, dosage, scheduled_time, taken_time, status, notes) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (medication_id, medication_name, dosage, scheduled_time, taken_time, status, notes)
        )
        conn.commit()
        return cursor.lastrowid

    @classmethod
    def get_records_by_date(cls, date_str: str) -> List[Dict[str, Any]]:
        conn = cls.get_conn()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM medication_records WHERE substr(scheduled_time, 1, 10) = ? ORDER BY scheduled_time",
            (date_str,)
        )
        return [dict(r) for r in cursor.fetchall()]

    @classmethod
    def get_records_by_month(cls, year: int, month: int) -> List[Dict[str, Any]]:
        conn = cls.get_conn()
        cursor = conn.cursor()
        prefix = f"{year:04d}-{month:02d}"
        cursor.execute(
            "SELECT * FROM medication_records WHERE substr(scheduled_time, 1, 7) = ? ORDER BY scheduled_time",
            (prefix,)
        )
        return [dict(r) for r in cursor.fetchall()]

    @classmethod
    def get_all_records(cls, limit: int = 500) -> List[Dict[str, Any]]:
        conn = cls.get_conn()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM medication_records ORDER BY scheduled_time DESC LIMIT ?",
            (limit,)
        )
        return [dict(r) for r in cursor.fetchall()]

    @classmethod
    def update_record_status(cls, record_id: int, status: str, taken_time: Optional[str] = None):
        conn = cls.get_conn()
        cursor = conn.cursor()
        if taken_time:
            cursor.execute(
                "UPDATE medication_records SET status=?, taken_time=? WHERE id=?",
                (status, taken_time, record_id)
            )
        else:
            cursor.execute(
                "UPDATE medication_records SET status=? WHERE id=?",
                (status, record_id)
            )
        conn.commit()

    # ============ 血压记录 ============
    @classmethod
    def add_blood_pressure(cls, systolic: int, diastolic: int,
                           pulse: Optional[int], measurement_time: str, notes: str = "") -> int:
        conn = cls.get_conn()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO blood_pressure (systolic, diastolic, pulse, measurement_time, notes) VALUES (?, ?, ?, ?, ?)",
            (systolic, diastolic, pulse, measurement_time, notes)
        )
        conn.commit()
        return cursor.lastrowid

    @classmethod
    def get_all_blood_pressure(cls) -> List[Dict[str, Any]]:
        conn = cls.get_conn()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM blood_pressure ORDER BY measurement_time DESC")
        return [dict(r) for r in cursor.fetchall()]

    @classmethod
    def delete_blood_pressure(cls, bp_id: int):
        conn = cls.get_conn()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM blood_pressure WHERE id=?", (bp_id,))
        conn.commit()

    # ============ 统计 ============
    @classmethod
    def get_statistics(cls, start_date: str, end_date: str) -> Dict[str, int]:
        conn = cls.get_conn()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT status, COUNT(*) as cnt FROM medication_records "
            "WHERE substr(scheduled_time, 1, 10) BETWEEN ? AND ? GROUP BY status",
            (start_date, end_date)
        )
        rows = cursor.fetchall()
        stats = {"taken": 0, "delayed": 0, "missed": 0, "total": 0}
        for r in rows:
            key = r["status"]
            if key in stats:
                stats[key] = r["cnt"]
            stats["total"] += r["cnt"]
        return stats
