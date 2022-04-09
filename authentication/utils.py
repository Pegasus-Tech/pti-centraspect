
def parse_auth_token(header_val):
    return header_val.split('Authorization ')[-1] if header_val is not None else None
