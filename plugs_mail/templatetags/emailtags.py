from django import template
from django.utils.safestring import mark_safe

register = template.Library()


def get_styles():
    """
    Return inline css styles
    """
    style = "background: #3f51b5;" \
        "display: block;" \
        "font-size: 13px;" \
        "font-weight: 100;" \
        "font-family: Helvetica,Arial,sans-serif;" \
        "text-transform: uppercase;" \
        "text-align: center;" \
        "letter-spacing: 1px;" \
        "text-decoration: none;" \
        "margin: 0 auto;" \
        "line-height: 62px;" \
        "width: 300px;" \
        "height: 60px;" \
        "-webkit-border-radius: 3px;" \
        "-moz-border-radius: 3px;" \
        "border-radius: 3px;" \
        "color: #ffffff;" \
        "webkit-text-size-adjust: none;" \
        "mso-hide: all;"
    return style


@register.simple_tag
def button(url, txt):
    template = '<div style="padding: 30px;"><a target="_blank" href="{0}" style="{1}" class="button">{2}</a></div>'
    html = template.format(url, get_styles(), txt)
    return mark_safe(html)
