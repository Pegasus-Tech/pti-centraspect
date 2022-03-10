from django import template

register = template.Library()


@register.filter
def replace_or_insert_page(path, page):
    if '?page' in path:
        base_path = path.split('?')[0]
        return f'{base_path}?path={page}'
    elif '&page' in path:
        base_path = path.split('&page')[0]
        return f'{base_path}&page={page}'
    elif '?' in path:
        return f'{path}&page={page}'
    return f'?page={page}'


@register.filter
def append_to_path(path, toAppend):
    paths = path.split('?')
    base = paths[0]
    query = paths[1] if len(paths) > 1 else None
    final_query = ''

    if query is not None:
        existing_params = query.split('&')
        for param in existing_params:
            if 'sort_col' not in param and 'sort_dir' not in param:
                final_query += f'&{param}'

    final_path = f'{base}?{toAppend}{final_query}'
    return final_path

