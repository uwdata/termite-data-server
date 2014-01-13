Termite Web Server for STM models
=================================

Termite is a visualization tool for inspecting the output of statistical topic models.

The tool contains two components:
  * A web server for accessing the output of a topic model and distributing the content over the internet.
  * A client interface for visualizing the topic model in a web browser.

This repository contains the server-side component for processing the output of an Structural Topic Model (STM) and hosting the content on a web2py server. This middleware is developed by [Jason Chuang](http://jason.chuang.ca), and distributed under the BSD-3 license. Structural Topic Modeling is developed by Margaret Roberts and Brandon Stewart, et al. [The web2py Web Framework](http://web2py.com) is developed by Massimo Di Pierro, et al.

Using the software
------------------

Run the setup script to fetch all required libraries. This script only needs to be run once when Termite Web Server for MALLET is first downloaded onto a new machine.

```
bin/setup.sh
```

To launch the web server, execute the following command. A dialogue will appear. Click on "start server" to proceed.

```
bin/start_server.sh
```

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

Credits
-------

Termite requires the use of the following libraries and tools.
We thank their respective authors for developing and distributing these tools.

  Structural Topic Models  
  Paper website: http://scholar.harvard.edu/mroberts, http://scholar.harvard.edu/bstewart 
  Developed by Margaret Roberts and Brandon Stewart, et al.  

  The web2py Web Framework  
  Project website: http://web2py.com  
  Developed by Massimo Di Pierro, et al.  

  Font Awesome  
  Project website: http://fontawesome.io  
  Developed by Dave Gandy  
