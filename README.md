Termite Web Server for Topic Models
===================================

Termite is a visualization tool for inspecting the output of statistical topic models.

The tool contains two components:
  * A web server for processing the output of a topic model and distributing the content over the internet.
  * A client interface for visualizing the topic model in a web browser.

This repository contains the server component for processing topic models and hosting the content on a web2py server. This middleware is developed by [Jason Chuang](http://jason.chuang.ca), and distributed under the BSD-3 license.

Topic modeling
--------------

Currently, this tool comes with scripts for training and importing:
  * [MALLET Topic Models](http://mallet.cs.umass.edu)
  * [Gensim](http://radimrehurek.com/gensim/)

We are in the process of adding support for:
  * [Interactive Topic Modeling](http://github.com/uwdata/termite-treetm)
  * [Structural Topic Models](http://github.com/uwdata/termite-stm)
  * [Stanford Topic Modeling Toolbox](http://nlp.stanford.edu/downloads/tmt/tmt-0.4/)

Setting up this web server
--------------------------

Run the setup script to fetch all required libraries. This script only needs to be run once when Termite Web Server for Topic Models is first downloaded onto a new machine.

```
bin/setup.sh
```

To launch the web server, execute the following command. A dialogue will appear. Click on "start server" to proceed.

```
bin/start_server.sh
```

Demo data and topic models
--------------------------

Two demo scripts are included in this repository.

Executing the following command will download the 20newsgroups dataset (18828 documents), build a LDA topic model with 20 latent topics, and launch the web server.

```
./demo-20newsgroups.sh
```

Executing the following command will download the InfoVis dataset (449 documents with metadata), build a LDA topic model with 20 latent topics, and launch the web server.

```
./demo-infovis.sh
```

The resulting topic model(s) will be available at:

```
http://127.0.0.1:8075/
```

API Format
----------

A goal of developing this server is to provide a common API (application programming interface), so that multiple topic model visualizations can interact with each other and with any number of topic modeling software.

All API calls to this web server are in following format.

```
http:// [server] / [dataset] / [model] / [attribute]
```

The string `[server]` is the base portion of the URL, such as `http://localhost:8080` when running a local machine.  As multiple projects can be hosted on the same server, `[dataset]` is a string `[A-Za-z0-9_]+` that uniquely identifies a project. A web-based visualization can access the content of a topic model by specifying the remaining URL `[model]/[attribute]`, such as `lda/TermTopicMatrix` and `treetm/TermTopicConstraints` to retrieve the term-topic matrix and send user-defined constraints to the server, respectively.

Credits
-------

Termite requires the use of the following software. We thank their respective authors for developing and distributing these tools.

  * [MALLET (MAchine Learning for LanguagE Toolkit)](http://mallet.cs.umass.edu) by Andrew McCallum, et al.
  * [Interactive Topic Modeling](http://www.cs.umd.edu/~ynhu) by Yuening Hu, et al.
  * Structural Topic Models by Margaret Roberts, et al.
  * [STMT (Stanford Topic Modeling Toolbox)](http://nlp.stanford.edu/downloads/tmt/tmt-0.4) by Daniel Ramage
  * [Gensim](http://radimrehurek.com/gensim) by Radim Řehůřek
  * [The web2py Web Framework](http://web2py.com) by Massimo Di Pierro, et al.
  * [Font Awesome](http://fontawesome.io) by Dave Gandy  

License
-------

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
