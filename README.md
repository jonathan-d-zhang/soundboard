# Soundboard

Discord Bot to get around soundboard limits.

## Dev

We use `uv` (see [uv](https://docs.astral.sh/uv/)). Use `uv sync --dev` to
create a venv.

For testing you will need to create a Discord Bot through the app portal. The
required environment variables are listed in the example environment file (see
[example file](./example.env)). Importantly, the `message_content` intent
should be enabled.

Your bot must have the `bot` scope. The required permissions are:

* `Create Expressions` - To add new sounds
* `Manage Expressions` - To edit sounds
* `Use Soundboard` - To play sounds
* `Speak` - To play sounds

Run with `docker compose up`.
