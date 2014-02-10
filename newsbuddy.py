"""
Main entry point for several newsbuddy utility methods
"""
import argparse

def do_action(action, arguments):
    print arguments
    if action == "parse-news":
        import cmd.parse
        cmd.parse.parse_news()
    elif action == "export-solr":
        import cmd.db_to_solr
        cmd.db_to_solr.export_to_solr()
    elif action == "runserver":
        import cmd.runserver
        cmd.runserver.runserver(arguments.hostname, arguments.port)



parser = argparse.ArgumentParser(description="Newsbuddy command-line utility methods.", add_help=True)
subcommands = parser.add_subparsers(title="commands", dest='action')
runserver_parser = subcommands.add_parser('runserver', help="Runs local development server")
runserver_parser.add_argument("hostname", default="0.0.0.0", nargs="?")
runserver_parser.add_argument("port", default="8005", type=int, nargs="?")
parse_parser = subcommands.add_parser('parse-news', help="Parse news")
solr_parser = subcommands.add_parser('export-solr', help="Export database into Solr")
args = parser.parse_args()
do_action(args.action, args)