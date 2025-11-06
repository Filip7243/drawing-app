from db.database_manager_singleton import get_db
from db.models import AfterwardsOpinion


class ExamineReasonRepository:
    def __init__(self):
        self.db = get_db()

    def get_afterwards_opinion_by_examine_id(self, examine_id: int):
        query = """
                SELECT examine_id,
                       reason
                FROM afterwards_opinion
                WHERE examine_id = %s;
                """
        with self.db.conn.cursor() as cur:
            cur.execute(query, (examine_id,))
            row = cur.fetchone()
            if not row:
                return None

            return AfterwardsOpinion(
                examine_id=row['examine_id'],
                opinion=row['reason']
            )

    def insert_afterwards_opinion(self, afterwards_opinion: AfterwardsOpinion):
        query = """
                INSERT INTO afterwards_opinion (examine_id, reason)
                VALUES (%s, %s)
                RETURNING examine_id;
                """
        with self.db.conn.cursor() as cur:
            cur.execute(query, (afterwards_opinion.examine_id, afterwards_opinion.opinion))
            inserted_id = cur.fetchone()['examine_id']
            self.db.conn.commit()
            return inserted_id
