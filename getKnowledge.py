#!/usr/bin/env python3

import argparse
import os
import pathlib
from typing import List, Tuple, Dict, Optional, Union
import weakref

from knowledge_base import KnowledgeBase
from knowledge_enum import DebugLevels
from knowledge_logger import KnowledgeLogger

class Knowledge():
    """
        Driver class that contains knowledge utilities and interfaces them to
        the user, functioning as a shell-level program

        The idea is that string-like knowledge will be voted higher and higher
        based on the similarity of the string trigger and its contents to the
        user's input. Tools can also define tags to get them higher, but they
        should also be directly available via a --tool flag to select them
        directly.

        For implementing tools, the idea is that there could be MANY tools
        coming from MANY extensions, so no tools are created until they are
        selected. Tools will be instead be a wrapper class that contains the
        voting-bias information for vote time, and their __call__() will
        actively bring the tool's implementation into memory at runtime and
        pass any / all unparsed arguments in from that point onwards. As such,
        tools may prefer to auto-fail if they cannot parse their arguments
        robustly, encouraging the user to select them directly via the --tool
        flag so the remaining arguments are very easily controlled.
    """
    def __init__(self):
        # Make arguments
        parser = self.build()
        self.arguments, not_parsed = self.parse(parser)
        del parser
        # Set up logging
        self.logger = KnowledgeLogger(self.arguments.debug,
                                      self.arguments.logfile)

        # Set up knowledge base using configurations
        self.logger.info('Initialize KnowledgeBase')
        self.knowledge_base = KnowledgeBase(self.arguments,
                                            self.logger)
        self.logger.info('KnowledgeBase Ready')

        # Not-parsed arguments are expected to be a request of the knowledge base
        self.knowledge_request(not_parsed)

    def __del__(self):
        # If --help is given, the logger is never created and NO messages are
        # logged. Otherwise, cleanly denote the end of the program execution
        if hasattr(self, 'logger'):
            self.logger.info('Knowledge shutting down...\n')

    def build(self,
              existing_parser: Optional[argparse.ArgumentParser] = None,
              ) -> argparse.ArgumentParser:
        """
            I'm not sure if the knowledge class should be subclassed or not,
            but extending the option interface is relatively trivial as long
            as developers do not clash with the existing namespace
        """
        if existing_parser is None:
            existing_parser = argparse.ArgumentParser()

        default_help = "(default: %(default)s)"

        kl_args = existing_parser.add_argument_group("Knowledge")
        # Set as string so argparse displays it nicely, even though it will
        # display it as a list (we do not want argparse to try to call a
        # .extend() method on a string)
        kl_args.add_argument("--configuration", "-c",
                             default=[str(pathlib.Path(os.environ['HOME']) /
                                      ".pyknowledge" /
                                      "config.ini")],
                             nargs="*",
                             action="extend",
                             type=pathlib.Path,
                             help="Additional configuration files that point "
                                  "to custom knowledge sources, tools and "
                                 f"extensions {default_help}")
        kl_args.add_argument("--show-path", "-sp",
                             action="store_true",
                             help="Show the directory to add to your shell's "
                             "PATH variable so that you can getKnowledge from "
                             "any directory easily")
        kl_args.add_argument("--debug", "-d",
                             default='logged',
                             choices=list(DebugLevels),
                             type=DebugLevels,
                             help=f"Logging verbosity / behavior {default_help}")
        kl_args.add_argument("--logfile", "-l",
                             default=pathlib.Path(os.environ['HOME']) /
                                     ".pyknowledge" /
                                     "knowledge.log",
                             type=pathlib.Path,
                             help=f"Logfile location for debug {default_help}")
        kl_args.add_argument("--vote-query", "-v",
                             action="store_true",
                             help=f"Show votes for knowledge query {default_help}")
        return existing_parser

    def parse(self,
              parser: argparse.ArgumentParser,
              arguments: Optional[Union[List,argparse.Namespace]] = None,
              ) -> Union[argparse.Namespace,Tuple[argparse.Namespace,List]]:
        """
            I'm not sure if the knowledge class should be subclassed or not,
            but we expect to have unknown arguments that are passed along
            as keywords to knowledge search
        """
        (known_args, unknown_args) = parser.parse_known_args(arguments)
        if known_args.show_path:
            print(pathlib.Path(__file__).parents[0].resolve())
            exit(0)
        # Fix string path of explicit argument 0 to be pathlib.Path again
        known_args.configuration[0] = pathlib.Path(known_args.configuration[0])
        return (known_args, unknown_args)

    def knowledge_request(self, *args):
        votes, literal_votes, references = self.search_for_knowledge(*args)
        # Do some sorting based on votes (customizable)
        voted_knowledge = self.rank_votes(votes, literal_votes, references)
        # Execute the knowledge
        if callable(voted_knowledge):
            voted_knowledge(not_parsed)
        else:
            # Easter-egg / Tutorial
            if (" ".join(*args),) == ('Show me a magic demo!',):
                print("Thank you for using knowledge!")
                if len(self.knowledge_base) == 0:
                    print("It looks like your database doesn't have any "
                          "knowledge set up yet, but you can start adding "
                          "entries at "
                          f"{self.knowledge_base['knowledge.sources']['global']} "
                          "or develop Python tools within "
                          f"{self.knowledge_base['knowledge.tools']['global']}")
                else:
                    print(f"Your database has {len(self.knowledge_base)} items!")
                    print("You can add more knowledge at "
                          f"{self.knowledge_base['knowledge.sources']['global']} "
                          "or develop Python tools within "
                          f"{self.knowledge_base['knowledge.tools']['global']}")
                exit(0)
            print(voted_knowledge)

    def search_for_knowledge(self,
                             query: List[str],
                             ) -> Tuple[Dict[int,float],Dict[object,float],Dict[int,object]]:
        """
            Parse extra arguments and find the correct knowledge / tool to
            utilize by collecting votes across the knowledge base.
            Return the votes by mapping weakreferences to their votes
        """
        votes = dict()
        literal_votes = dict()
        references = weakref.WeakValueDictionary()
        for knowledge in self.knowledge_base:
            if type(knowledge) in [str, int, float]:
                literal_votes[knowledge] = 1.0
            if type(knowledge) is dict:
                for (k,v) in knowledge.items():
                    literal_votes[v] = 3.0 # Should be voted on by k using query
            else:
                references[id(knowledge)] = knowledge
                votes[id(knowledge)] = 2.0
        return votes, literal_votes, references

    def rank_votes(self,
                   votes: Dict[int,float],
                   literal_votes: Dict[object,float],
                   references: Dict[int,object],
                   ) -> object:
        """
            Decide which vote carries the most importance and return its object.
            Note that for literal votes, the KEY is the object to return.
            For non-literal votes, the weakreference indicated by the key should
            resolve to the appropriate object
        """
        #best_voted = list(votes.keys())[0]
        #best_vote_is_literal = False
        if len(literal_votes) == 0:
            return None
        best_voted = list(literal_votes.keys())[0]
        best_vote_is_literal = True
        if best_vote_is_literal:
            return best_voted
        else:
            return references[best_voted]

if __name__ == '__main__':
    Knowledge()

