from __future__ import annotations

from instamine.models import PostDTO, ContentDTO, StoryDTO, HighlightDTO
from instamine.models.DTOs.profile_dto import ProfileDTO

from src.exceptions.exceptions import InvalidDTOError
from src.models import Person, Post, Content, Story, Highlight


class InstamineMapper:

    @staticmethod
    def to_person_entity(dto: ProfileDTO) -> Person:
        if not dto.id:
            raise InvalidDTOError("ProfileDTO must have a valid 'id' to map to Person entity.")
        elif not dto.username:
            raise InvalidDTOError("ProfileDTO must have a valid 'username' to map to Person entity.")


        return Person(
            external_id=dto.id,
            username=dto.username,
            full_name=dto.full_name,
            bio=dto.biography,
            n_followers=dto.n_followers,
            n_following=dto.n_following,
            n_posts=dto.n_posts
        )


    @staticmethod
    def to_post_entity(dto: PostDTO, owner_id: int) -> Post:
        if not dto.id:
            raise InvalidDTOError("PostDTO must have a valid 'id' to map to Post entity.")

        return Post(
            external_id=dto.id,
            publication_datetime=dto.publication_datetime,
            caption=dto.caption,
            n_likes=dto.n_likes,

            owner_id=owner_id
        )


    @staticmethod
    def to_story_entity(dto: StoryDTO, owner_id: int) -> Story:
        if not dto.id:
            raise InvalidDTOError("StoryDTO must have a valid 'id' to map to Story entity.")

        return Story(
            external_id=dto.id,
            publication_datetime=dto.publication_datetime,

            owner_id=owner_id
        )


    @staticmethod
    def to_highlight_entity(dto: HighlightDTO, owner_id: int) -> Highlight:
        if not dto.id:
            raise InvalidDTOError("HighlightDTO must have a valid 'id' to map to Highlight entity.")

        return Highlight(
            external_id=dto.id,
            title=dto.title,

            owner_id=owner_id
        )

    @staticmethod
    def to_content_entity(dto: ContentDTO) -> Content:
        if not dto.id:
            raise InvalidDTOError("ContentDTO must have a valid 'id' to map to Content entity.")

        if not dto.content.size() > 0:
            raise InvalidDTOError("ContentDTO must contain a valid content to map to Content entity.")

        return Content(
            external_id=dto.id,
            publication_datetime=dto.publication_datetime,
        )
