from __future__ import print_function
import markdown
import os

from django.contrib.flatpages.models import FlatPage
from django.contrib.sites.models import Site
from django.core.management.base import BaseCommand

from honeycomb_markdown import HoneycombMarkdown


def mockable_print(val):
    print(val)


class Command(BaseCommand):
    help = ("Updates (or creates) flatpages in the database using the "
            "contents of the files in flatpage-defaults.  Markdown or "
            "HTML are supported.")

    def add_arguments(self, parser):
        parser.add_argument(
            '--create-missing',
            dest="create_missing",
            action='store_true',
            help="Create new flatpage if one isn't found in the DB with that "
                 "url.")

    def handle(self, *args, **kwargs):
        fp_dir = os.path.join(os.getcwd(), 'flatpage-defaults')
        flatpage_files = [f for f
                          in os.listdir(fp_dir)
                          if os.path.isfile(os.path.join(fp_dir, f))]
        for page in flatpage_files:
            filename = os.path.join(os.getcwd(), 'flatpage-defaults', page)
            page_name = '/{}/'.format(
                '/'.join(page.split('-')).replace('.md', ''))
            with open(filename, 'r') as f:
                content = f.read()
            rendered_content = markdown.markdown(
                content,
                extensions=['pymdownx.extra', HoneycombMarkdown()])
            try:
                flatpage = FlatPage.objects.get(url=page_name)
                flatpage.content = rendered_content
                flatpage.save()
                mockable_print('{} updated.'.format(page_name))
            except FlatPage.DoesNotExist:
                if kwargs['create_missing']:
                    mockable_print('{} does not exist, '
                                   'creating.'.format(page_name))
                    flatpage = FlatPage(
                        url=page_name,
                        title=page,
                        content=rendered_content)
                    flatpage.save()
                    flatpage.sites = Site.objects.all()
                    mockable_print((u'- {} created (you should probably '
                                    u'update the title).').format(page_name))
                else:
                    mockable_print('{} does not exist, '
                                   'ignoring.'.format(page_name))
        mockable_print("\nIf there haven't been any errors, you should now "
                       "run:\n\n  make generatefixtures")
