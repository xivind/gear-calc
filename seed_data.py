from database_manager import initialize_db, add_component, get_components
import json
import logging

logger = logging.getLogger(__name__)

def seed_database():
    """Seed the database with default components. Idempotent - only seeds if empty."""
    if get_components():
        logger.info("Database already seeded, skipping seed data.")
        return

    # Chainrings
    add_component("Compact Road", "Chainring", json.dumps([50, 34]), speed=11, comments="Standard compact road double")
    add_component("Standard Road", "Chainring", json.dumps([53, 39]), speed=11, comments="Standard road double")
    add_component("Gravel 1x", "Chainring", json.dumps([40]), speed=11, comments="Gravel single ring")

    # Cassettes
    add_component("Road 11-28", "Cassette", json.dumps([11, 12, 13, 14, 15, 17, 19, 21, 23, 25, 28]), speed=11, comments="Standard road cassette")
    add_component("Road 11-32", "Cassette", json.dumps([11, 12, 13, 14, 16, 18, 20, 22, 25, 28, 32]), speed=11, comments="Climbing road cassette")
    add_component("Gravel 11-42", "Cassette", json.dumps([11, 13, 15, 17, 19, 21, 24, 28, 32, 36, 42]), speed=11, comments="Wide range gravel cassette")

    logger.info("Database seeded successfully with default components.")

if __name__ == "__main__":
    initialize_db()
    seed_database()
