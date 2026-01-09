import logging
import mimetypes
import os
import shutil
from typing import Optional


class FileStorageManager:
    def __init__(self, base_root: str):
        """
        Manages physical file storage.
        Internal structure: see file_storage_schema.drawio
        """

        self.base_root = base_root

        self.logger = logging.getLogger(__name__)


    # *******************************************************
    # Public methods
    # *******************************************************

    def save_post_media(
        self,
        user_id: str,
        post_id: str,
        content_id: str,
        data: bytes,
        mime_type: str,
    ):
        """
        Saves media for a post.
        """
        path = os.path.join(self.base_root, user_id, "Posts", post_id)
        self._save_file(path, content_id, data, mime_type)


    def save_story_media(
        self,
        user_id: str,
        story_id: str,
        data: bytes,
        mime_type: str,
    ):
        """
        Saves media for a story.
        NOTE: The file name is the story ID (not the content ID)
        """
        path = os.path.join(self.base_root, user_id, "Stories")
        self._save_file(path, story_id, data, mime_type)


    def save_highlight_media(
        self,
        user_id: str,
        highlight_id: str,
        content_id: str,
        data: bytes,
        mime_type: str,
    ):
        """
        Saves media for a highlight.
        """
        path = os.path.join(self.base_root, user_id, "Highlights", highlight_id)
        self._save_file(path, content_id, data, mime_type)


    def get_story_path(self, user_external_id: str, story_external_id: str) -> str:
        """
        Locates the story file on disk, ignoring the extension.
        Path: data/contents/{user}/Stories/{story_id}.*
        """
        target_dir = os.path.join(self.base_root, user_external_id, "Stories")
        return self._find_file_by_stem(target_dir, story_external_id)


    def get_post_file_path(self, user_external_id: str, post_external_id: str, content_external_id: str) -> str:
        """
        Locates a specific file within a Post folder.
        Path: data/contents/{user}/Posts/{post_id}/{content_id}.*
        """
        target_dir = os.path.join(self.base_root, user_external_id, "Posts", post_external_id)

        return self._find_file_by_stem(target_dir, content_external_id)


    def get_highlight_path(self, user_external_id: str, highlight_external_id: str, content_external_id: str) -> str:
        """
        Locates a file in a Highlight folder.
        Path: data/contents/{user}/Highlights/{highlight_id}/{content_id}.*
        """
        target_dir = os.path.join(self.base_root, user_external_id, "Highlights", highlight_external_id)

        return self._find_file_by_stem(target_dir, content_external_id)


    def delete_user_folder(self, user_id: str):
        user_path = os.path.join(self.base_root, user_id)
        self._delete_folder_recursively(user_path)


    def delete_posts_folder(self, user_id: str):
        posts_path = os.path.join(self.base_root, user_id, "Posts")
        self._delete_folder_recursively(posts_path)


    def delete_stories_folder(self, user_id: str):
        stories_path = os.path.join(self.base_root, user_id, "Stories")
        self._delete_folder_recursively(stories_path)


    def delete_highlights_folder(self, user_id: str):
        highlights_path = os.path.join(self.base_root, user_id, "Highlights")
        self._delete_folder_recursively(highlights_path)


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


    def _find_file_by_stem(self, directory: str, target_stem: str) -> str:
        if not os.path.exists(directory):
            self.logger.error(f"Directory {directory} does not exist")
            raise FileNotFoundError(f"Directory {directory} does not exist")

        try:
            for filename in os.listdir(directory):
                stem, ext = os.path.splitext(filename)
                if stem == target_stem:
                    return os.path.join(directory, filename)

            raise FileNotFoundError(f"File {target_stem} not found in {directory}")
        except Exception as e:
            self.logger.error(f"Error searching for file in {directory}: {str(e)}")
            raise e


    def _delete_folder_recursively(self, path: str):
        if os.path.exists(path):
            try:
                shutil.rmtree(path)
            except Exception as e:
                self.logger.error(f"Failed to delete folder at {path}: {str(e)}")
                raise IOError(f"Failed to delete folder at {path}: {str(e)}")