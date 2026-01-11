import logging
import mimetypes
import os
import shutil
from datetime import datetime
from typing import Optional

import markdown


class FileStorageManager:
    def __init__(self, base_root: str):
        """
        Manages physical file storage.
        Internal structure: see file_storage_schema.drawio
        """

        self.base_root = base_root
        os.makedirs(base_root, exist_ok=True)

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


    def save_report(self, user_external_id: str, username: str, markdown_content: str) -> str:
        """
        Saves the report as Markdown and PDF.
        Returns the path to the PDF file.
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_dir = self.get_report_dir(user_external_id)

        filename_base = f"Report_{username}_{timestamp}"
        md_path = os.path.join(report_dir, f"{filename_base}.md")
        pdf_path = os.path.join(report_dir, f"{filename_base}.pdf")

        # 1. Save Markdown
        with open(md_path, "w", encoding="utf-8") as f:
            f.write(markdown_content)

        # 2. Convert to PDF
        try:
            import weasyprint

            # Convert MD -> HTML
            html_body = markdown.markdown(markdown_content)

            # Add some basic CSS for a professional look
            css_style = """
                body { font-family: sans-serif; line-height: 1.6; color: #333; }
                h1 { color: #2c3e50; border-bottom: 2px solid #2c3e50; padding-bottom: 10px; }
                h2 { color: #16a085; margin-top: 20px; }
                strong { color: #2980b9; }
                hr { border: 0; border-top: 1px solid #eee; margin: 30px 0; }
            """

            html_content = f"<html><head><style>{css_style}</style></head><body>{html_body}</body></html>"

            # Generate PDF
            weasyprint.HTML(string=html_content).write_pdf(pdf_path)

            return pdf_path

        except ImportError:
            print("Warning: 'weasyprint' not installed. Saving only Markdown.")
            return md_path
        except Exception as e:
            print(f"Warning: PDF generation failed: {e}. Report saved as Markdown only.")
            return md_path


    def get_story_filepath(self, user_external_id: str, story_external_id: str) -> str:
        """
        Locates the story file on disk, ignoring the extension.
        Path: data/contents/{user}/Stories/{story_id}.*
        """
        target_dir = os.path.join(self.base_root, user_external_id, "Stories")
        return self._find_file_by_stem(target_dir, story_external_id)


    def get_post_filepath(self, user_external_id: str, post_external_id: str, content_external_id: str) -> str:
        """
        Locates a specific file within a Post folder.
        Path: data/contents/{user}/Posts/{post_id}/{content_id}.*
        """
        target_dir = os.path.join(self.base_root, user_external_id, "Posts", post_external_id)

        return self._find_file_by_stem(target_dir, content_external_id)


    def get_highlight_filepath(self, user_external_id: str, highlight_external_id: str, content_external_id: str) -> str:
        """
        Locates a file in a Highlight folder.
        Path: data/contents/{user}/Highlights/{highlight_id}/{content_id}.*
        """
        target_dir = os.path.join(self.base_root, user_external_id, "Highlights", highlight_external_id)

        return self._find_file_by_stem(target_dir, content_external_id)


    def get_report_dir(self, user_external_id: str) -> str:
        """Creates and returns the report directory for a user."""
        path = os.path.join(self.base_root, str(user_external_id), "Reports")
        os.makedirs(path, exist_ok=True)
        return path


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


    def clear_storage(self):
        """
        Deletes all files and folders in the base root.
        Use with caution.
        """

        for item in os.listdir(self.base_root):
            item_path = os.path.join(self.base_root, item)
            try:
                if os.path.isdir(item_path):
                    shutil.rmtree(item_path)
                else:
                    os.remove(item_path)
            except Exception as e:
                self.logger.error(f"Failed to delete {item_path}: {str(e)}")
                raise IOError(f"Failed to delete {item_path}: {str(e)}")



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