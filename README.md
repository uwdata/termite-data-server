Data Server for Topic Models
============================

Termite is a visual analysis tool for exploring the output of statistical topic models.

This repository contains:
  * a web server based on the web2py framework
  * helper scripts to download various datasets
  * helper scripts to download and setup various topic modeling tools
  * helper scripts to build topic models
  * helper scripts to import topic model outputs into the server

The web server includes various interactive visualizations:
  * term-topic matrix
  * group-in-a-box visualization
  * scatter plot

This software is distributed under the BSD-3 license.

Contributors and Credits
------------------------

The Termite Data Server is developed and maintained by [Jason Chuang](http://jason.chuang.ca) with contributions from:
 * [Ashley Jin](http://www.linkedin.com/in/ashpjin) on the initial implementation of the Termite Data Server, the term-topic matrix visualization, and various data processing scripts
 * [Alison Smith](http://www.cs.umd.edu/people/amsmit) on the group-in-a-box visualization
 * [Michael Freeman](https://www.linkedin.com/pub/michael-freeman/66/363/322) on the scatter plot visualization
 * [Peter Enns](https://www.linkedin.com/pub/peter-enns/37/674/408) on the web server upload functionality
 * [Leo Claudino](http://www.linkedin.com/in/claudino) on data processing for interactive topic models
 * [Yuening Hu](http://www.cs.umd.edu/~ynhu) on data processing for interactive topic models
 * [Molly Roberts](http://scholar.harvard.edu/mroberts/home) on data processing for structural topic models

Termite requires on the use of the following software. We thank their respective authors for developing and distributing these tools.

  * [MALLET (MAchine Learning for LanguagE Toolkit)](http://mallet.cs.umass.edu) by Andrew McCallum, et al.
  * [Interactive Topic Modeling](http://www.cs.umd.edu/~ynhu) by Yuening Hu, et al.
  * Structural Topic Models by Margaret Roberts, et al.
  * [Stanford Topic Modeling Toolbox](http://nlp.stanford.edu/downloads/tmt/tmt-0.4) by Daniel Ramage
  * [Gensim](http://radimrehurek.com/gensim) by Radim Řehůřek
  * [The web2py Web Framework](http://web2py.com) by Massimo Di Pierro, et al.
  * [Font Awesome](http://fontawesome.io) by Dave Gandy  

Launch this data server
=======================

Currently, this data server can import topic models from:
  * [MALLET](http://mallet.cs.umass.edu)
  * [Gensim](http://radimrehurek.com/gensim/)
  * [Interactive Topic Modeling](http://github.com/uwdata/termite-treetm)
  * [Structural Topic Models](http://github.com/uwdata/termite-stm)

We are in the process of adding support for:
  * [Stanford Topic Modeling Toolbox](http://nlp.stanford.edu/downloads/tmt/tmt-0.4/)

The data server can be deployed on [various platforms supported by web2py](http://web2py.com/books/default/chapter/29/13/deployment-recipes).  However, the copy included in the repository is customized for Apple's OSX.

Preparations
------------

At the time of writing, the following three tools need to be installed when this repository is first cloned.  Execute the following commands at the root of the repository.

```
bin/setup_corenlp.sh
bin/setup_mallet.sh
make -C utils/corenlp
```

Start the web server
--------------------

To launch this data server, execute the following command. A dialogue box will appear. Click on "start server" to proceed.

```
./start_server.sh
```

Build a topic model
-------------------

Several demos are included in this repository.

Executing the following command will download the 20newsgroups dataset (18828 documents), build an LDA topic model with 20 latent topics using MALLET, and launch the web server.

```
./demo.py 20newsgroups
```

Executing the following command will download the InfoVis dataset (449 documents with metadata), build an LDA topic model with 20 latent topics using MALLET, and launch the web server.

```
./demo.py infovis
```

To build an example topic model on the InfoVis dataset using Gensim:

```
./demo.py infovis gensim
```

More generally, to build a topic model on `dataset` using `tool`:

```
./demo.py [dataset] [tool]
```

To see more demo options:

```
./demo.py --help
```

The resulting topic model(s) will be available at:

```
http://127.0.0.1:8075/
```

Active Research Project
=======================

This is an active research project. While we would like to support as many users as possible, we are constrained by available resources. Below are the system requirements, known issues as well as the API format, for developing additional visualizations and incorporating additional models to the data server.

System requirements
-------------------

  * **Python 2.7** for web2py, server scripts, and other helper scripts
  * **Java** for MALLET
  * [Optional] NumPy 1.3, SciPy 0.7 for Gensim
  * [Optional] R for Structural Topic Models

Known issues
------------

The web server is based on the web2py framework. While web2py is designed to work on Windows, Mac, and most Unix platforms, we have only tested the system on OSX. The framework will not work under Cygwin on Windows.

API format
----------

A primary goal of developing this data server is to provide a common API (application programming interface), so that multiple topic model visualizations can interact with any number of topic modeling software, and with other visualizations.

All API calls to this web server are in following format.

```
http:// [server] / [dataset] / [model] / [attribute]
```

The string `[server]` is the base portion of the URL, such as `http://localhost:8080` when running a local machine.  As multiple projects can be hosted on the same server, `[dataset]` is a string `[A-Za-z0-9_]+` that uniquely identifies a project. A web-based visualization can access the content of a topic model by specifying the remaining URL `[model]/[attribute]`, such as `lda/TermTopicMatrix` and `treetm/TermTopicConstraints` to retrieve the term-topic matrix and send user-defined constraints to the server, respectively.

License
=======

Copyright (c) 2013, Leland Stanford Junior University
Copyright (c) 2014, University of Washington
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:
  * Redistributions of source code must retain the above copyright
    notice, this list of conditions and the following disclaimer.
  * Redistributions in binary form must reproduce the above copyright
    notice, this list of conditions and the following disclaimer in the
    documentation and/or other materials provided with the distribution.
  * Neither the name of the <organization> nor the
    names of its contributors may be used to endorse or promote products
    derived from this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL <COPYRIGHT HOLDER> BE LIABLE FOR ANY
DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
(INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
