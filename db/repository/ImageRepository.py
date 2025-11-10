from PyQt6.QtCore import QBuffer

from db.database_manager_singleton import get_db
from db.models import Image


class ImageRepository:
    def __init__(self):
        self.db = get_db()

    def get_image_by_examine_id(self, examine_id: int):
        query = """
                SELECT examine_id,
                       content,
                       time
                FROM image
                WHERE examine_id = %s;
                """
        with self.db.conn.cursor() as cur:
            cur.execute(query, (examine_id,))
            row = cur.fetchone()
            if not row:
                return None

            return Image(
                examine_id=row['examine_id'],
                content=row['content'],
                time=row['time']
            )

    def insert_image(self, image: Image):
        query = """
                INSERT INTO image (examine_id, content, time)
                VALUES (%s, %s, %s)
                RETURNING examine_id;
                """
        with self.db.conn.cursor() as cur:
            cur.execute(query, (image.examine_id, image.content, image.time))
            inserted_id = cur.fetchone()['examine_id']
            self.db.conn.commit()
            return inserted_id
