function graph (topic) {
    var $el = angular.element("#" + topic.id);

    // Add and remove elements on the graph object
    this.addNode = function (node) {
        nodes.push(node);
        update();
    }

    this.removeNode = function (name) {
        var i = 0;
        var n = findNode(name);
        while (i < links.length) {
            if ((links[i]['source'] == n)||(links[i]['target'] == n)) links.splice(i,1);
            else i++;
        }
        nodes.splice(findNodeIndex(id),1);
        update();
    }

    this.addLink = function (source, target) {
        links.push({"source":findNode(source),"target":findNode(target)});
        update();
    }

    this.layout = function (layout) {
        $el.css(layout);
    }

    var findNode = function(name) {
        for (var i in nodes) {if (nodes[i]["name"] === name) return nodes[i]};
    }

    var findNodeIndex = function(name) {
        for (var i in nodes) {if (nodes[i]["name"] === name) return i};
    }

    // set up the D3 visualisation in the specified element
    var w = $el.innerWidth(),
        h = $el.innerHeight();

    var k = Math.sqrt(topic.nodes.length / (w * h)),
        d = 2*topic.edges.length/(topic.nodes.length*(topic.nodes.length-1));

        d3.select("#" + topic.id).on("mouseover", function () {
        // highlight self and all connected topics
        angular.element(this).addClass("topic-hovered");
        angular.forEach(topic.connections, function (t) {
            angular.element("#"+t.id).addClass("topic-hovered");
        });
    }).on("mouseout", function () {
        angular.element(this).removeClass("topic-hovered");
        angular.forEach.each(topic.connections, function (t) {
            angular.element("#"+t.id).removeClass("topic-hovered");
        });
    })

    var vis = this.vis = d3.select("#" + topic.id + "> .topic-svg").append("svg")
        .attr("width", w)
        .attr("height", h);

    var force = d3.layout.force()
        .charge(-10 / k)
        .gravity(80 * k)
        // a denser graph needs the nodes to be pushed further away
        .linkDistance(Math.min(Math.max(50, 200*d), 200))
        .size([w, h]);

        force
            .nodes(topic.nodes)
            .links(topic.edges);

    var nodes = force.nodes(),
        links = force.links();

    /**
     * [update description]
     * @return {[type]} [description]
     */
    var update = function () {

        var link = vis.selectAll(".link")
           .data(links);


        link.enter().append("line")
           .attr("class", "link");

        link.exit().remove();

        var node = vis.selectAll("g.node")
            .data(nodes);

                var nodedrag = d3.behavior.drag()
        .on("dragstart", dragstart)
        .on("drag", dragmove)
        .on("dragend", dragend);

    function dragstart(d, i) {
      //  force.stop() // stops the force auto positioning before you start dragging
    }

    function dragmove(d, i) {
        d.px += d3.event.dx;
        d.py += d3.event.dy;
        d.x += d3.event.dx;
        d.y += d3.event.dy; 
        tick(); // this is the key to make it work together with updating both px,py,x,y on d !
    }

    function dragend(d, i) {
        d.fixed = true; // of course set the node to fixed so the force doesn't include the node in its auto positioning stuff
        tick();
       // force.resume();
    }

        var nodeEnter = node.enter().append("g")
            .attr("class", function(d) { return "node node__"+d.name + " " + d.class })
            // Highlight all matching term nodes
            .on( "mouseover", function(d) { d3.selectAll("g.node__"+d.name).classed({"hovered":true}); })//.style("fill", "#2ECC71").style("stroke", "#2ECC71") })
            .on( "mouseout", function(d) { d3.selectAll("g.node__"+d.name).classed({"hovered":false}); })//.style("fill", null).style("stroke", null) })
            // Toggle Select
            .on( "click", function (d) { d3.select(this).classed({"selected": true}) });


        node.exit().remove();

        var circle = nodeEnter.append("circle")
            .attr("class", "circle")
            .attr("r", function (d) { return Math.min(d.value/10, 40) + "px"; })
            .call(nodedrag);

        var label = nodeEnter.append("text")
            .attr("class", "term")
            .text(function(d) { return d.name})
            .attr("text-anchor", "middle")
            .call(nodedrag);

        nodeEnter.append("title")
          .text(function(d) { return d.name; });


        var n = 100;
        force.start();
        for (var i = n * n; i > 0; --i) force.tick();
        force.stop();

        tick();

            function tick() {
            link.attr("x1", function(d) { return d.source.x; })
                    .attr("y1", function(d) { return d.source.y; })
                    .attr("x2", function(d) { return d.target.x; })
                    .attr("y2", function(d) { return d.target.y; });

            node.attr("transform", function(d) { 
                return 'translate(' + [d.x, d.y] + ')'; 
            });  
    }

    }

    // Make it all go
    update();

}