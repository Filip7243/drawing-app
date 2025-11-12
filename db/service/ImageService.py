from db.models import ImageTableDataSummary, Image
from db.repository.ImageRepository import ImageRepository


class ImageService:
    imageRepo = ImageRepository()

    def get_images_table_summary_by_examine_id(self, examine_id: int) -> list[ImageTableDataSummary]:
        print("POBIRAM DANE Z IMAGE")
        images: list[Image] = self.imageRepo.get_images_by_examine_id(examine_id=examine_id)
        results: list[ImageTableDataSummary] = []
        for idx, img in enumerate(images, start=1):
            results.append(ImageTableDataSummary(
                idx,
                img.examine_id,
                img.content,
                img.time,
                # Tutaj narazie placeholder, jak będzie gotowy model AI, tutaj wypełniamy danymi z niego (join do tabeli)
                True,
                [0, 1, 0, 0, 1]
            ))
        return results
