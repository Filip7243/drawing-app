from db.database_manager_singleton import get_db
from db.models import Failure


class FailureRepository:
    def __init__(self):
        self.db = get_db()

    def insert_failure(self, failure: Failure):
        query = """
                INSERT INTO failure (image_id,
                                     pominiecia,
                                     znieksztalcenia,
                                     perserwacje,
                                     rotacje,
                                     przemieszczenia,
                                     bledy_wzglednej_wielkosci)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                RETURNING id;
                """
        with self.db.conn.cursor() as cur:
            cur.execute(
                query,
                (
                    failure.image_id,
                    failure.pominiecia,
                    failure.znieksztalcenia,
                    failure.perserwacje,
                    failure.rotacje,
                    failure.przemieszczenia,
                    failure.bledy_wzglednej_wielkosci,
                ),
            )
            new_id = cur.fetchone()['id']
            self.db.conn.commit()
            return new_id

    def get_failures_by_image_id(self, image_id: int) -> list[Failure]:
        query = """
                SELECT id,
                       image_id,
                       pominiecia,
                       znieksztalcenia,
                       perserwacje,
                       rotacje,
                       przemieszczenia,
                       bledy_wzglednej_wielkosci
                FROM failure
                WHERE image_id = %s;
                """
        with self.db.conn.cursor() as cur:
            cur.execute(query, (image_id,))
            rows = cur.fetchall()
            if not rows:
                return []

            failures = []
            for row in rows:
                failures.append(Failure(
                    id=row['id'],
                    image_id=row['image_id'],
                    pominiecia=row['pominiecia'],
                    znieksztalcenia=row['znieksztalcenia'],
                    perserwacje=row['perserwacje'],
                    rotacje=row['rotacje'],
                    przemieszczenia=row['przemieszczenia'],
                    bledy_wzglednej_wielkosci=row['bledy_wzglednej_wielkosci']
                ))
            return failures
