class BugzillaError(Exception):
    pass


class BugNotFound(BugzillaError):
    pass


class BugzillaSearchError(BugzillaError):
    pass


class BugzillaAuthError(BugzillaError):
    """Raised when Bugzilla rejects a request for permission/authorization reasons
    (private bug or restricted comments), as distinct from a genuine 'not found'."""
