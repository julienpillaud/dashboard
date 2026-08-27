class AuthorizationError(Exception):
    pass


class InvalidAccessToken(AuthorizationError):
    pass
