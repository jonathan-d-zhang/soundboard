# Soundboard

HTTP Interactions Bot to get around soundboard limits. Goal is to use the
Discord API to dynamically swap sounds in and out to have the perception of
more soundboard slots than the server has available.

## Dev

We use `uv` (see [uv](https://docs.astral.sh/uv/)). Use `uv sync --dev` to
create a venv.

For testing you will need to create a Discord Bot through the app portal. You
will also need a Cloudflare Tunnel (which is free). The required environment
variables are listed in the example environment file (see [example
file](./example.env)).

Your bot must have the `applications.commands` and `bot` scopes. It also needs
the `Use Soundboard` permission.

Run with `docker compose up`.
