from db.database_manager_singleton import get_db
from db.models import Comment


class CommentRepository:
    def __init__(self):
        self.db = get_db()

    def get_comment_by_patient_id(self, patient_id: int):
        query = """
                SELECT patient_id,
                       comment
                FROM comments
                WHERE patient_id = %s;
                """
        with self.db.conn.cursor() as cur:
            cur.execute(query, (patient_id,))
            row = cur.fetchone()
            if not row:
                return None

            return Comment(
                patient_id=row['patient_id'],
                comment=row['comment']
            )

    def insert_comment(self, comment: Comment):
        query = """
                INSERT INTO comments (patient_id, comment)
                VALUES (%s, %s)
                RETURNING patient_id;
                """
        with self.db.conn.cursor() as cur:
            cur.execute(query, (comment.patient_id, comment.comment))
            inserted_id = cur.fetchone()['patient_id']
            self.db.conn.commit()
            return inserted_id
