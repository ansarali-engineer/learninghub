# learninghub

## API authentication

Register users with `POST /api/create_user`, then log in with `POST /api/login`:

```json
{
  "email": "student@example.com",
  "password": "your-password"
}
```

The login response contains an `access_token` that expires after one hour. Send
it on authenticated requests using:

```text
Authorization: Bearer <access_token>
```

`GET /api/users_list` requires an authenticated admin account. Public
registration creates active student accounts only; authenticated admins can
assign other roles and statuses when creating users. To bootstrap the first
admin, configure `ADMIN_BOOTSTRAP_TOKEN` in `.env` and include it as
`bootstrap_token` in the first admin registration request. This works only
while no admin exists; remove the token from `.env` after setup. Inactive users
cannot log in, and there is no refresh-token or logout endpoint yet.
