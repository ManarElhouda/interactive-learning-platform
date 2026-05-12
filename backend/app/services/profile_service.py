"""Service for managing child profiles (JSON-based storage)."""
import json
import logging
from datetime import datetime
from pathlib import Path
from app.models.profile import UserProfile

logger = logging.getLogger(__name__)

PROFILES_DIR = Path("db/profiles")


class ProfileService:

    def __init__(self):
        PROFILES_DIR.mkdir(parents=True, exist_ok=True)

    def get_profile(self, child_id: str) -> UserProfile:
        profile_path = PROFILES_DIR / f"{child_id}.json"
        if profile_path.exists():
            try:
                with open(profile_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                return UserProfile(**data)
            except Exception as e:
                logger.error(f"Error loading profile {child_id}: {str(e)}")
                return self._default_profile(child_id)
        return self._default_profile(child_id)

    def save_profile(self, profile: UserProfile) -> bool:
        try:
            profile_path = PROFILES_DIR / f"{profile.child_id}.json"
            profile.updated_at = datetime.now().isoformat()
            with open(profile_path, "w", encoding="utf-8") as f:
                json.dump(profile.model_dump(), f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            logger.error(f"Error saving profile: {str(e)}")
            return False

    def _default_profile(self, child_id: str) -> UserProfile:
        profile = UserProfile(
            child_id=child_id,
            created_at=datetime.now().isoformat(),
            updated_at=datetime.now().isoformat(),
        )
        self.save_profile(profile)
        return profile

    def build_system_prompt_context(self, profile: UserProfile) -> str:
        blacklist_str = ", ".join(profile.blacklist) if profile.blacklist else "none"
        keywords_str = ", ".join(profile.positive_keywords) if profile.positive_keywords else "none"
        return (
            "CHILD PROFILE:\n"
            f"- Name: {profile.name}, Age: {profile.age}\n"
            f"- Cognitive level: {profile.cognitive_level}\n"
            f"- Interests: {', '.join(profile.interests)}\n"
            f"- Preferred colors: {', '.join(profile.preferred_colors)}\n"
            f"- Style: {profile.style_preference}\n"
            f"- Blacklist (NEVER use): {blacklist_str}\n"
            f"- Boosted keywords: {keywords_str}"
        )

    def get_sdxl_style_suffix(self, profile: UserProfile) -> str:
        style_map = {
            "cartoon": "cartoon style, flat design, bold outlines, vibrant colors, child-friendly",
            "watercolor": "watercolor illustration, soft edges, pastel colors, artistic",
            "realistic": "photorealistic, detailed, natural lighting, clear",
        }
        style_base = style_map.get(profile.style_preference, style_map["cartoon"])
        return f"{style_base}, colors: {', '.join(profile.preferred_colors)}"

    def get_negative_prompt_additions(self, profile: UserProfile) -> str:
        if not profile.blacklist:
            return ""
        return ", ".join(profile.blacklist)

    def save_interaction(self, child_id: str, interaction_record: dict) -> bool:
        try:
            interactions_dir = PROFILES_DIR / f"{child_id}_interactions"
            interactions_dir.mkdir(parents=True, exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            interaction_path = interactions_dir / f"{timestamp}.json"
            record_with_ts = {**interaction_record, "timestamp": datetime.now().isoformat()}
            with open(interaction_path, "w", encoding="utf-8") as f:
                json.dump(record_with_ts, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            logger.error(f"Error saving interaction: {str(e)}")
            return False

    def update_profile_from_feedback(self, child_id: str, translation: str,
                                     quality_score: int, clarity_score: int,
                                     style_score: int) -> bool:
        try:
            profile = self.get_profile(child_id)

            if quality_score == 3:
                kw = translation.strip().split()[0].lower() if translation.strip() else ""
                if kw and kw not in profile.positive_keywords:
                    profile.positive_keywords.append(kw)
                    logger.info(f"Keyword boosted: '{kw}'")
            elif quality_score == 1:
                logger.info(f"Negative quality feedback for {child_id}")

            if clarity_score == 1:
                profile.style_preference = "cartoon"
                logger.info(f"Style simplified to cartoon for {child_id}")

            if style_score == 3:
                logger.info(f"Visual style validated for {child_id}")
            elif style_score == 1:
                logger.info(f"Visual style not adapted for {child_id}")

            return self.save_profile(profile)
        except Exception as e:
            logger.error(f"Error updating profile from feedback: {str(e)}")
            return False


profile_service = ProfileService()
