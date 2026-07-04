import os
import json
from config_manager import config_manager

def update_missing_translations(channels):
    missing_categories = set()
    for channel in channels:
        category = channel.get('group-title', 'Unknown')
        if category.lower() not in category_translation:
            missing_categories.add(category)
    
    if missing_categories:
        logger.info("Missing translations:")
        for category in missing_categories:
            logger.info(f"- {category}")

