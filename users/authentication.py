from django.core import signing
from rest_framework.authentication import BaseAuthentication, get_authorization_header
from rest_framework.exceptions import AuthenticationFailed

from users.models import User

ACCESS_TOKEN_TTL_SECONDS = 60 * 60
_signer = signing.TimestampSigner(salt="learninghub.bearer-auth")


def create_access_token(user_id: int) -> str:
    return _signer.sign_object({"user_id": user_id})


class BearerTokenAuthentication(BaseAuthentication):
    def authenticate(self, request):
        auth = get_authorization_header(request).split()
        if not auth:
            return None
        if auth[0].lower() != b"bearer":
            return None
        if len(auth) != 2:
            raise AuthenticationFailed("Invalid bearer token.")

        try:
            token = auth[1].decode("ascii")
            payload = _signer.unsign_object(
                token, max_age=ACCESS_TOKEN_TTL_SECONDS
            )
        except (UnicodeDecodeError, signing.BadSignature):
            raise AuthenticationFailed("Invalid or expired bearer token.")

        if (
            not isinstance(payload, dict)
            or type(payload.get("user_id")) is not int
        ):
            raise AuthenticationFailed("Invalid bearer token.")

        user = User.objects.filter(
            pk=payload["user_id"], status="active"
        ).first()
        if user is None:
            raise AuthenticationFailed("User is inactive or no longer exists.")
        return user, token

    def authenticate_header(self, _request):
        return "Bearer"
