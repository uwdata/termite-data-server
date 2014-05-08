'use strict';

/* Directives */


angular.module('termite.directives', [])
	.directive('ngEnter', function () {
    return function (scope, element, attrs) {
        element.bind("keypress", function (event) {
            if(event.which === 13) {
                scope.$apply(function (){
                    scope.$eval(attrs.ngEnter);
                });

                event.preventDefault();
            }
        });
    }
  })
  .directive('topicGraph', [function() {
    return {
    	restrict: 'E',
    	scope: {
    		topic: "="
    	},
    	link: function(scope, elm, attrs) {
    		// listen for an update event for this topic
    		scope.$on(scope.topic.id + ":update", function (event, data) { 
    			console.log('update this topic: ' + scope.topic.id);
    			update();
    		});

    		var topic = scope.topic;
      		//var width = $(elm).innerWidth(),
	    	//	height = $(elm).innerHeight();

	    	var width = 225, 
	    		height = 225;

	  		var color = d3.scale.category20();

	  		var k = Math.sqrt(topic.nodes.length / (width * height));
	  		var d = 2*topic.edges.length/(topic.nodes.length*(topic.nodes.length-1));

	  		d3.select(elm[0]).on("mouseover", function () {
	  			// highlight self and all connected topics
				angular.element(this).addClass("topic-hovered");
        		angular.forEach(topic.connections, function (t) {
            		angular.element(document.querySelector("#"+t.id)).addClass("topic-hovered");
        		});
	  		}).on("mouseout", function () {
        		angular.element(this).removeClass("topic-hovered");
        		angular.forEach(topic.connections, function (t) {
            		angular.element(document.querySelector("#"+t.id)).removeClass("topic-hovered");
        		});
	  		});

	  		var svg = d3.select(elm[0]).append("svg")
				.attr("width", width)
				.attr("height", height);

			//TODO: should the force directed layout take edge weight into account? 
			var force = d3.layout.force()
				.charge(-10 / k)
				.gravity(80 * k)
				// a denser graph needs the nodes to be pushed further away
				.linkDistance(Math.min(Math.max(50, 200*d), 200))
				//.linkStrength(function (d) { return Math.min(d.value/1000, 1); })
				.size([width, height]);	

			force
            	.nodes(topic.nodes)
            	.links(topic.edges);

            	var node = svg.selectAll(".node"),
            		link = svg.selectAll(".link");


	    	var update = function () {
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

			    function tick() {
			        link.attr("x1", function(d) { return d.source.x; })
			           .attr("y1", function(d) { return d.source.y; })
			           .attr("x2", function(d) { return d.target.x; })
			           .attr("y2", function(d) { return d.target.y; });

			        node.attr("transform", function(d) { 
			           	return 'translate(' + [d.x, d.y] + ')'; 
			        });  
			    }

	    		link = link 
			     //   .data(topic.edges);
			     .data(force.links(), function (d) {
			     	return d.source + "-" + d.target;
			     });


			    link.enter().append("line")
			        .attr("class", "link");

			    link.exit().remove();

			   	node = node
	          		//.data(topic.nodes);
	          		.data(force.nodes(), function (d) {
	          			return d.term;
	          		});

	          	var nodeEnter = node.enter().append("g")
	          		.attr("class", function(d) { return "node node__"+d.term + " " + d.class })
	      			// Highlight all matching term nodes
	      			.on( "mouseover", function(d) { d3.selectAll("g.node__"+d.term).classed({"hovered":true}); })//.style("fill", "#2ECC71").style("stroke", "#2ECC71") })
	      			.on( "mouseout", function(d) { d3.selectAll("g.node__"+d.term).classed({"hovered":false}); })//.style("fill", null).style("stroke", null) })
	      			// Toggle Select
	      			.on( "click", function (d) { 
	      				// if the node is already selected, unselect it 
	      				if (d3.select(this).classed("selected")) {
	      					var index = scope.topic.selectedWords.indexOf(d);
	      					if (index > -1) {
	      						scope.topic.selectedWords.splice(index, 1);
	      					}
	      					d3.select(this).classed({"selected": false});
	      					scope.$emit("node-unselected", scope.topic); 
	      				} else {
	      					// add to selected node list for the topic
		      				scope.topic.selectedWords.push(d);
		      				d3.select(this).classed({"selected": true}); 
		      				scope.$emit("node-selected", scope.topic);
	      				}
	      			});

	          	node.exit().remove();

	          	var circle = nodeEnter.append("circle")
		        	.attr("class", "circle")
		      	  	.attr("r", function (d) { return Math.min(d.value*2000, 40) + "px"; })
		        	.call(nodedrag);

		    	var label = nodeEnter.append("text")
		        	.attr("class", "term")
		        	.text(function(d) { return d.term})
		        	.attr("text-anchor", "middle")
		        	.call(nodedrag);

		    	nodeEnter.append("title")
		        	.text(function(d) { return d.term; });

		        var n = 100;
		    	force.start();
		      	for (var i = n * n; i > 0; --i) force.tick();
		      	force.stop();

		    	tick();


	    	} // update()

	    	// make it all go
	    	update();

    	} // link
  	}
  }
 ]);
