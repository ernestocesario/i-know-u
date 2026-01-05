import mimetypes
import os


class FileStorageManager:
    def __init__(self, base_root: str):
        """
        Manages physical file storage.
        Internal structure: see file_storage_schema.drawio
        """

        self.base_root = base_root


    # *******************************************************
    # Public methods
    # *******************************************************

    def save_post_media(
        self,
        username: str,
        post_id: str,
        content_id: str,
        data: bytes,
        mime_type: str,
    ):
        """
        Saves media for a post.
        """
        path = os.path.join(self.base_root, username, "Posts", post_id)
        self._save_file(path, content_id, data, mime_type)


    def save_story_media(
        self,
        username: str,
        story_id: str,
        data: bytes,
        mime_type: str,
    ):
        """
        Saves media for a story.
        NOTE: The file name is the story ID (not the content ID)
        """
        path = os.path.join(self.base_root, username, "Stories")
        self._save_file(path, story_id, data, mime_type)


    def save_highlight_media(
        self,
        username: str,
        highlight_id: str,
        content_id: str,
        data: bytes,
        mime_type: str,
    ):
        """
        Saves media for a highlight.
        """
        path = os.path.join(self.base_root, username, "Highlights", highlight_id)
        self._save_file(path, content_id, data, mime_type)



    # *******************************************************
    # Private methods
    # *******************************************************

    @staticmethod
    def _get_extension(mime_type: str) -> str:
        """
        Converts a mime type (e.g. 'image/jpeg') to a file extension (e.g. '.jpg').
        """
        if not mime_type:
            return ".bin"  # Fallback if mime_type is missing

        # mimetypes.guess_extension returns the standard extension
        ext = mimetypes.guess_extension(mime_type)

        if ext:
            return ext

        # Common manual fallbacks if the library fails
        if "jpeg" in mime_type or "jpg" in mime_type:
            return ".jpg"
        if "png" in mime_type:
            return ".png"
        if "mp4" in mime_type:
            return ".mp4"

        return ".bin"


    def _save_file(self, folder_path: str, file_name_no_ext: str, data: bytes, mime_type: str) -> str:
        """
        Internal helper: creates the folder (if needed) and saves the file
        using the correct extension.
        """
        # 1. Create the directory if it does not exist
        os.makedirs(folder_path, exist_ok=True)

        # 2. Determine file extension
        extension = self._get_extension(mime_type)
        file_name = f"{file_name_no_ext}{extension}"

        # 3. Build full file path
        full_path = os.path.join(folder_path, file_name)

        try:
            with open(full_path, "wb") as f:
                f.write(data)
            return full_path
        except Exception as e:
            raise IOError(f"Failed to save file at {full_path}: {str(e)}")