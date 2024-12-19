# Soundboard

Discord Bot to get around soundboard limits. Goal is to use the Discord API to
dynamically swap sounds in and out to have the perception of more soundboard
slots than the server has available.

## Dev

We use `uv` (see [uv](https://docs.astral.sh/uv/)). Use `uv sync --dev` to
create a venv.

For testing you will need to create a Discord Bot through the app portal. The
required environment variables are listed in the example environment file (see
[example file](./example.env)).

Your bot must have the `bot` scope. The required permissions are:

* `Create Expressions` - To add new sounds
* `Manage Expressions` - To edit sounds
* `Use Soundboard` - To play sounds
* `Speak` - To play sounds

Run with `docker compose up`.
