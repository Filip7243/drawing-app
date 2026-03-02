from db.models import ImageTableDataSummary, Image, Failure
from db.repository.ImageRepository import ImageRepository
from db.repository.FailureRepository import FailureRepository


class ImageService:
    imageRepo = ImageRepository()
    failureRepo = FailureRepository()

    def get_images_table_summary_by_examine_id(self, examine_id: int) -> list[ImageTableDataSummary]:
        images: list[Image] = self.imageRepo.get_images_by_examine_id(examine_id=examine_id)
        results: list[ImageTableDataSummary] = []
        for idx, img in enumerate(images, start=1):
            failures = self.failureRepo.get_failures_by_image_id(img.id)
            
            # Sumujemy błędy dla danego obrazu, jeśli istnieją (powinien być jeden rekord lub zero)
            if failures:
                f = failures[0]
                failure_list = [
                    f.pominiecia or 0,
                    f.znieksztalcenia or 0,
                    f.perserwacje or 0,
                    f.rotacje or 0,
                    f.przemieszczenia or 0,
                    f.bledy_wzglednej_wielkosci or 0
                ]
                is_valid = sum(failure_list) == 0
            else:
                failure_list = [0, 0, 0, 0, 0, 0]
                is_valid = True

            results.append(ImageTableDataSummary(
                idx=idx,
                examine_id=img.examine_id,
                content=img.content,
                duration_s=img.duration_s,
                is_valid=is_valid,
                failures=failure_list
            ))
        return results
