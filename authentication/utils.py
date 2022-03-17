
def parse_auth_token(header_val):
    return header_val.split('Authorization ')[-1]
