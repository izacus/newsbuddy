"""
Main entry point for several newsbuddy utility methods
"""
import argparse

def do_action(action, arguments):
    print arguments
    if action == "parse-news":
        import commands.parse
        commands.parse.parse_news()
    elif action == "export-solr":
        import commands.db_to_solr
        commands.db_to_solr.export_to_solr()
    elif action == "runserver":
        import commands.runserver
        commands.runserver.runserver(arguments.hostname, arguments.port)
    elif action == "purge-duplicates":
        import commands.purge_duplicates
        commands.purge_duplicates.purge_duplicates(arguments.commit)
    elif action == "tag-news":
        import commands.tag_news
        commands.tag_news.tag_news(arguments.retag)

parser = argparse.ArgumentParser(description="Newsbuddy command-line utility methods.", add_help=True)
subcommands = parser.add_subparsers(title="commands", dest='action')
runserver_parser = subcommands.add_parser('runserver', help="Runs local development server")
runserver_parser.add_argument("hostname", default="0.0.0.0", nargs="?")
runserver_parser.add_argument("port", default="8005", type=int, nargs="?")
parse_parser = subcommands.add_parser('parse-news', help="Parse news")
solr_parser = subcommands.add_parser('export-solr', help="Export database into Solr")
purge_parser = subcommands.add_parser('purge-duplicates', help="Purge duplicate news from DB")
purge_parser.add_argument("commit", default=False, type=bool, nargs="?")
tag_parser = subcommands.add_parser('tag-news', help="Tag news")
tag_parser.add_argument("retag", help="Retag already tagged news", default=False, nargs="?")
args = parser.parse_args()
do_action(args.action, args)