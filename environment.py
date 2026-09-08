"""
environment.py — Behave hooks

Lifecycle:
  before_all      -> loads environment config from environments.yml
  before_scenario -> instantiates fresh ApiClient per scenario
  after_scenario  -> cleans up created users (automatic teardown)
"""
import os
import yaml
from dotenv import load_dotenv
from utils.api_client import ApiClient

load_dotenv()  # Load variables from .env if present


def before_all(context):
    # Dynamically load the target environment ('dev' or 'prod') from CLI arguments 
    # (e.g. -D env=dev) or OS environment variables, and resolve it using 'environments.yml'
    env = (
            context.config.userdata.get("env")
            or os.environ.get("TEST_ENV", "dev")
    )

    config_path = os.path.join(os.path.dirname(__file__), "config", "environments.yml")
    with open(config_path, "r") as f:
        all_envs = yaml.safe_load(f)

    if env not in all_envs:
        available = list(all_envs.keys())
        raise ValueError(
            f"Unknown environment: '{env}'. "
        )

    env_config = all_envs[env]
    context.env = env
    context.base_url = env_config["base_url"]

    token_var = env_config["token_env_var"]
    context.auth_token = os.environ.get(token_var)
    if not context.auth_token:
        raise ValueError(f"Environment variable '{token_var}' is not set. Please check your .env file or CI secrets")

    print(f"\n[ENV] Running in environment: {env.upper()} -> {context.base_url}")


def before_scenario(context, scenario):
    # for each environment use tags like @dev and @prod
    # If we run the suite targeting DEV (-D env=dev) but a scenario is tagged ONLY for @prod,
    # Behave automatically skips it
    env_tags = {"dev", "prod", "qa"}
    scenario_envs = env_tags.intersection(scenario.effective_tags)

    if scenario_envs and context.env not in scenario_envs:
        scenario.skip(f"Skipped: Scenario intended for {scenario_envs}, current env is '{context.env}'")
        return

    context.api_client = ApiClient(context.base_url, context.auth_token)  # instance of ApiClient
    context.response = None  # for validation Json and status
    context.created_emails = [] # array of emails
    context.user_data = {}


# """Deletes all users created during the scenario after scenario iteration"""
def after_scenario(context, scenario):
    for email in context.created_emails:
        try:
            context.api_client.delete(f"/users/{email}", token=context.auth_token)
        except Exception as e:
            print(f"[TEARDOWN] Could not delete {email}: {e}")
