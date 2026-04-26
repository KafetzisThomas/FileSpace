def add_folder_to_zip(zip_file, folder, base_path=""):
    """
    Recursively add a folder and its contents to a zip archive.
    """
    for file_obj in folder.files.all():
        if file_obj.file:
            zip_file.write(file_obj.file.path, arcname=f"{base_path}{file_obj.name}")

    for subfolder in folder.subfolders.all():
        add_folder_to_zip(zip_file, subfolder, f"{base_path}{subfolder.name}/")
