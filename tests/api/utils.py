def authorization_header(token) -> dict:
    return {'Authorization': f'Bearer {token}'}
