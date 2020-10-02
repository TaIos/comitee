# constants
OK = 0
BAD = 1


def apply_violations(violations, session, commit):
    if len(violations) == 0:
        return

    # TODO
