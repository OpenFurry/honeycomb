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
    """A command for updating the site's flatpages from a directory of files.
    """
    help = ("Updates (or creates) flatpages in the database using the "
            "contents of the files in flatpage-defaults.  Markdown or "
            "HTML are supported. Files should be named after the flatpage "
            "URL, with slashes replaced with dashes (e.g: about-terms.md for "
            "the flatpage living at /about/terms/)")

    def add_arguments(self, parser):
        """Adds arguments via argparse"""
        parser.add_argument(
            '--create-missing',
            dest="create_missing",
            action='store_true',
            help="Create new flatpage if one isn't found in the DB with that "
                 "url.")

    def handle(self, *args, **kwargs):
        """Updates and potentially creates flatpages from files on disk.

        This command expects a directory named flatpage-defaults in the project
        root to be filled with markdown/HTML files, named after the flatpage
        URL that they represent (e.g: `about-terms.md` for the flatpage living
        at `/about/terms/`).  If the command-line argument `--create-missing`
        is passed, new pages will be created, otherwise files not matching up
        with a flatpage will be ignored.
        """
        # Get a list of files to turn into flatpages.
        fp_dir = os.path.join(os.getcwd(), 'flatpage-defaults')
        flatpage_files = [f for f
                          in os.listdir(fp_dir)
                          if os.path.isfile(os.path.join(fp_dir, f))]

        for page in flatpage_files:
            filename = os.path.join(os.getcwd(), 'flatpage-defaults', page)

            # Attempt to find a matching flatpage for the file
            page_name = '/{}/'.format(
                '/'.join(page.split('-')).replace('.md', ''))

            # Render any markdown.
            with open(filename, 'r') as f:
                content = f.read()
            rendered_content = markdown.markdown(
                content,
                extensions=[
                    'pymdownx.extra',
                    'markdown.extensions.codehilite',
                    'pymdownx.headeranchor',
                    'pymdownx.magiclink',
                    'pymdownx.smartsymbols',
                    'pymdownx.tilde',
                    'pymdownx.mark',
                    HoneycombMarkdown(),
                ])

            # Retrieve the flatpage and update it.
            try:
                flatpage = FlatPage.objects.get(url=page_name)
                flatpage.content = rendered_content
                flatpage.save()
                mockable_print('{} updated.'.format(page_name))
            except FlatPage.DoesNotExist:
                if kwargs['create_missing']:
                    # Create the page if it does not exist, but only if we have
                    # been told to do so.
                    mockable_print('{} does not exist, '
                                   'creating.'.format(page_name))
                    flatpage = FlatPage(
                        url=page_name,
                        title=page,
                        content=rendered_content)
                    flatpage.save()

                    # Add the flatpage to all sites.
                    flatpage.sites = Site.objects.all()
                    mockable_print((u'- {} created (you should probably '
                                    u'update the title).').format(page_name))
                else:
                    # Otherwise, just warn the user.
                    mockable_print('{} does not exist, '
                                   'ignoring.'.format(page_name))
        mockable_print("\nIf there haven't been any errors, you should now "
                       "run:\n\n  make generatefixtures")
