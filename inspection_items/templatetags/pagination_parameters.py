from django import template

register = template.Library()


@register.filter
def replace_or_insert_page(path, page):
    print(f'Param: {path} | value: {page}')
    if '?page' in path:
        base_path = path.split('?')[0]
        return f'{base_path}?path={page}'
    elif '&page' in path:
        base_path = path.split('&page')[0]
        return f'{base_path}&page={page}'
    elif '?' in path:
        return f'{path}&page={page}'
    return f'?page={page}'

