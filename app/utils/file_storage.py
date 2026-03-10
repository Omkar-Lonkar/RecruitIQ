import os
import uuid

BASE_STORAGE_PATH = "storage"


def save_resume_file(company_id, candidate_id, file):
    company_folder = os.path.join(
        BASE_STORAGE_PATH,
        f"company_{company_id}",
        f"candidate_{candidate_id}",
    )

    os.makedirs(company_folder, exist_ok=True)

    file_extension = file.filename.split(".")[-1]
    unique_filename = f"resume_{uuid.uuid4()}.{file_extension}"
    file_path = os.path.join(company_folder, unique_filename)

    with open(file_path, "wb") as buffer:
        buffer.write(file.file.read())

    return file_path, unique_filename
