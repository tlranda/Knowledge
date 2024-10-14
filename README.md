# Knowledge: A Shell Tool for Knowledge and Tooling in Python

## What is it?

**knowledge** is a Python package that tracks your own accumulated knowledge
and Python tools in a lightweight, shell-ready, and extensively customizable
manner.

## Can you show me what that looks like?

Absolutely! Setup is very simple:

```
# 1) Install knowledge
TODO: Demonstrate pypi or other installation on system (ie: pip install)
# 2) Add knowledge to your path:
$ export PATH="${PATH}:$(python3 getKnowledge.py --show-path)";
>
# 3) Run knowledge
$ getKnowledge "Show me a magic demo!"
> Thank you for using knowledge!
It looks like your database doesn't have any knowledge set up yet, but you can
start adding entries at ${HOME}/.pyknowledge/information.json or develop Python
tools within ${HOME}/.pyknowledge/tools
```

Why don't we add something simple to our knowledge database and retrieve it:
```
$ echo "
{
    "install knowledge": "pip install"
}
" > ${HOME}/.pyknowledge/information.json;
>
$ getKnowledge how do I install knowledge?
> pip install
```

## The keys features of **knowledge** are:

* Automatic fuzzy ranking: Enables you to quickly find items on-demand without
remembering every last detail or special syntax
* Global definition and local specification: Allows you to customize retrieved
knowledge based on the machine you use to retrieve it!
* 100% Offline: No internet required for usage, permitting fast (or as fast as
your Python interpreter permits) access rain or shine
* Human-Readable and Migratable: Easily port your knowledge from one place to
another by copying a few files. All data is stored in human-readable formats
so you always know what is recorded and can easily edit it yourself if needed

## How do I set up my knowledge?

First, you'll need to ensure your installation of Python is >= version 3.10.
PyKnowledge relies on various builtin modules, language features, and behaviors
that are not present in earlier versions of Python.

### Static knowledge

Static knowledge are located in JSON files (such as
${HOME}/.pyknowledge/information.json). Each key in the JSON should be the set
of tags you want to increase the likelihood of that knowledge being selected.
You can brainstorm a variety of triggers, but every word within the value will
automatically be considered as part of the helpfullness of that piece of knowledge,
albeit at half the rate as the key. So you can duplicate the word in the key if
you really want to emphasize it.

### Customized knowledge

(TODO: Explain how to customize static knowledge with separate files based on
your machine)

### Tools

You can implement simple python scripts in the tools directory. Knowledge will
scan for filenames here and load the `knowledge_tags` attribute from each file
to inform when the tool should be selected (TODO: Explain how knowledge tags
work). If your tool is selected to run, knowledge will attempt to import and
\_\_call\_\_() an attribute that has the same name as the file itself, with
a positional argument of the user's input to knowledge (ie: tools/my\_tool.py
would essentially run: from tools.my\_tool import my\_tool; my\_tool(query)).
The query is a list of strings, so you should parse it yourself before proceeding.

Users can also give the `--tool` flag to directly name a tool to reduce ambiguity,
so it's appropriate to call this out if your tool is unable to parse the query.

