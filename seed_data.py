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
    add_component("Specialites TA ONE X110 42T", "Chainring", json.dumps([42]), speed=1, comments="TA ONE X110 for 1x setups")
    add_component("Shimano GRX RX600 40T", "Chainring", json.dumps([40]), speed=1, comments="Shimano GRX for 1x setups")
    add_component("Race Face 36T", "Chainring", json.dumps([36]), speed=1, comments="Chainring for 1x setups")
    add_component("Wolf Tooth 36T", "Chainring", json.dumps([36]), speed=1, comments="Wolf Tooth chainring for 1x setups")

    # Cassettes
    add_component("Deore XT CS-M8000 11-46", "Cassette", json.dumps([11, 13, 15, 17, 19, 21, 24, 28, 32, 37, 46]), speed=11, comments="High range MTB cassette")
    add_component("Deore XT CS-M8000 11-42", "Cassette", json.dumps([11, 13, 15, 17, 19, 21, 24, 27, 31, 35, 42]), speed=11, comments="Medium range MTB cassette")
    add_component("Deore XT CS-M8000 11-40", "Cassette", json.dumps([11, 13, 15, 17, 19, 21, 24, 27, 31, 35, 40]), speed=11, comments="Low range MTB cassette")

    logger.info("Database seeded successfully with default components.")

if __name__ == "__main__":
    initialize_db()
    seed_database()
