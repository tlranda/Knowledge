Basic knowledge implementation:
* Make programatic interface to inspect / add knowledge to a document
* Make configuration updates to load dynamic knowledge (ie: based on hostname)

Basic knowledge search:
* Means to index all k,v of basic knowledge
    + Concept based on LLM byte-pair encoding. Parse out bi-grams and map them
    such that more bi-gram matches and more sequential matches ranks higher. Can
    do light spellcheck by adding minor score if an interrupted streak of bi-grams
    has a small edit distance or something

Basic tool implementation:
* Tools are labeled with an explicit name and tags (in the main tool file)
* Tools are dynamically imported and executed on their query when selected

Customized tool implementation:
* Configuration can supply directories to customize tool loading (should have
same name as tools they replace, but can change the tags / implementation to affect
scoring and usage)
* Provide an API for tools to load other tools to facilitate reuse that adheres
to current environment

Nice to have:
* Query file sizes of indexed structures (logs, knowledge bases, configurations)
