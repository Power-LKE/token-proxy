"""
Admin CLI — create users, check balances
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from proxy.auth import user_manager


def cmd_create_user(args):
    if not args:
        print("Usage: python cli.py create-user <name> [balance]")
        return
    name = args[0]
    balance = float(args[1]) if len(args) > 1 else None
    user = user_manager.create_user(name, balance)
    print(f"User created!")
    print(f"  Name: {user.name}")
    print(f"  API Key: {user.api_key}")
    print(f"  Balance: {user.balance} yuan")


def cmd_list_users(args=None):
    users = user_manager.list_users()
    if not users:
        print("No users")
        return
    print(f"{'Name':<20} {'API Key':<50} {'Balance':<10} {'Status':<8}")
    print("-" * 90)
    for u in users:
        status = "Active" if u.is_active else "Disabled"
        print(f"{u.name:<20} {u.api_key:<50} {u.balance:<10.2f} {status:<8}")


def cmd_balance(args):
    if not args:
        print("Please provide API Key")
        return
    key = args[0]
    user = user_manager.get_user(key)
    if user:
        print(f"User: {user.name}")
        print(f"Balance: {user.balance} yuan")
        print(f"Status: {'Active' if user.is_active else 'Disabled'}")
    else:
        print("User not found")


def cmd_config(args=None):
    from config import UPSTREAM_PROVIDERS, MARKUP, DEFAULT_BALANCE, HOST, PORT
    print("Current configuration:")
    print(f"  Listen: {HOST}:{PORT}")
    print(f"  Markup: {MARKUP}")
    print(f"  New user bonus: {DEFAULT_BALANCE} yuan")
    print()
    print("  Upstream providers:")
    for key, p in UPSTREAM_PROVIDERS.items():
        print(f"    {p.name}:")
        print(f"      API base: {p.api_base}")
        api_key_val = os.environ.get(p.api_key_env, "NOT SET")
        print(f"      API key: {api_key_val}")
        print(f"      Models:")
        for model, price in p.models.items():
            print(f"        {model}: {price} yuan/1M input tokens")


def main():
    if len(sys.argv) < 2:
        print("Usage: python cli.py <command> [args]")
        print("Commands: create-user, list-users, balance, config, help")
        return
    cmd = sys.argv[1]
    args = sys.argv[2:]
    cmds = {
        "create-user": cmd_create_user,
        "list-users": cmd_list_users,
        "balance": cmd_balance,
        "config": cmd_config,
        "help": lambda _: print("Commands: create-user, list-users, balance, config"),
    }
    fn = cmds.get(cmd)
    if fn:
        fn(args)
    else:
        print(f"Unknown command: {cmd}")


if __name__ == "__main__":
    main()
