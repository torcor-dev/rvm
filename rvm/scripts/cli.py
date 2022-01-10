import click
from tabulate import tabulate

from rvm.db.manager import Manager, TagManager, Filters

@click.group()
def cli():
    pass

@cli.command()
@click.option('--list', is_flag=True, is_eager=True, help='list all existing tags')
@click.option('--tag-subs', nargs=2, type=str, metavar='SUBS TAGS', help='add tags to subreddits')
@click.option('--untag-subs', nargs=2, type=str, metavar='SUBS TAGS', help='remove tags from subreddits')
@click.option('--tagged-subs', metavar='TAG', help='show a list of subreddits tagged by TAG')
@click.option('--untagged-subs', is_flag=True, help='show a list of untagged subreddits')
@click.option('--sub-tags', help='show a list of tags for the subreddit')
def tags(list, tag_subs, untag_subs, untagged_subs, sub_tags, tagged_subs):
    manager = TagManager()
    if list:
        result = manager.list_tags()
        click.echo(tabulate_result(result, 'Tags'))
    if tag_subs:
        subs, tags = split_args(tag_subs)
        result = manager.tag_subs(subs, tags)
        click.echo(result)
    if untag_subs:
        subs, tags = split_args(untag_subs)
        result = manager.untag_subs(subs, tags)
        click.echo(result)
    if untagged_subs:
        result = manager.untagged_subs()
        if not result:
            click.echo("No untagged subs", err=True)
        else:
            for sub in result:
                click.echo(sub)
    if tagged_subs:
        tag = tagged_subs.lower().strip()
        result = manager.tagged_subs(tag)
        if not result:
            click.echo(f'No subreddit found with tag {tag}', err=True)
        else:
            click.echo(tabulate_result(result, f'Subreddits tagged with "{tag}"'))
    if sub_tags:
        sub = sub_tags.lower().strip()
        result = manager.list_sub_tags(sub)
        if not result:
            click.echo(f'No tags found for "{sub_tags}"', err=True)
        else:
            for tag in result:
                click.echo(tag)


@cli.command()
@click.option('--root', help='root path to media directories')
@click.option('--title', help='include media from posts containing word or phrase in the title')
@click.option('--landscape', is_flag=True, help='only include wide media')
@click.option('--portrait', is_flag=True, help='only include tall media')
@click.option('--high-res', is_flag=True, help='only include media with high (1600x1200+) resolution')
@click.option('--absurd-res', is_flag=True, help='only include media with very high (3200x2400+) resolution')
@click.option('--no-strips', is_flag=True, help='exclude very tall and slim media - typically comic strips')
@click.option('--age', type=int, help='include media from posts no older than N days')
@click.option('--score', type=int, help='include media from posts with a score greater than N')
@click.option('--tags', help='''
        include media from subreddits tagged by any of the included tags
        example: --tags "foo bar"
        ''')
@click.option('--exclude-tags', help='''
        exclude media from subreddits tagged by any of the included tags
        example: --exclude-tags "foo bar"
        ''')
@click.option('--subreddits', help='include media from subreddits')
@click.option('--exclude-subreddits', help='exclude media from subreddits')
@click.option('--debug', is_flag=True, help='shows count of results of query, and raw SQL')
@click.option('--videos/--no-videos', default=False, help='\b\ninclude or exclude videos\n[Default: --no-videos]')
@click.option('--formats', help=f'\b\ninclude files of the listed formats\nuse "--formats {Filters.ALL_FORMATS}" to include every file type')
def list(title, landscape, portrait, high_res, absurd_res, no_strips, age, root, score, tags, exclude_tags, subreddits, exclude_subreddits, debug, videos, formats):
    manager = Manager()
    manager.new_query()
    
    if root:
        manager.root_path = root
    if title:
        manager.add_query_filter(Filters.TITLE, title)
    if landscape:
        manager.add_query_filter(Filters.ASPECT_RATIO, Filters.LANDSCAPE)
    if portrait:
        manager.add_query_filter(Filters.ASPECT_RATIO, Filters.PORTRAIT)
    if no_strips:
        manager.add_query_filter(Filters.ASPECT_RATIO, Filters.NO_COMIC_STRIPS)
    if high_res:
        manager.add_query_filter(Filters.RESOLUTION, Filters.HIGH_RES)
    if absurd_res:
        manager.add_query_filter(Filters.RESOLUTION, Filters.ABSURD_RES)
    if age:
        manager.add_query_filter(Filters.AGE, age)
    if score:
        manager.add_query_filter(Filters.SCORE, score)
    if tags:
        tags = tags.lower().strip()
        manager.add_query_filter(Filters.TAGS_INCLUDE, tags.split(' '))
    if exclude_tags:
        exclude_tags = exclude_tags.lower().strip()
        manager.add_query_filter(Filters.TAGS_EXCLUDE, exclude_tags.split(' '))
    if subreddits:
        subreddits = subreddits.lower().strip()
        manager.add_query_filter(Filters.SUBREDDITS_INCLUDE, subreddits.split(' '))
    if exclude_subreddits:
        exclude_subreddits = exclude_subreddits.lower().strip()
        manager.add_query_filter(Filters.SUBREDDITS_EXCLUDE, exclude_subreddits.split(' '))

    if formats:
        formats = formats.lower().strip().split(' ')
        if formats[0] != Filters.ALL_FORMATS:
            manager.add_query_filter(Filters.FORMATS, formats)
    elif videos:
        manager.add_query_filter(Filters.FORMATS, Filters.VIDEOS)
    else:
        manager.add_query_filter(Filters.FORMATS, Filters.IMAGES)

    if debug:
        manager.debug_query(5)
    else:
        result = manager.list_files()
        if result:
            for res in result:
                click.echo(res) 
        else:
            click.echo("No results found.", err=True)

def split_args(args):
    return (arg.strip().lower().split(' ') for arg in args)


def tabulate_result(result, heading):
        table = []
        for i in range(0, len(result), step:=4):
            table.append(result[i:step+i])
        headers = [heading] + [''] * (step-1)
        return tabulate(table, headers, tablefmt='simple')


if __name__ == '__main__':
    cli()
