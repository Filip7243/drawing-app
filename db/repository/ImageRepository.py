from db.database_manager_singleton import get_db
from db.models import Image


class ImageRepository:
    def __init__(self):
        self.db = get_db()

    def get_images_by_examine_id(self, examine_id: int) -> list[Image]:
        query = """
                SELECT id,
                       examine_id,
                       content,
                       started_at_ts,
                       first_stroke_at_ts,
                       finished_at_ts,
                       interruptions_count,
                       interruptions_durations,
                       undo_count,
                       redo_count,
                       overdrawing_score,
                       revisit_count,
                       shading_detected,
                       direction_changes_count,
                       direction_reversal_count,
                       rapid_velocity_changes_count,
                       efficency_ratio,
                       max_local_density,
                       max_local_density_coords,
                       avg_velocity,
                       max_velocity,
                       velocity_ratio,
                       velocities,
                       velocity_profile_filename,
                       overlay_filename,
                       heatmap_filename,
                       duration_s,
                       actual_drawing_duration_s,
                       avg_interruption_duration_s
                FROM image
                WHERE examine_id = %s
                ORDER BY id;
                """
        try:
            with self.db.conn.cursor() as cur:
                cur.execute(query, (examine_id,))
                rows = cur.fetchall()
                if not rows:
                    return []

                images = []
                for row in rows:
                    images.append(Image(
                        id=row['id'],
                        examine_id=row['examine_id'],
                        content=row['content'],
                        started_at_ts=row['started_at_ts'],
                        first_stroke_at_ts=row['first_stroke_at_ts'],
                        finished_at_ts=row['finished_at_ts'],
                        interruptions_count=row['interruptions_count'],
                        interruptions_durations=row['interruptions_durations'] if row[
                            'interruptions_durations'] else [],
                        undo_count=row['undo_count'],
                        redo_count=row['redo_count'],
                        overdrawing_score=float(row['overdrawing_score']) if row[
                                                                                 'overdrawing_score'] is not None else 0.0,
                        revisit_count=row['revisit_count'],
                        shading_detected=row['shading_detected'],
                        direction_changes_count=row['direction_changes_count'],
                        direction_reversal_count=row['direction_reversal_count'],
                        rapid_velocity_changes_count=row['rapid_velocity_changes_count'],
                        efficiency_ratio=float(row['efficency_ratio']) if row['efficency_ratio'] is not None else 0.0,
                        max_local_density=float(row['max_local_density']) if row[
                                                                                 'max_local_density'] is not None else 0.0,
                        max_local_density_coords=row['max_local_density_coords'] if row[
                            'max_local_density_coords'] else [],
                        avg_velocity=float(row['avg_velocity']) if row['avg_velocity'] is not None else 0.0,
                        max_velocity=float(row['max_velocity']) if row['max_velocity'] is not None else 0.0,
                        velocity_ratio=float(row['velocity_ratio']) if row['velocity_ratio'] is not None else 0.0,
                        velocities=row['velocities'] if row['velocities'] else [],
                        velocity_profile_filename=row['velocity_profile_filename'],
                        overlay_filename=row['overlay_filename'],
                        heatmap_filename=row['heatmap_filename'],
                        duration_s=float(row['duration_s']) if row['duration_s'] is not None else 0.0,
                        actual_drawing_duration_s=float(row['actual_drawing_duration_s']) if row[
                                                                                                 'actual_drawing_duration_s'] is not None else 0.0,
                        avg_interruption_duration_s=float(row['avg_interruption_duration_s']) if row[
                                                                                                     'avg_interruption_duration_s'] is not None else 0.0
                    ))
                return images
        except Exception as e:
            import traceback
            print("Błąd przy pobieraniu danych rysunkow!")
            print(f"Typ błędu: {type(e).__name__}")
            print("Treść błędu:", e)
            print(traceback.format_exc())
            return []

    def insert_image(self, image: Image):
        query = """
                INSERT INTO image (examine_id,
                                   content,
                                   started_at_ts,
                                   first_stroke_at_ts,
                                   finished_at_ts,
                                   interruptions_count,
                                   interruptions_durations,
                                   undo_count,
                                   redo_count,
                                   overdrawing_score,
                                   revisit_count,
                                   shading_detected,
                                   direction_changes_count,
                                   direction_reversal_count,
                                   rapid_velocity_changes_count,
                                   efficency_ratio,
                                   max_local_density,
                                   max_local_density_coords,
                                   avg_velocity,
                                   max_velocity,
                                   velocity_ratio,
                                   velocities,
                                   velocity_profile_filename,
                                   overlay_filename,
                                   heatmap_filename,
                                   duration_s,
                                   actual_drawing_duration_s,
                                   avg_interruption_duration_s)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                        %s, %s, %s, %s)
                RETURNING id;
                """
        with self.db.conn.cursor() as cur:
            cur.execute(
                query,
                (
                    image.examine_id,
                    image.content,
                    image.started_at_ts,
                    image.first_stroke_at_ts,
                    image.finished_at_ts,
                    image.interruptions_count,
                    image.interruptions_durations,
                    image.undo_count,
                    image.redo_count,
                    image.overdrawing_score,
                    image.revisit_count,
                    image.shading_detected,
                    image.direction_changes_count,
                    image.direction_reversal_count,
                    image.rapid_velocity_changes_count,
                    image.efficiency_ratio,
                    image.max_local_density,
                    image.max_local_density_coords,
                    image.avg_velocity,
                    image.max_velocity,
                    image.velocity_ratio,
                    image.velocities,
                    image.velocity_profile_filename,
                    image.overlay_filename,
                    image.heatmap_filename,
                    image.duration_s,
                    image.actual_drawing_duration_s,
                    image.avg_interruption_duration_s,
                ),
            )
            inserted_id = cur.fetchone()['id']
            self.db.conn.commit()
            return inserted_id
