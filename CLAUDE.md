# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Gear Calc is a self-hosted bicycle gear ratio calculator built with FastAPI and SQLite. It helps cyclists and mechanics calculate gear ratios, manage drivetrain configurations, and visualize gear ranges with color-coded tables based on user-defined preferred ratios.

## Development Commands

### Running the Application

```bash
# Development mode with auto-reload and logging
uvicorn main:app --host 0.0.0.0 --port 8005 --reload --log-config uvicorn_log_config.ini

# Production mode (in container)
uvicorn main:app --host 0.0.0.0 --port 8005 --log-config uvicorn_log_config.ini
```

The application will be available at `http://localhost:8005`

### Docker

```bash
# Use the provided script (recommended)
./create-container-gearcalc.sh

# Or manually build and run
docker build -t gear-calc .
docker run -d --name=gear-calc -p 8005:8005 -v ~/code/container_data:/app/data gear-calc
```

The container includes:
- Health check monitoring (checks status.txt every 10 minutes)
- Persistent data storage in ~/code/container_data
- Auto-restart unless manually stopped
- Timezone set to Europe/Stockholm

### Database

The application uses SQLite with the Peewee ORM. The database is stored at `./data/gear_calc.db` and is created automatically on first run.

**Automatic Seeding**: On startup, `seed_database()` is called automatically. It's idempotent - it only adds default components (chainrings and cassettes) if the database is empty.

**Manual Seeding** (if needed):
```bash
python seed_data.py
```

**Backup Database**:
```bash
./backup_db.sh
```
This script safely stops the container, backs up the database to /home/pi/backup/, and restarts the container.

### Health Monitoring

The application includes a health check system:
- `health_check()` function in main.py tests database connectivity on startup
- Writes "ok" or "error" to `status.txt`
- Docker HEALTHCHECK reads this file every 10 minutes
- Container is marked unhealthy if status.txt contains "error"

## Architecture

### Strict Layer Separation

This codebase follows a strict three-layer architecture. **Do not violate these boundaries:**

1. **main.py** - Routing layer only
   - FastAPI routes and HTTP handling
   - Template rendering
   - **NO business logic or database operations**

2. **business_logic.py** - Business logic layer
   - All calculations (gear ratios, ranges, percentages)
   - Data transformation and formatting
   - **MUST call database_manager.py for all CRUD operations**
   - **NEVER call Peewee models directly**

3. **database_manager.py** - Data access layer
   - All CRUD operations
   - Direct interaction with Peewee models
   - Database initialization

### Supporting Modules

- **database_model.py** - Peewee ORM models (Component, GearConfiguration, UserPreference)
- **utils.py** - Helper functions (UUID generation, etc.)
- **logger.py** - Centralized logging configuration

### Database Model

The application uses UUIDs for all primary keys (generated in the backend, not by the database). The three main tables are:

- **Component**: Stores chainrings and cassettes with teeth as JSON arrays
- **GearConfiguration**: Links front and rear components with user metadata
- **UserPreference**: Stores min/max ratio preferences for color-coding

### Frontend Architecture

- Server-side rendered HTML with Jinja2 templates
- Minimal JavaScript in `static/js/main.js` (TomSelect initialization, delete handlers)
- Bootstrap for styling with custom CSS in `static/css/styles.css`
- TomSelect library for enhanced select dropdowns
- **No complex client-side framework** - keep JavaScript minimal and vanilla

### Key Business Logic

- **Teeth parsing**: Components store teeth as JSON arrays (e.g., `[32, 48]` for a 2x chainring). The `parse_teeth()` function handles JSON strings, comma-separated strings, or lists.
- **Gear ratio calculation**: Performed in `calculate_gear_ratios()` which also determines color-coding status (optimal/warning/poor) based on user preferences with a 10% buffer zone.
- **Total range**: Calculated as `(max_ratio / min_ratio) * 100` where max_ratio = largest_chainring / smallest_cog and min_ratio = smallest_chainring / largest_cog.

## Important Constraints

- **Always use UUID4 for new records** - Call `utils.generate_uuid()`, never rely on auto-increment
- **Teeth must be stored as JSON arrays** - Use `json.dumps([list])` when saving components
- **HTMX or partial rendering** - The `/calculate-preview` endpoint returns a partial template for dynamic updates
- **No backrefs in database models** - Keep the Peewee model simple and explicit
- **Comments can be nullable** - Handle "None" strings properly by converting to actual None
- **Preferences have a 10% buffer zone** - Ratios within 10% of min/max thresholds get "warning" status, not "optimal" or "poor"

## Common Patterns

### Adding a new component
1. User submits form with comma-separated teeth (e.g., "11, 13, 15, 17, 19")
2. `business_logic.save_component()` validates and converts to JSON array
3. `database_manager.add_component()` or `update_component()` performs CRUD

### Creating a configuration
1. User selects chainring and cassette from dropdowns
2. Frontend can preview calculations via `/calculate-preview` POST endpoint
3. User saves with name and comments
4. `business_logic.create_configuration()` → `database_manager.add_configuration()`

### Displaying gear tables
1. Load configuration via `business_logic.get_configuration_details()`
2. This returns parsed components, calculated gear ratios, and total range
3. Template renders color-coded tables based on preferences

## File Structure Notes

- Templates are in `templates/` with a `base.html` layout
- Partials in `templates/partials/` for HTMX-style updates
- Static assets in `static/` (css, js, img)
- Database file `gear_calc.db` is gitignored and created on first run
