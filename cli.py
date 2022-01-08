import click
from tabulate import tabulate

from db.manager import Manager, TagManager, Filters

@click.group()
def cli():
    pass

@cli.command()
@click.option('--list', is_flag=True, is_eager=True, help='list all existing tags')
@click.option('--tag-subs', nargs=2, type=str, metavar='SUBS TAGS', help='add tags to subreddits')
@click.option('--untag-subs', nargs=2, type=str, metavar='SUBS TAGS', help='remove tags from subreddits')
def tags(list, tag_subs, untag_subs):
    manager = TagManager()
    if list:
        result = manager.list_tags()
        click.echo(tabulate_tags(result))
    if tag_subs:
        subs, tags = split_args(tag_subs)
        result = manager.tag_subs(subs, tags)
        click.echo(result)
    if untag_subs:
        subs, tags = split_args(untag_subs)
        result = manager.untag_subs(subs, tags)
        click.echo(result)


@cli.command()
@click.option('--root', help='root path to image directories')
@click.option('--title', help='include images from posts containing word or phrase in the title')
@click.option('--landscape', is_flag=True, help='only include wide images')
@click.option('--portrait', is_flag=True, help='only include tall images')
@click.option('--high-res', is_flag=True, help='only include images with high (1600x1200+) resolution')
@click.option('--absurd-res', is_flag=True, help='only include images with very high (3200x2400+) resolution')
@click.option('--no-strips', is_flag=True, help='exclude very tall and slim images - typically comic strips')
@click.option('--age', type=int, help='include images from posts no older than N days')
@click.option('--score', type=int, help='include images from posts with a score greater than N')
@click.option('--tags', help='''
        include images from subreddits tagged by any of the included tags
        example: --tags "foo bar"
        ''')
@click.option('--exclude-tags', help='''
        exclude images from subreddits tagged by any of the included tags
        example: --exclude-tags "foo bar"
        ''')
@click.option('--subreddits', help='include images from subreddits')
@click.option('--exclude-subreddits', help='exclude images from subreddits')
def list(title, landscape, portrait, high_res, absurd_res, no_strips, age, root, score, tags, exclude_tags, subreddits, exclude_subreddits):
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
        tags = tags.strip()
        manager.add_query_filter(Filters.TAGS_INCLUDE, tags.split(' '))
    if exclude_tags:
        exclude_tags = exclude_tags.strip()
        manager.add_query_filter(Filters.TAGS_EXCLUDE, exclude_tags.split(' '))
    if subreddits:
        subreddits = subreddits.strip()
        manager.add_query_filter(Filters.SUBREDDITS_INCLUDE, subreddits.split(' '))
    if exclude_subreddits:
        exclude_subreddits = exclude_subreddits.strip()
        manager.add_query_filter(Filters.SUBREDDITS_EXCLUDE, exclude_subreddits.split(' '))

    #manager.debug_query(5)
    result = manager.list_files()
    for res in result:
        click.echo(res) 
    else:
        click.echo("No results found.", err=True)

def split_args(args):
    return (arg.strip().split(' ') for arg in args)


def tabulate_tags(result):
        table = []
        for i in range(0, len(result), step:=4):
            table.append(result[i:step+i])
        headers = ['Tags'] + [''] * (step-1)
        return tabulate(table, headers, tablefmt='simple')


if __name__ == '__main__':
    cli()
