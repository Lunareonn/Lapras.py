import config


def check_if_roster(ctx):
    if not ctx.guild:
        return False

    return any(r.id in config.roster_roles for r in ctx.author.roles)


def check_if_leader(ctx):
    if not ctx.guild:
        return False

    return any(r.id in config.leader_roles for r in ctx.author.roles)


def unfinished(ctx):
    return False
