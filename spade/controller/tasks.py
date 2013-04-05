from celery import task
from spade.utils.cssparser import CSSParser


@task(name="parse-css")
def parse_css(linkedcss):
    parser = CSSParser()
    parser.parse(linkedcss)
