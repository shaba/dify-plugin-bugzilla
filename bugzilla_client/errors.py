class BugzillaError(Exception):
    pass


class BugNotFound(BugzillaError):
    pass


class BugzillaSearchError(BugzillaError):
    pass
