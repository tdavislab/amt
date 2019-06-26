document.onload = (function(d3, saveAs, Blob, undefined){
    "use strict";
    var consts = {
	defaultTitle: "random variable"
    };
    var settings = {
	appendElSpec1: "#graph1",
	appendElSpec2: "#graph2",
	appendElSpec3: "#graph3",
	appendElSpec4: "#graph4"
	
    };
    // define graphcreator object
    var GraphCreator = function(svg, nodes, edges, Domain, height){
	var thisGraph = this;
	thisGraph.domain = Domain;
        thisGraph.idct = 0;
	thisGraph.svgheight = height;
	
	thisGraph.nodes = nodes || [];
	thisGraph.edges = edges || [];
	
	thisGraph.state = {
	    selectedNode: null,
	    selectedEdge: null,
	    mouseDownNode: null,
	    mouseDownLink: null,
	    justDragged: false,
	    justScaleTransGraph: false,
	    lastKeyDown: -1,
	    shiftNodeDrag: false,
	    selectedText: null
	};

	thisGraph.consts =  {
	    selectedClass: "selected",
	    connectClass: "connect-node",
	    circleGClass: "conceptG",
	    graphClass: "graph",
	    activeEditId: "active-editing",
	    BACKSPACE_KEY: 8,
	    DELETE_KEY: 46,
	    ENTER_KEY: 13,
	    nodeRadius: 30
	};

	

	
	thisGraph.svg = svg;
	thisGraph.svgG = svg.append("g")
            .classed(thisGraph.consts.graphClass, true);
	var svgG = thisGraph.svgG;
	
	// displayed when dragging between nodes
	thisGraph.dragLine = svgG.append('svg:path')
            .attr('class', 'link dragline hidden')
            .attr('d', 'M0,0L0,0');

	// svg nodes and edges
	thisGraph.paths = svgG.append("g").selectAll("g");
	thisGraph.circles = svgG.append("g").selectAll("g");
	
	thisGraph.drag = d3.behavior.drag()
            .origin(function(d){
		return {x: d.x, y: d.y};
            })
            .on("drag", function(args){
		thisGraph.state.justDragged = true;
		thisGraph.dragmove.call(thisGraph, args);
            })
            .on("dragend", function() {
		// todo check if edge-mode is selected
            });
	// listen for key events
	d3.select(thisGraph.domain).on("keydown", function(){
	    thisGraph.svgKeyDown.call(thisGraph);
	})
	    .on("keyup", function(){
		thisGraph.svgKeyUp.call(thisGraph);
	    });
	svg.on("mousedown", function(d){thisGraph.svgMouseDown.call(thisGraph, d);});
	svg.on("mouseup", function(d){thisGraph.svgMouseUp.call(thisGraph, d);});
	
	// listen for dragging
	var dragSvg = d3.behavior.zoom()
            .on("zoom", function(){
		if (d3.event.sourceEvent.shiftKey){
		    // TODO  the internal d3 state is still changing
		    return false;
		}
		/*
		else {
		    thisGraph.zoomed.call(thisGraph);
		}
		*/
		return true;
            })
            .on("zoomstart", function(){
		var ael = d3.select("#" + thisGraph.consts.activeEditId).node();
		if (ael){
		    ael.blur();
		}
		//if (!d3.event.sourceEvent.shiftKey) d3.select('body').style("cursor", "move");
            })
            .on("zoomend", function(){
		d3.select('body').style("cursor", "auto");
            });
	
	svg.call(dragSvg).on("dblclick.zoom", null);

	
	thisGraph.setIdCt = function(idct){
	    this.idct = idct;
	};

	thisGraph.dragmove = function(d) {
	    var thisGraph = this;
	    if (thisGraph.state.shiftNodeDrag){
		thisGraph.dragLine.attr('d', 'M' + d.x + ',' + d.y + 'L' + d3.mouse(thisGraph.svgG.node())[0] + ',' + d3.mouse(this.svgG.node())[1]);
	    } else{
		d.x += d3.event.dx;
		d.y +=  d3.event.dy;
		thisGraph.updateGraph();
	    }
	};
	
	thisGraph.deleteGraph = function(skipPrompt){
	    var thisGraph = this,
		doDelete = true;
	    if (!skipPrompt){
		doDelete = window.confirm("Press OK to delete this graph");
	    }
	    if(doDelete){
		thisGraph.nodes = [];
		thisGraph.edges = [];
		thisGraph.updateGraph();
	    }
	};


	/* select all text in element: taken from http://stackoverflow.com/questions/6139107/programatically-select-text-in-a-contenteditable-html-element */
	thisGraph.selectElementContents = function(el) {
	    var range = document.createRange();
	    range.selectNodeContents(el);
	    var sel = window.getSelection();
	    sel.removeAllRanges();
	    sel.addRange(range);
	};
	
    
	/* insert svg line breaks: taken from http://stackoverflow.com/questions/13241475/how-do-i-include-newlines-in-labels-in-d3-charts */
	thisGraph.insertTitleLinebreaks = function (gEl, title) {
	   
	    var words = title.split(/\s+/g),
		nwords = words.length;
	    var el = gEl.append("text")
		.attr("text-anchor","middle")
		.attr("dy", "6px")
		.attr("font-size", "25px");
	    
	    for (var i = 0; i < words.length; i++) {
		var tspan = el.append('tspan').text(words[i]);
		if (i > 0)
		    tspan.attr('x', 0).attr('dy', '15');
	    }
	};

	thisGraph.showPosition = function (gEl) {
	   
	    console.log(gEl[0][0].__data__.x);
	};
    
	// remove edges associated with a node
	thisGraph.spliceLinksForNode = function(node) {
	    var thisGraph = this,
		toSplice = thisGraph.edges.filter(function(l) {
		    return (l.source === node || l.target === node);
		});
	    toSplice.map(function(l) {
		thisGraph.edges.splice(thisGraph.edges.indexOf(l), 1);
	    });
	};
	
	thisGraph.replaceSelectEdge = function(d3Path, edgeData){
	    var thisGraph = this;
	    d3Path.classed(thisGraph.consts.selectedClass, true);
	    if (thisGraph.state.selectedEdge){
		thisGraph.removeSelectFromEdge();
	    }
	    thisGraph.state.selectedEdge = edgeData;
	};
	
	thisGraph.replaceSelectNode = function(d3Node, nodeData){
	    var thisGraph = this;
	    d3Node.classed(this.consts.selectedClass, true);
	    if (thisGraph.state.selectedNode){
		thisGraph.removeSelectFromNode();
	    }
	    thisGraph.state.selectedNode = nodeData;
	};
    
	thisGraph.removeSelectFromNode = function(){
	    var thisGraph = this;
	    thisGraph.circles.filter(function(cd){
		return cd.id === thisGraph.state.selectedNode.id;
	    }).classed(thisGraph.consts.selectedClass, false);
	    thisGraph.state.selectedNode = null;
	};
    
	thisGraph.removeSelectFromEdge = function(){
	    var thisGraph = this;
	    thisGraph.paths.filter(function(cd){
		return cd === thisGraph.state.selectedEdge;
	    }).classed(thisGraph.consts.selectedClass, false);
	    thisGraph.state.selectedEdge = null;
	};
    
	thisGraph.pathMouseDown = function(d3path, d){
	    var thisGraph = this,
		state = thisGraph.state;
	    d3.event.stopPropagation();
	    state.mouseDownLink = d;
	    
	    if (state.selectedNode){
		thisGraph.removeSelectFromNode();
	    }
	
	    var prevEdge = state.selectedEdge;
	    if (!prevEdge || prevEdge !== d){
		thisGraph.replaceSelectEdge(d3path, d);
	    } else{
		thisGraph.removeSelectFromEdge();
	    }
	};
	
	// mousedown on node
	thisGraph.circleMouseDown = function(d3node, d){
	    var thisGraph = this,
		state = thisGraph.state;
	    d3.event.stopPropagation();
	    state.mouseDownNode = d;
	    if (d3.event.shiftKey){
		state.shiftNodeDrag = d3.event.shiftKey;
		// reposition dragged directed edge
		thisGraph.dragLine.classed('hidden', false)
		    .attr('d', 'M' + d.x + ',' + d.y + 'L' + d.x + ',' + d.y);
		return;
	    }
	};
	
	/* place editable text on node in place of svg text */
	thisGraph.changeTextOfNode = function(d3node, d){
	    var thisGraph= this,
		consts = thisGraph.consts,
		htmlEl = d3node.node();
	    d3node.selectAll("text").remove();
	    var nodeBCR = htmlEl.getBoundingClientRect(),
		curScale = nodeBCR.width/consts.nodeRadius,
		placePad  =  5*curScale,
		useHW = curScale > 1 ? nodeBCR.width*0.71 : consts.nodeRadius*1.42;
	    // replace with editableconent text
	    var d3txt = thisGraph.svg.selectAll("foreignObject")
		.data([d])
		.enter()
		.append("foreignObject")
		.attr("x", d.x- consts.nodeRadius*0.7)
		.attr("y", d.y- consts.nodeRadius*0.7)
		.attr("height", useHW)
		.attr("width", useHW)
		.append("xhtml:p")
		.attr("id", consts.activeEditId)
		.attr("contentEditable", "true")
		.text(d.title)
		.on("mousedown", function(d){
		    d3.event.stopPropagation();
		})
		.on("keydown", function(d){
		    d3.event.stopPropagation();
		    if (d3.event.keyCode == consts.ENTER_KEY && !d3.event.shiftKey){
			this.blur();
		    }
		})
		.on("blur", function(d){
		    d.title = this.textContent;
		    thisGraph.insertTitleLinebreaks(d3node, d.title);
		    d3.select(this.parentElement).remove();
		});
	    return d3txt;
	};
    
	// mouseup on nodes
	thisGraph.circleMouseUp = function(d3node, d){
	    var thisGraph = this,
		state = thisGraph.state,
		consts = thisGraph.consts;
	    // reset the states
	    state.shiftNodeDrag = false;
	    d3node.classed(consts.connectClass, false);
	    
	    var mouseDownNode = state.mouseDownNode;
	    
	    if (!mouseDownNode) return;
	    
	    thisGraph.dragLine.classed("hidden", true);
	    
	    if (mouseDownNode !== d){
		// we're in a different node: create new edge for mousedown edge and add to graph
		var newEdge = {source: mouseDownNode, target: d};
		var filtRes = thisGraph.paths.filter(function(d){
		    if (d.source === newEdge.target && d.target === newEdge.source){
			thisGraph.edges.splice(thisGraph.edges.indexOf(d), 1);
		    }
		    return d.source === newEdge.source && d.target === newEdge.target;
		});
		if (!filtRes[0].length){
		    thisGraph.edges.push(newEdge);
		    thisGraph.updateGraph();
		}
	    } else{
		// we're in the same node
		if (state.justDragged) {
		    // dragged, not clicked
		    state.justDragged = false;
		} else{
		    // clicked, not dragged
		    if (d3.event.shiftKey){
			// shift-clicked node: edit text content
			var d3txt = thisGraph.changeTextOfNode(d3node, d);
			var txtNode = d3txt.node();
			thisGraph.selectElementContents(txtNode);
			txtNode.focus();
		    } else{
			if (state.selectedEdge){
			    thisGraph.removeSelectFromEdge();
			}
			var prevNode = state.selectedNode;
			
			if (!prevNode || prevNode.id !== d.id){
			    thisGraph.replaceSelectNode(d3node, d);
			} else{
			    thisGraph.removeSelectFromNode();
			}
		    }
		}
	    }
	    state.mouseDownNode = null;
	    return;
	
	}; // end of circles mouseup
    
	// mousedown on main svg
	thisGraph.svgMouseDown = function(){
	    this.state.graphMouseDown = true;
	};
    
	// mouseup on main svg
	thisGraph.svgMouseUp = function(){
	    var thisGraph = this,
		state = thisGraph.state;
	  
	    if (state.justScaleTransGraph) {
		// dragged not clicked
		state.justScaleTransGraph = false;
	    } else if (state.graphMouseDown && d3.event.shiftKey){
		// clicked not dragged from svg
		var xycoords = d3.mouse(thisGraph.svgG.node()),		    
		    d = { title:  thisGraph.idct.toString(), id: thisGraph.idct++, x: xycoords[0], y: xycoords[1]};
		thisGraph.nodes.push(d);
		thisGraph.updateGraph();
		// make title of text immediently editable
		var d3txt = thisGraph.changeTextOfNode(thisGraph.circles.filter(function(dval){
		    return dval.id === d.id;
		}), d),
		    txtNode = d3txt.node();
		thisGraph.selectElementContents(txtNode);
		txtNode.focus();
	    } else if (state.shiftNodeDrag){
		// dragged from node
		state.shiftNodeDrag = false;
		thisGraph.dragLine.classed("hidden", true);
	    }
	    state.graphMouseDown = false;
	};

	// keydown on main svg
	thisGraph.svgKeyDown = function() {
	    var thisGraph = this,
		state = thisGraph.state,
		consts = thisGraph.consts;
	    // make sure repeated key presses don't register for each keydown
	    if(state.lastKeyDown !== -1) return;
	    state.lastKeyDown = d3.event.keyCode;
	    var selectedNode = state.selectedNode,
		selectedEdge = state.selectedEdge;
	    switch(d3.event.keyCode) {
	    case consts.BACKSPACE_KEY:
	    case consts.DELETE_KEY:
		d3.event.preventDefault();
		if (selectedNode){
		    thisGraph.nodes.splice(thisGraph.nodes.indexOf(selectedNode), 1);
		    thisGraph.spliceLinksForNode(selectedNode);
		    state.selectedNode = null;
		    thisGraph.updateGraph();
		} else if (selectedEdge){
		    thisGraph.edges.splice(thisGraph.edges.indexOf(selectedEdge), 1);
		    state.selectedEdge = null;
		    thisGraph.updateGraph();
		}
		break;
	    }
	};
	
	thisGraph.svgKeyUp = function() {
	    this.state.lastKeyDown = -1;
	};
	// call to propagate changes to graph
	thisGraph.updateGraph = function(){
	    
	    var thisGraph = this,
		consts = thisGraph.consts,
		state = thisGraph.state;
	    
	    // update existing nodes
	    thisGraph.circles = thisGraph.circles.data(thisGraph.nodes, function(d){ return d.id;});
	    thisGraph.circles.attr("transform", function(d){
		return "translate(" + d.x + "," + d.y + ")";});
	    
	    // add new nodes
	    var newGs= thisGraph.circles.enter()
		.append("g");
	
	    newGs.classed(consts.circleGClass, true)
		.attr("transform", function(d){return "translate(" + d.x + "," + d.y + ")";})
		.on("mouseover", function(d){
		    if (state.shiftNodeDrag){
			d3.select(this).classed(consts.connectClass, true);
		    }
		})
		.on("mouseout", function(d){
		    d3.select(this).classed(consts.connectClass, false);
		})
		.on("mousedown", function(d){
		    thisGraph.circleMouseDown.call(thisGraph, d3.select(this), d);
		})
		.on("mouseup", function(d){
		    thisGraph.circleMouseUp.call(thisGraph, d3.select(this), d);
		})
		.call(thisGraph.drag);
	    
	    newGs.append("circle")
		.attr("r", String(consts.nodeRadius));
	    
	    newGs.each(function(d){
		thisGraph.insertTitleLinebreaks(d3.select(this), d.title);
		// thisGraph.showPosition(d3.select(this));
	    });

	    thisGraph.edges = Update_edges_according_to_nodes(thisGraph.edges, thisGraph.nodes);

	    thisGraph.paths = thisGraph.paths.data(thisGraph.edges, function(d){
		return String(d.source.id) + "+" + String(d.target.id);
	    });
	    
	    thisGraph.paths
		.classed(consts.selectedClass, function(d){
		    return d === state.selectedEdge;
		})
		.attr("d", function(d){
		    return "M" + d.source.x + "," + d.source.y + "L" + d.target.x + "," + d.target.y;
		});
	    
	    var paths = thisGraph.paths.enter()
		.append("path")
		.classed("link", true)
		.attr("d", function(d){
		    return "M" + d.source.x + "," + d.source.y + "L" + d.target.x + "," + d.target.y;
		})
		.on("mousedown", function(d){
		    thisGraph.pathMouseDown.call(thisGraph, d3.select(this), d);
		}
		   )
		.on("mouseup", function(d){
		    state.mouseDownLink = null;
	    });
	    
	    // remove old links
	    thisGraph.paths.exit().remove();
	    // remove old nodes
	    thisGraph.circles.exit().remove();
	    /*
	    var text = thisGraph.svg.selectAll(".pos")
		.data(thisGraph.circles[0]);

	    text.enter().append("text")
		.attr("text-anchor","middle")
		.attr("dy", "50px")
		.attr("font-size", "15px");

	   
	    text
		.classed("pos", true)
		.attr("x", function(d){
		    return d.__data__.x;})
		.attr("y", function(d){return d.__data__.y;})
		.text(function(d){
		    var y = parseInt(thisGraph.svgheight-+d.__data__.y);
		    var x = parseInt(d.__data__.x)
		    return '('+ x +', '+y+')';});

	    
	    text.exit().remove();
	    */
	   
	};
	/*
	thisGraph.zoomed = function(){
	    this.state.justScaleTransGraph = true;
	    d3.select("." + this.consts.graphClass)
		.attr("transform", "translate(" + d3.event.translate + ") scale(" + d3.event.scale + ")");
	};
	
	thisGraph.updateWindow = function(svg){
	    var docEl = document.documentElement,
		bodyEl = document.getElementsByTagName('body')[0];
	    var x = window.innerWidth || docEl.clientWidth || bodyEl.clientWidth;
	    var y = window.innerHeight|| docEl.clientHeight|| bodyEl.clientHeight;
	    svg.attr("width", x).attr("height", y);
	};
	*/
	
	function Update_edges_according_to_nodes(Edges, Nodes){
	    for(var i = 0; i < Edges.length; i++){
		var del_id = -1;
		var node = Nodes.filter(obj => obj.id === Edges[i].source.id)
		if(node.length>0){
		    Edges[i].source.x = node[0].x;
		    Edges[i].source.y = node[0].y;
		}
		else{
		    del_id = Edges[i].source.id;
		}
		node = Nodes.filter(obj => obj.id === Edges[i].target.id)
		if(node.length>0){
		    Edges[i].target.x = node[0].x;
		    Edges[i].target.y = node[0].y;
		}
		else{
		    del_id =  Edges[i].target.id;
		}
		if (del_id>0){
		    var toSplice = Edges.filter(obj => obj.source.id===del_id || obj.target.id===del_id)
		    toSplice.map(function(l) {
			Edges.splice(Edges.indexOf(l), 1);
	    });
		}
	    }
	    return Edges
	    
	};
	
    };

   

    
    /**** MAIN ****/

    // warn the user when leaving
    window.onbeforeunload = function(){
	return "Make sure to save your graph locally before leaving :-)";
    };
    
    var docEl = document.documentElement,
	bodyEl = document.getElementsByTagName('body')[0];
    
    var width = window.innerWidth || docEl.clientWidth || bodyEl.clientWidth,
	height =  window.innerHeight|| docEl.clientHeight|| bodyEl.clientHeight;
    var svg_width = width/3;
    var svg_height = height;

    var xLoc = width/2 - 25,
	yLoc = 100;
    var tid = 0;
    var tids = [];

    var AM = 'LA';
  
  
    var cm_set = 1;
    var DS = "SUV1",
	MTS = "MT2"
    var selected_node = "AMT";
    var selected_edge = -1;
    var circle, paths, dt, colorScale;
    var nTrees = [];
    var hidden_flag_cm = 0,
	hidden_flag_scv = 0;
    d3.selectAll(".CV").on("click", function(){
	d3.selectAll(".CV").classed("selected-icon", false);
	d3.select(this).classed("selected-icon", true);
	switch(this.title){
	case "label":
	    DS = "LS"
	    hide_colormap();
	    break;
	case "circular glyph":
	    d3.select("#CV1").classed("selected-icon", true);
	    d3.select("#CV21").classed("selected-icon", true);
	    DS = "UV";
	    break;
	case "line glyph":
	    DS = "UV2";
	    d3.select("#CV2").classed("selected-icon", true);
	    d3.select("#CV22").classed("selected-icon", true);
	    break;
	case "statistic circular glyph":
	    DS = "SUV1";
	    break;
	case "statistic line glyph":
	    DS = "SUV2";
	    break;
	case "statistic ribbon glyph":
	    DS = "SUV3";
	    break;
	default:
	    DS = "UV3";
	    d3.select("#CV3").classed("selected-icon", true);
	    d3.select("#CV23").classed("selected-icon", true);
	    break;
	}
	if (DS!="LS"){
	    show_colormap();
	}
	
	if (nTrees.status=="success"){
	    DRAW_TREE(nTrees, DS, svg3, selected_node, circle, paths, colorScale, MTS);
	}
    });

    d3.selectAll(".LGA").on("click", function(){
	d3.selectAll(".LGA").classed("selected-icon", false);
	d3.select(this).classed("selected-icon", true);
	if(this.title=="linear animation"){
	    AM = 'LA';
	}else{
	    AM = 'GA';
	}
	if (nTrees.status=="success"&&selected_edge!=-1){
	    var dt = [ circle, paths];
	    ANIMATION(nTrees, svg4, selected_edge, dt, colorScale);
	}
    });

    var AM_c = "CV";
    d3.selectAll(".LCA").on("click", function(){
	d3.selectAll(".LCA").classed("selected-icon", false);
	d3.select(this).classed("selected-icon", true);
	if(this.title=="colored by label"){
	    AM_c = "LS";
	}else{
	    AM_c = "CV";
	}
	if (nTrees.status=="success"&&selected_edge!=-1){
	    var dt = [ circle, paths];
	    ANIMATION(nTrees, svg4, selected_edge, dt, colorScale);
	}
    });
    
    
    var CM_id="set1";
    var CM_g=0;
    d3.selectAll(".CMg").on("click", function(){
	d3.selectAll(".CMg").classed("selected-icon", false);
	d3.select(this).classed("selected-icon", true);
	CM_g = this.title-1;
	CM_id ="set"+this.title;
	if (nTrees.status=="success"){
	    DRAW_TREE(nTrees, DS, svg3, selected_node, circle, paths, colorScale, MTS);
	}
    });
  
   
    function append_title(tid, svg){
	var treeid = "Tree -";
	var circle = svg.selectAll(".display-circle")
	    .data(treeid);
	circle.enter().append("circle")
	    .attr("r", 20)
	    .attr("cx",  width/13.2-12)
	    .attr("cy", 12)
	    .attr("fill", "#2b303c")
	    .attr("class", "display-circle");

	var text = svg.selectAll(".display-text")
	    .data(treeid);
	text.enter().append("text")
	    .attr("text-anchor","middle")
	    .attr("x", width/13.2-15)
	    .attr("y", 20)
	    .attr("font-size", "20px")
	    .attr("fill", "white")
	    .text(tid)
	    .attr("class", "display-text");
    }
    
    
    function add_titles_for_animation(svg, title){
    svg.append("circle")
    	.attr("r", 28)
    	.attr("cx", svg_animation_width-12)
    	.attr("cy", 12)
    	.attr("fill", "#2b303c")
    	.attr("class", "annotations");
    
    svg.append("text")
	.attr("dy", 22)
	.text(title)
	.style('fill', 'white')
	.attr("class", "annotations-text")
	.attr("text-anchor", "middle")
	.attr("font-size", "22px")
	.attr("dx", svg_animation_width-18);
    }
    
    function insert_annotation_animation(svg, id){
	svg.append("text")
	.text(id)
	.attr("dy", 25)
	.style('fill', 'white')
	.attr("text-anchor", "middle")
	.attr("font-size", "25px")
	.attr("dx", svg_animation_width-18);
    }


    function add_tree(nodes, edges, Trees, tid, tids){
	var nn=[];
	var ee=[];
	nn = JSON.parse(JSON.stringify(nodes));
	ee = JSON.parse(JSON.stringify(edges));
	Trees["Nodes-"+tid] = nn;
	Trees["Edges-"+tid] = ee;

	var div = document.createElement('div');
	div.className = "toolbox-tree";
	div.style.left = (tids.length-1)*(width/13.2+10)+'px';
	
	var input = document.createElement('input');
	input.type = "image";
	input.id  = 'delete-'+tids.length
	input.className = "delete-tree";
	input.title = "Delete tree";
	input.src = 'static/fig/trash-icon.png';
	input.alt = 'Delete tree';

	var input2 = document.createElement('input');
	input2.type = "image";
	input2.id  = 'edit-'+tids.length
	input2.className = "edit-tree";
	input2.title = "Edit tree";
	input2.src = 'static/fig/edit-icon.png';
	input2.alt = 'Edit tree';

	var input3 = document.createElement('input');
	input3.type = "image";
	input3.id  = 'refresh-'+tids.length
	input3.className = "refresh-tree";
	input3.title = "Refresh tree";
	input3.src = 'static/fig/refresh-icon.png';
	input3.alt = 'Refresh tree';

	document.getElementById('Trees').appendChild(div).appendChild(input2);
	document.getElementById('Trees').appendChild(div).appendChild(input3);
	document.getElementById('Trees').appendChild(div).appendChild(input);
	
	var svg = d3.select("#Trees").append("svg")
	    .attr("width", width/13.2)
	    .attr("height", height/6)
	    .attr("class", "trees")
	    .attr("id", "trees-"+tid);
	
	var circle, paths;
	var dt = draw_tree(edges, nodes, svg, circle, paths, 4, 'display');
	append_title(tid, svg);

	var treesss = d3.select("#Trees").selectAll(".trees")
	treesss.on("click", function(){
	    var selected_id = this.id.split('-')[1];
	    display_tree_no_change(selected_id);
	    treesss.classed("selected-tree", false);
	    d3.select(this).attr("class", "trees selected-tree");
	});
    }

    function delete_tree(sid, tids, Trees){
	var tid = tids[sid-1]
	d3.select("#trees-" + tid).remove();
	d3.select("#delete-"+tids.length).remove();
	d3.select("#edit-"+tids.length).remove();
	d3.select("#refresh-"+tids.length).remove();
	tids = tids.filter(item => item !== tids[sid-1]);
	delete Trees["Nodes-"+tid];
	delete Trees["Edges-"+tid];
	
	return [tids, Trees];
	
    }

    

    function remove_graph(svg, mode=null){
	svg.selectAll("path").remove();
	svg.selectAll(".nodes").remove();
	if (mode!='display'){
	    svg.selectAll("circle").filter(function() {
		return !this.classList.contains('annotations')
	    })
		.remove();	
	    svg.selectAll("text").filter(function() {
		return !(this.classList.contains('annotations-text')||this.classList.contains('annotations-content')||this.classList.contains('colormap')||this.classList.contains('Not_Remove'))
	    }).remove();
	}

    }

    d3.selection.prototype.moveToFront = function() {  
	return this.each(function(){
	    this.parentNode.appendChild(this);
	});
    };
    
    d3.selection.prototype.moveToBack = function() {  
        return this.each(function() { 
	    var firstChild = this.parentNode.firstChild; 
	    if (firstChild) { 
                this.parentNode.insertBefore(this, firstChild); 
	    } 
        });
    };
    
    
    // initial node data
    var nodes = [];
    var edges = [];
 
    /** MAIN SVG **/
    var control_panel_width = width/3.1/12*7-10;
    var svg4_width = width/3.1/12*7.8
    var control_svg_height = height/4.5;
    var svg4_height = height/1.5-control_svg_height-47;
  	var a_s = 1.7,
	    at_s = height/1.5/(svg4_height-40)*2;

    
    var svg = d3.select(settings.appendElSpec1).append("svg")
        .attr("width", width/3.1)
	.attr("height", height/1.5)
	.style('background-color', 'white');
   
    var svg2 = d3.select(settings.appendElSpec2).append("svg")
        .attr("width", control_panel_width)
	.attr("height", control_svg_height)
	.style('background-color', 'white')
	.attr("id", "layout")
        .attr("preserveAspectRatio", "xMidYMid")
        .attr("viewBox", "0 0 " + control_panel_width + " " + control_svg_height);

    var svg_animation_width = width/3/12*4;
    var control_svg_width =  width/3/12*5;
    var svg_control = d3.select("#control-panel").append("svg")
	.attr("width", control_svg_width)
	.attr("height", control_svg_height)
	.style("background-color", "white")
	.attr("id", "svg-control");

    var left_s = 100,
	width_s = svg_animation_width-82-15,
	gap = control_svg_height/10,
	top_s = control_svg_height/3.8,
	top_t = top_s+gap*5;
	

    var ED_param = 0.5,
	min_ED = 0.1,
	max_ED = 0.9;
    
    
    var slider1 = new simpleSlider();
    slider1.width(width_s).x(left_s).y(top_s).value(0.5).event(function(){
        ED_param = (slider1.value()*(max_ED-min_ED)+min_ED).toFixed(2);
	update_params('#ED-param', ED_param);
    });
    svg_control.call(slider1);

    svg_control.append("text")
	.text(min_ED)
    	.attr("text-anchor", "end")
	.attr('dx', left_s-10)
	.attr('dy', top_s+4);

    svg_control.append("text")
	.text(max_ED)
    	.attr("text-anchor", "start")
	.attr('dx', left_s+width_s+10)
	.attr('dy', top_s+4);

        
    var sigma = 0.15,
	min_sigma = 0.05,
	max_sigma = 0.25;

    var slider2 = new simpleSlider();
    slider2.width(width_s).x(left_s).y(top_s+gap).value(0.5).event(function(){
        sigma = (slider2.value()*(max_sigma-min_sigma)+min_sigma).toFixed(2);
	update_params('#sigma', sigma);
    });
    svg_control.call(slider2)
    svg_control.append("text")
	.text(min_sigma)
    	.attr("text-anchor", "end")
	.attr('dx', left_s-10)
	.attr('dy', top_s+gap+4);

    svg_control.append("text")
	.text(max_sigma)
    	.attr("text-anchor", "start")
	.attr('dx', left_s+width_s+10)
	.attr('dy', top_s+gap+4);

    var GA_param = 20,
	min_GA = 2,
	max_GA = 50;

    var slider3 = new simpleSlider();
    slider3.width(width_s).x(left_s).y(top_s+2*gap).value(0.4).event(function(){
        GA_param = parseInt(slider3.value()*(max_GA-min_GA)+min_GA);
	update_params('#GA-param', GA_param);
    });
    svg_control.call(slider3);
    svg_control.append("text")
	.text(min_GA)
    	.attr("text-anchor", "end")
	.attr('dx', left_s-10)
	.attr('dy', top_s+gap*2+4);
    
    svg_control.append("text")
	.text(max_GA)
    	.attr("text-anchor", "start")
	.attr('dx', left_s+width_s+10)
	.attr('dy', top_s+gap*2+4);

    var params = svg_control.selectAll(".params")
	.data([ "\u03BB = ", "\u03B4 = ", "#steps = "])

    params.enter().append("text")
	.text(function(d){return d;})
	.attr("class", "params")
	.attr('dy', function(d, i){
	    return top_t+gap*i-12;
	})
	.attr("text-anchor", "end")
	.attr('dx',  svg_animation_width/3);

    var params0 = svg_control.selectAll(".params0")
	.data([ "\u03BB: ", "\u03B4: ", "#steps: "])
    params0.enter().append("text")
	.text(function(d){return d;})
	.attr("class", "params0")
	.attr('dy', function(d, i){
	    return top_s+gap*i+4;
	})
	.attr("text-anchor", "end")
	.attr('dx', left_s-45);
    
    var ids = ["ED-param", "sigma", "GA-param"]
    params = svg_control.selectAll(".params_value")
	.data([ ED_param, sigma, GA_param])

    params.enter().append("text")
	.text(function(d){return d;})
	.attr("class", "params_value")
	.attr('dy', function(d, i){
	    return top_t+gap*i-12;
	})
	.attr("text-anchor", "middle")
	.attr('dx',  svg_animation_width/3+20)
	.attr("id", function(d, i){return ids[i];});
    
    
     d3.select("#svg-control").append("rect")
	.attr("x", 0)
	.attr("y", top_s+3*gap+5)
	.attr("width", control_svg_width)
	.attr("height", 2)
	.attr("fill", "#333");

    d3.select("#svg-control").append("rect")
	.attr("x", svg_animation_width/2+10)
	.attr("y", top_s+3*gap+10)
	.attr("width", 2)
	.attr("height", control_svg_height-top_s-3*gap-12)
	.attr("fill", "#cbcbcb");
    
    var svg4 = d3.select(settings.appendElSpec4).append("svg")
        .attr("width", svg4_width)
	.attr("height", svg4_height)
	.style('background-color', 'white');

    
    
    var svg3 = d3.select(settings.appendElSpec3).append("svg")
        .attr("width", width/3.1)
	.attr("height", height/1.5)
	.style('background-color', 'white');


    function insert_colormap_txt(){
	svg3.append("rect")
	    .attr("x", 0)
	    .attr("y", height/1.6-35)
	    .attr("width", 125)
	    .attr("height", 28)
	    .attr("fill", "#333")
	    .attr("class", "colormap");

	svg3.append("text")
	    .text("color map")
	    .attr("dy", height/1.6-15)
	    .attr("dx", 20)
	    .attr("fill", "white")
	    .attr("class", "colormap");
    }

    

    

    
    insert_colormap_txt()
    var scales_UV = {
	'Nodes': ["#3288bd", "#66c2a5", "#abdda4", "#e6f598", "#fee08b", "#fdae61", "#f46d43", "#d53e4f"],
	'Edges': [ "#252525", "#525252", "#737373", "#969696", "#bdbdbd", "#d9d9d9" ],
	'setg':["#377eb8", "#e41a1c","#4daf4a","#984ea3","#ff7f00","#cbcbcb","#a65628","#f781bf"],
	'set1':["#7fc97f", "#beaed4", "#fdc086", "#ffff99", "#386cb0"],
	'set2':[ "#d7191c","#fdae61","#ffffbf","#abdda4","#2b83ba"],
	'set3':[ "#fbb4ae","#b3cde3","#ccebc5","#decbe4","#fed9a6"],
	'set4':["#a6cee3","#1f78b4","#b2df8a","#33a02c","#fb9a99"],
	'set5':["#8dd3c7","#ffffb3","#bebada","#fb8072","#80b1d3"],
	'set6':["#66c2a5","#fc8d62","#8da0cb","#e78ac3","#a6d854"],
	'set7':["#f1eef6","#bdc9e1","#74a9cf","#2b8cbe","#045a8d"],
	'set8':[ "#ffffd4","#fed98e","#fe9929","#d95f0e","#993404"]};

   

    insert_annotation(svg, ['#F6FBFF', '#9ba3b7', '#9ba3b7'], ['#2b303c', 'white', '#2b303c'],['editable', "uneditable", "selected"], 4);
    insert_annotation(svg3, ['#8e0c01', '#006400', '#2b303c'], ['white', 'white', '#2b303c'], ['original labeled leaf', 'newly labeled leaf', "internal vertex"], 50);


    var svg_source = d3.select("#Animation-Trees").append("svg")
	.attr("width", svg_animation_width )
	.attr("height", svg4_height/2-2)
	.style("background-color", "white")
	.attr("id", "trees-source");

    d3.select("#svg-control").append("rect")
	.attr("x", 0)
	.attr("y", 0)
	.attr("width", control_svg_width)
	.attr("height", 40)
	.attr("fill", "#333");

    
    d3.select("#svg-control").append("text")
	.text("Parameter Setting")
	.style('fill', "white")
	.attr("text-anchor", "middle")
    	.attr("class", "param-text")
	.attr("dy", 25)
	.attr("dx", control_svg_width/2);
    
    

    var svg_target = d3.select("#Animation-Trees").append("svg")
	.attr("width", svg_animation_width)
	.attr("height",svg4_height/2-2)
	.style("background-color", "white")
	.attr("id", "trees-target");

    
    add_titles_for_animation(d3.select("#trees-source"), "AMT")
	add_titles_for_animation(d3.select("#trees-target"), "")
    
    
    var graph = new GraphCreator(svg, nodes, edges, settings.appendElSpec1, height);
    graph.setIdCt(1);
    graph.updateGraph();
    
    var Trees = {};
    var layoutdata = {
	nodes:[
	    {name: "AMT"}
	],
	edges:[]
    };

    var w = control_panel_width,
        h = control_svg_height,
        aspect = w / h;
	
    var force = d3.layout
        .force()
        .nodes(layoutdata.nodes)
        .links(layoutdata.edges)
        .size([w, h])
        .gravity(.05)
        .distance(70)
        .charge(-400)
        .start();


    var edge = svg2.selectAll(".edge")
    var node = svg2.selectAll(".node")

    force.on("tick", function() {
        edge.attr("x1", function(d) { return d.source.x; })
	    .attr("y1", function(d) { return d.source.y; })
	    .attr("x2", function(d) { return d.target.x; })
	    .attr("y2", function(d) { return d.target.y; });
	
        node.attr("transform", function(d) {
    	    return "translate(" + d.x + "," + d.y + ")";
    	});
    });
    d3.select("g#tree-AMT")
	.on("mousedown.drag", null)
	
	// Scale on window resize
	
    update_layout();

    function update_layout(IL_dists=null, colorScale=null){
	var global_dist = JSON.parse(JSON.stringify(IL_dists))
	var pivot = 0;
	if (IL_dists != null){
	    pivot =  Math.max(...IL_dists)+0.00001;
	}
	var max_l = 80,
	    min_l = 10;
	
	if(global_dist != null){
	    force.distance(function(d, i){
		return IL_dists[i+1]/pivot*(max_l-min_l)+min_l;
	    })
	} else{
	    force.distance(70);
	}

	
	edge=edge.data(layoutdata.edges);
	edge.enter()
	    .insert("line")
	    .attr("class", "edge")
	    .style('stroke', function(d, i){
		if  (global_dist == null){
		    return "#2b303c";
		} else {
		    return colorScale(IL_dists[i+1]);
		}

	    })
	    .attr("id", function(d){
		return "edge-"+JSON.parse(JSON.stringify(d.target.name))});

	if (global_dist != null){
	    edge.style('stroke', function(d, i){
		return colorScale(IL_dists[i+1]);
	    })

	}
	
	node = node
	    .data(layoutdata.nodes);
    
	node.enter()
	    .append("g")
	    .attr("class", "node")
	    .attr("id", function(d) {
		if (d.name == "AMT") {
		    return "tree-AMT";
		}
		else{
		    return "tree-"+JSON.parse(JSON.stringify(d.name));
		}
	    })
	    .call(force.drag);
	
	node.append("circle")
            .attr("r", 13)
            .append("title")
            .text(function(d) {
		if (d.name == "AMT") {
		    return "Average Merge Tree";
		} else{
		    return "Tree "+JSON.parse(JSON.stringify(d.name));
		}
            });

	node.append("text")
            .attr("dx", 0)
            .attr("dy", 5.5)
            .text(function(d) {
		return d.name;
	    })
	    .attr("text-anchor","middle");

	node.each(function(d){
	    d3.select(this).moveToFront();
	});


	node.exit().remove()
	edge.exit().remove()

	if (global_dist !=null){
	    insert_legend(svg2, IL_dists, Math.max(...IL_dists), scales_UV["Edges"]);
	}
    

	force.start()
	global_dist=null;
    }

    function update_params(id, context){
	d3.select(id).text(context);
    }


    function insert_legend(svg, l, maxn, scale){
	// clear current legend
        svg.selectAll('.legend').remove();
	
	var legendFullHeight = 200;
	var legendFullWidth = 50;
	
	var legendMargin = { top: 20, bottom: 20, left: 20, right: 20 };

	// use same margins as main plot
	var legendWidth = legendFullWidth - legendMargin.left - legendMargin.right;
	var legendHeight = legendFullHeight - legendMargin.top - legendMargin.bottom;

	
	var legendSvg = svg.append('g')
	    .attr('class', 'legend')
            .attr('transform', 'translate(' + legendMargin.left + ',' +
		  legendMargin.top + ')');

        // append gradient bar
        var gradient = legendSvg.append('defs')
	    .attr("class", "legend")
            .append('linearGradient')
            .attr('id', 'gradient'+maxn)
            .attr('x1', '0%') // bottom
            .attr('y1', '100%')
            .attr('x2', '0%') // to top
            .attr('y2', '0%')
            .attr('spreadMethod', 'pad');
	
	var pct = linspace(0, 100, scale.length).map(function(d) {
            return Math.round(d) + '%';
        });

	var colourPct = d3.zip(pct, scale);
        colourPct.forEach(function(d) {
            gradient.append('stop')
                .attr('offset', d[0])
                .attr('stop-color', d[1])
                .attr('stop-opacity', 1);
        });

	legendSvg.append('rect')
	    .attr("class", "legend")
            .attr('x1', 0)
            .attr('y1', 0)
            .attr('width', legendWidth)
            .attr('height', legendHeight)
            .style('fill', 'url(#gradient'+maxn+')');

        // create a scale and axis for the legend

	
        var legendScale = d3.scale.linear()
            .domain([0, maxn])
            .range([legendHeight, 0]);

        var legendAxis = d3.svg.axis()
            .scale(legendScale)
            .orient("right")
	    .ticks(5)
	    .tickSize(0);

        legendSvg.append("g")
	    .attr("class", "axis x")
            .attr("transform", "translate(" + legendWidth + ", 0)")
            .call(legendAxis);


    }

    

    
    
    d3.select("#confirm-input").on("click", function(){
	if(nodes.length>0){
	    if(tids.length<12){
		var treesss = d3.select("#Trees").selectAll(".trees")
		treesss.classed("selected-tree", false)
		tid = tid+1;
		tids.push(JSON.parse(JSON.stringify(tid)));
		add_tree(nodes, edges, Trees, tid, tids);
		var anode = {name: JSON.parse(JSON.stringify(tid)), x: w/2, y:h/2}
		layoutdata.nodes.push(anode);
		layoutdata.edges.push({source: 0, target: anode});
		update_layout();
		d3.select("#Trees").selectAll(".delete-tree").on("click", function(){
		    var del_id = Math.round(parseFloat(this.parentNode.style.left)/(width/13.2+10)+1);
		    layoutdata.nodes.splice(del_id,1);
		    layoutdata.edges.splice(del_id-1, 1);
		    d3.event.stopPropagation();
		    update_layout();
		    var del_elems = delete_tree(del_id, tids, Trees);
		    tids = del_elems[0];
		    Trees = del_elems[1];
		    
		});
		d3.select("#Trees").selectAll(".edit-tree").on("click", function(){
		    var del_id = Math.round(parseFloat(this.parentNode.style.left)/(width/13.2+10)+1);
		    var stid = tids[del_id-1];
		    var treesss = d3.select("#Trees").selectAll(".trees")
		    display_tree(stid);
		    treesss.classed("selected-tree", false);
		    d3.select("#trees-"+stid).attr("class", "trees selected-tree");		
		});
		
		d3.select("#Trees").selectAll(".refresh-tree").on("click", function(){
		    var del_id = Math.round(parseFloat(this.parentNode.style.left)/(width/13.2+10)+1);
		    var stid = tids[del_id-1];
		    var svg = d3.select("#trees-"+stid);
		    var circle, paths;
		    draw_tree(Trees["Edges-"+stid], Trees["Nodes-"+stid], svg, circle, paths, 4, 'display');
		});
	    }else{
		alert('Sorry! The number of trees cannot larger than 12. You can delete some of existed tree before add a new one!');
	    }
	    
	    
	}
	else{
	    alert('Please draw a tree before confirmation!');
	}
	
    });


    d3.select("#add-input").on("click", function(){
	var treesss = d3.select("#Trees").selectAll(".trees")
	treesss.classed("selected-tree", false)
	remove_graph(svg);
	nodes = [];
	edges = [];
	graph = new GraphCreator(svg, nodes, edges, settings.appendElSpec1, height);
	graph.setIdCt(1);
	graph.updateGraph()
    });

    d3.select("#help")
	.on("click", function(){
	    alert('shift-click on graph to create a node\nshift-click on a node and then drag to another node to connect them with a edge\nshift-click on a node to change its title\nclick on node or edge and press backspace/delete to delete');
	});

    d3.select("#help-control")
	.on("click", function(){
	    alert('Click "start calculate" first when you finished adding trees.\nClick a node to show corresponding tree.\nClick edge to show the animation of deformation between selected tree and average tree.');
	});

    function delete_annotation(svg){
	svg.selectAll(".annotations").remove();
	svg.selectAll(".annotations-text").remove();
	svg.selectAll(".annotations-content").remove();
    }

    function insert_annotation(svg, circle_color , text_color, text_content, gap, mode=null){
	delete_annotation(svg);

	if(mode=="sGraduated_Lines"||mode=="svarying_line"){
	     var circle = svg.selectAll(".annotations")
		.data(circle_color);

	    var circleEnter = circle.enter().append("rect")
		.attr('class', 'annotations')
		.attr('width', 20)
		.attr('height', 10)
		.attr("transform", function(d, i){
		    return "translate(" + (width/gap-8) + "," + (30*(i+1)-5) + ")";
		})
		.style('fill', function(d){ return d;})
		.style('stroke', "#333")
		.style("stroke-width", function(d){
		    if (mode=="sGraduated_Lines"){
			return 0;
		    }else{return 0;}
		});

	}else{
	    var circle = svg.selectAll(".annotations")
		.data(circle_color);

	    var circleEnter = circle.enter().append("circle")
		.attr('class', 'annotations')
		.attr('r', 10)
		.attr("transform", function(d, i){
		    return "translate(" + width/gap + "," + 30*(i+1) + ")";
		})
		.style('fill', function(d){ return d;})
		.style('stroke', "#333")
		.style("stroke-width", "1px");
	}
	
	var text = svg.selectAll(".annotations-text")
	    .data(text_color);
	if (mode==null){
	    var textEnter = text.enter().append('text')
		.attr('class', 'annotations-text')
		.attr("text-anchor","middle")
		.attr("dy", "4px")
		.attr("font-size", "10px")
		.attr('fill', function(d){ return d;})
		.attr("x",  width/gap)
		.attr("y", function(d, i){return 30*(i+1);})
		.text('N');
	}
	text = svg.selectAll(".annotations-content")
	    .data(text_content);

	textEnter = text.enter().append('text')
	    .attr('class', 'annotations-content')
	    .attr("text-anchor","left")
	    .attr("dy", "4px")
	    .attr("font-size", "15px")
	    .attr('fill', "#333")
	    .attr("x",  width/gap+20)
	    .attr("y", function(d, i){return 30*(i+1);})
	    .text(function(d){ return d;});
	
    };
    

    function display_tree(sid){
	remove_graph(svg);
	var edge_name = "Edges-"+sid;
	var node_name = "Nodes-"+sid;
	edges = Trees[edge_name];
	nodes = Trees[node_name];
	graph = new GraphCreator(svg, nodes, edges, settings.appendElSpec1, height);
	graph.state.justDragged = true;
	graph.setIdCt(nodes.length+1);
	graph.updateGraph()

    };

    function display_tree_no_change(sid){
	d3.select("svg").remove()
	svg = d3.select(settings.appendElSpec1).append("svg")
            .attr("width", width/3.3)
	    .attr("height", height/1.5)
	    .style('background-color', 'white');

	insert_annotation(svg, ['#F6FBFF', '#9ba3b7', '#9ba3b7'], ['#2b303c', 'white', '#2b303c'],['Editable', "NOT Editable", "Selected"], 4.5);
	
	var edge_name = "Edges-"+sid;
	var node_name = "Nodes-"+sid;
	edges = Trees[edge_name];
	nodes = Trees[node_name];
	var circle, paths;
	
	draw_tree(edges, nodes, svg, circle, paths, 1, 'fixed');
    }

  
    d3.select("#start").on("click", function(){
	remove_graph(svg3);
	var treesss = d3.select("#Trees").selectAll(".trees")
	treesss.classed("selected-tree", false)

	for(var i = 0; i < tids.length; i++){
	    var svg = d3.select("#trees-"+tids[i]);
	    var circle, paths;
	    draw_tree(Trees["Edges-"+tids[i]], Trees["Nodes-"+tids[i]], svg, circle, paths, 4, 'display');
	}

	if (tids.length==0){
	    alert("Please draw and confirm trees first!")
	}
	else{
	    sent2python(Trees, svg_width, svg_height, svg3, ED_param, GA_param, function(data){
		nTrees = data;
	    });	    
	}
    });

    function hide_colormap(){
	if (hidden_flag_cm==0){
	    d3.selectAll(".colormap").remove();
	    d3.select('input[id="cmg1"]').node().type="hidden";
	    d3.select('input[id="cmg2"]').node().type="hidden";
	    d3.select('input[id="cmg3"]').node().type="hidden";
	    d3.select('input[id="cmg4"]').node().type="hidden";
	    d3.select('input[id="cmg5"]').node().type="hidden";
	    d3.select('input[id="cmg6"]').node().type="hidden";
	    d3.select('input[id="cmg7"]').node().type="hidden";
	    d3.select('input[id="cmg8"]').node().type="hidden";
	    hidden_flag_cm = 1;
	}
    }
    function show_colormap(){
	if (hidden_flag_cm==1){
	    var y = document.getElementById("cmg1");
	    y.type= "image";
	    y = document.getElementById("cmg2");
	    y.type= "image";
	    y = document.getElementById("cmg3");
	    y.type= "image";
	    y = document.getElementById("cmg4");
	    y.type= "image";
	    y = document.getElementById("cmg5");
	    y.type= "image";
	    y = document.getElementById("cmg6");
	    y.type= "image";
	    y = document.getElementById("cmg7");
	    y.type= "image";
	    y = document.getElementById("cmg8");
	    y.type= "image";
	    insert_colormap_txt();
	    hidden_flag_cm = 0;
	}
	
    }

    function hide_statistic_btn(){
	if (hidden_flag_scv==0){
	    d3.select('input[id="SSCV1"]').node().type="hidden";
	    d3.select('input[id="SSCV2"]').node().type="hidden";
	    d3.select('input[id="SSCV3"]').node().type="hidden";
	    d3.select('input[id="CV1"]').node().type="hidden";
	    d3.select('input[id="CV2"]').node().type="hidden";
	    d3.select('input[id="CV3"]').node().type="hidden";
	    var y = document.getElementById("CV21");
	    y.type= "image";
	    y = document.getElementById("CV22");
	    y.type= "image";
	    y = document.getElementById("CV23");
	    y.type= "image";
	    hidden_flag_scv = 1;
	}
    }

    function show_statistic_btn(){
	if (hidden_flag_scv==1){
	    var y = document.getElementById("SSCV1");
	    y.type= "image";
	    y = document.getElementById("SSCV2");
	    y.type= "image";
	    y = document.getElementById("SSCV3");
	    y.type= "image";
	    y = document.getElementById("CV1");
	    y.type= "image";
	    y = document.getElementById("CV2");
	    y.type= "image";
	    y = document.getElementById("CV3");
	    y.type= "image";

	    d3.select('input[id="CV21"]').node().type="hidden";
	    d3.select('input[id="CV22"]').node().type="hidden";
	    d3.select('input[id="CV23"]').node().type="hidden";
	    hidden_flag_scv=0;
	}
	
    }
    
    
    function sent2python (Trees, svg_width, svg_height, svg, ED_param, GA_param, callback){
	var params = Trees;
	params["width"] = svg_width;
	params["height"] = svg_height;
	params["tids"] = tids;
	params["sigma"] = sigma;
	var labelling_mode = d3.select('input[name="labelling-mode"]:checked').node().value;
	
	params["label-mode"] = labelling_mode;
	params["mapping-mode"] = d3.select('input[name="mapping-mode"]:checked').node().value;
	params["ED_param"] = ED_param;
	params["GA_param"] = GA_param;
	$.ajax(
	    {
		type: "POST",
		url: "/api/say_name",
		contentType: 'application/json; charset=utf-8',
		data: JSON.stringify(params),
		dataType: "json",
		success: function (response)
		{
		    if(response['status']=='failure'){
			switch(response['error-type']){
			case 'wrong labelling mode':
			    alert("Illegal input for 'Enforce Labels' mode. You can change input trees or select 'Ingore Lables' mode!");
			    break;
			case "not tree":
			    alert("At least one tree in your input is not a tree!\nA legel tree should have following properties.\n 1) There is no cycle.\n 2) The graph is connected.");
			    break;
			case "not merge tree":
			    alert("At least one tree in your input is not a merge tree!\nA legel tree should have following properties.\n 1) It is a tree.\n 2) The height of any node in tree should be larger than the heights of its children!");
			    break;
			case "not unique":
			    alert("Labels of leaves in one tree should be different from each other under 'Enforce Labels' mode. You can change input trees or select 'Ingore Lables' mode!");				
			    break;
			default:
			    alert("Unknown error!");
			    
			}
			
		    }
		    else{
			selected_node = "AMT";
			var IL_dists = [0];
			for(var i = 0; i<tids.length; i++){
			    IL_dists.push(response["IL-dist-"+tids[i]]);
			}
			colorScale = d3.scale.linear()
			    .domain(linspace(0, Math.max(...IL_dists), scales_UV["Edges"].length))
			    .range(scales_UV["Edges"]);
			update_layout(IL_dists, colorScale)		
			dt = DRAW_TREE(response, DS, svg, selected_node, circle, paths, colorScale, MTS);
			delete_annotation(svg4)
			draw_tree(response["UEdges-AMT"], response["UNodes-AMT"], svg_source, dt[0], dt[1], at_s, 'small', colorScale(0), 10);
			draw_tree(response["UEdges-AMT"], response["UNodes-AMT"], svg4, circle, paths, a_s, 'large', colorScale(0), svg4_width/20);

			show_statistic_btn();
			if(DS!="LS"){
			    show_colormap();  
			}
			
			node.on("click", function(){
			    node.classed('select', false);
			    edge.classed('select', false);
			    d3.select(this).classed('select', true);
			    var selected_id = this.__data__.name
			    selected_node = selected_id;
			    if (selected_node=="AMT"){
				show_statistic_btn();
				if(DS!="LS"){
				    show_colormap();
				}
			    }
			    else{
				if(DS=="SUV1"||DS=="SUV2"||DS=="SUV3"){
				    DS="UV";
				    d3.selectAll(".CV").classed("selected-icon", false);
				    d3.select("#CV21").classed("selected-icon", true);
				}
				disbtn3("CV")
				hide_statistic_btn();
				if(DS!="LS"){
				    show_colormap();
				}
			
			    }
			    
			    DRAW_TREE(response, DS, svg, selected_id, dt[0], dt[1], colorScale, MTS)
			});

			
			edge.on("click", function(){
			    node.classed('select', false);
			    edge.classed('select', false);
			    d3.select(this).classed('select', true);
			    var selected_id = this.__data__.target.name;
			    selected_edge = selected_id;
			    ANIMATION(response, svg, selected_id, dt, colorScale);	     
			});

			callback(response);
		    }
		},
	    });
	
	
    }


    function linspace(start, end, n) {
        var out = [];
        var delta = (end - start) / (n - 1);
	
        var i = 0;
        while(i < (n - 1)) {
            out.push(start + (i * delta));
            i++;
        }
	
        out.push(end);
        return out;
    }

    function draw_tree(edges, nodes, svg, circle, paths, scale, mode, edge_color=null, modify_x=null){
	var ss = 1
	if(mode=="small"){
	    ss = 1.5
	}
	if (modify_x==null){
	    modify_x=0;
	}
	nodes.sort(function(a, b){
	    return b.id-a.id;
	})

	var modify_y = 0;
	if(mode=="small"){
	    modify_y = 10;
	}
	
	svg.selectAll('.legend').remove();
	var l_dists = [];
	var colorScale = []
	if (edge_color!=null){
	    for(var i=0; i<nodes.length; i++){
		l_dists.push(nodes[i]['local-dist'])
	    }
	    colorScale = d3.scale.linear()
		.domain(linspace(0, 1, scales_UV["Nodes"].length))
		.range(scales_UV["Nodes"]);
	}

	remove_graph(svg, mode);
	d3.selection.prototype.moveToFront = function() {  
	    return this.each(function(){
		this.parentNode.appendChild(this);
	    });
	};
	d3.selection.prototype.moveToBack = function() {  
            return this.each(function() { 
		var firstChild = this.parentNode.firstChild; 
		if (firstChild) { 
                    this.parentNode.insertBefore(this, firstChild); 
		} 
            });
	};

	paths = svg.selectAll("path")
	    .data(edges);
	paths.enter().append("path")
	    .style("fill", function(d){
		if (mode=='varying_line'){
		    return scales_UV["setg"][CM_g];
		} else {
		    return "none";
		}	
	    })
	    .style("stroke", function(d){
		if (mode=="Graduated_Lines"){
		    return scales_UV["setg"][CM_g];
		} else if  (mode=='varying_line'){
		    return "#333";
		} 
		else{
		    return "#333";
		}})
	    .style("stroke-width", function(d){
		if(scale!=1 && mode!= "Graduated_Lines" && mode!="varying_line"){
		    return 4/scale*ss+"px";
		} else if(mode=="Graduated_Lines"){
		    var tmp = Math.min(d.source["local-dist"], d.target["local-dist"])
		    return (30*tmp)+"px"
		} else if(mode=="varying_line"){
		    return "1px";
		}
		else{
		    return "4px";}
	    })
	    .style("cursor", "default");
	
	paths
	    .attr("d", function(d){
		if (mode=="varying_line"){
		    return Varying_Line(d);
		}else{
		    return "M" + (d.source.x/scale+modify_x) + "," + (d.source.y/scale + modify_y) + "L" + (d.target.x/scale+modify_x) + "," + (d.target.y/scale + modify_y);
		}
	    })
	    .style("opacity", 0)
	    .transition()
	    .duration(500)
	    .style("opacity",1);
	    
	function Varying_Line(d){
	    
	    var x00 = d.source.x - (d.source["local-dist"]*20),
		x01 = d.source.x + (d.source["local-dist"]*20),
		x10 = d.target.x - (d.target["local-dist"]*20),
		x11 = d.target.x + (d.target["local-dist"]*20),
		y0 = d.source.y,
		y1 = d.target.y,
		x0 = d.source.x,
		x1 = d.target.x;

	    var curvature = 0.95;
	    if (d.source["local-dist"]>d.target["local-dist"]){
		curvature = 0.05;
	    };

	    if (Math.abs(d.source["local-dist"]-d.target["local-dist"])<0.1){
		curvature = 0.5;
	    }
	    
	    var x0i = d3.interpolateNumber(x00, x10),
		x02 = x0i(curvature),
		x03 = x0i(1 - curvature),
		yi =  d3.interpolateNumber(y0, y1),
		y2 = yi(curvature),
		y3 = yi(1 - curvature),
		x1i = d3.interpolateNumber(x11, x01),
		x12 = x1i(curvature),
		x13 = x1i(1 - curvature);

	    return "M" + x0 + "," + y0
		+ "C" + x0 + "," + y0
		+ " " + x02 + "," + y2
		+ " " + x1 + "," + y1
		+ "C" + x1 + "," + y1
		+ " " + x13 + "," + y2
		+ " " + x0 + "," + y0;
	}

	
	paths.sort(function(a, b){
	    return a.id-b.id;
	})
	
	paths.each(function(d){
	    d3.select(this).moveToBack();
	});
	
	
	circle = svg.selectAll("g.nodes")
	    .data(nodes);


	
	var circleEnter = circle.enter()
	    .append("g")
	    .attr('class', 'nodes')
	
	circleEnter.append("circle")
	    .attr("r", function(d){
		if (mode=="varying_node"){
		    return String(30/scale*ss*d['local-dist']);
		} else if(mode=="Graduated_Lines"||mode=="varying_line"){
		    return 15;
		}
		else{
		    return String(30/scale*ss);
		}
		
	    })
	    .attr("class", function(d){
		if(mode=="display"){
		    return "circle-display";
		}
		else if(mode=='fixed'){
		    return "circle-fixed";
		}
		else{
		    return d.cls;}
	    })
	    .style("z-index", function(d){
		if(d.cls=="IsLeaf"){
		    return 4;
		}else{
		    return 3;
		}
	    })
	    .style("stroke-width", function(d){
		if(scale!=1){
		    return 4/scale*ss+"px";
		}
		else{
		    return "2px";}
	    })
	    .attr("transform", function(d){
		return "translate(" + (d.x/scale+modify_x) + "," + (d.y/scale +  modify_y) + ")";})
	    .style("opacity", 0)
	    .transition()
	    .duration(500)
	    .style("opacity",1);

	if (mode!="varying_node" && mode!="Graduated_Lines" && mode!="varying_line"){
	    circleEnter.append("text")
		.attr("text-anchor","middle")
		.attr("dy", function(d){
		    if(mode=="display" || mode=="small"){
			return "4px";
		    }
		    else{
			return "6px";}
		})
		.attr("font-size", function(d){
		    if(scale!=1){
			return 25/scale*1.5*ss+"px";
		    }
		    else{
			return "25px";}
		})
		.attr("fill", function(d){
		    if(mode=="display"){
			return "#2b303c";
		    }
		    else{
			return "#F6FBFF";}
		})
		.attr("x", function(d){return (d.x/scale+modify_x);})
		.attr("y", function(d){return (d.y/scale +  modify_y);})
		.text(function(d){
		    return d.title;});
	    
	}
	circleEnter.each(function(d){
	    d3.select(this).moveToFront();
	});
	/*
	svg.selectAll("g.nodes").filter(function(){
	    return this.__data__.cls=="IsLeaf";}).each(function(d){
	    d3.select(this).moveToFront();
	});*/


	circle.select('circle')
	    .attr("transform", function(d){
		return "translate(" + (d.x/scale+modify_x) + "," + (d.y/scale + modify_y) + ")";})
	    .style("opacity", 0)
	    .transition()
	    .duration(500)
	    .style("opacity",1)
	    .style("stroke", function(d){
		if(edge_color!=null && mode!="varying_node" && mode!="Graduated_Lines"){
		    return edge_color;
		} else{
		    return "#333";
		}
	    });
	if (edge_color!=null){
	    circle.select('circle').style("fill", function(d, i){
		if (scale==1){
		    return scales_UV["setg"][CM_g];
		} else{
		    return colorScale(l_dists[i]);
		}
	    });
	}

	if (mode=="Graduated_Lines"||mode=="varying_line"){
	    circle.select('circle').style("fill", "#333");
	}

	if (mode!="varying_node" && mode!="Graduated_Lines"&& mode!="varying_line"){
	    circle.select('text')
		.attr("x", function(d){return (d.x/scale+modify_x);})
		.attr("y", function(d){return (d.y/scale+ modify_y);})
		.style("opacity", 0)
		.transition()
		.duration(500)
		.style("opacity",1)
		.style("fill", function(d){
		    if(edge_color != null || mode=="display"){
			return "black";
		    }else{
			return "white";
		    }
		});
	}
	
	paths.exit().transition().duration(1000).remove();
	circle.exit().transition().duration(1000).remove();
	
	if (edge_color !=null && mode!='small' && mode!="Graduated_Lines" && mode!="varying_line" && scale!=1){
	    insert_legend(svg, l_dists, 1, scales_UV["Nodes"]);
	}
	edge_color = null;

	return [circle, paths];
	
    }

    function draw_statistic_tree(edges, nodes, svg, circle, paths, scale, mode, edge_color=null, modify_x=null){
	nodes.sort(function(a, b){
	    return b.id-a.id;
	})

	var colorScale_s = []
	if (mode=="svarying_node"||mode=="svarying_line"||mode=="sGraduated_Lines"){
	    colorScale_s = d3.scale.ordinal()
		.range(scales_UV[CM_id]);
	    insert_annotation(svg, scales_UV[CM_id], [null, null, null, null, null], ['maximum', 'third quartile', 'median', 'first quartile', 'minimum'], 50, mode);
	}


	var Tcnt=nodes[0]['glocal-dist'].length;
	var ss = 1
	if(mode=="small"){
	    ss = 1.5
	}
	if (modify_x==null){
	    modify_x=0;
	}
	svg.selectAll('.legend').remove();
	var l_dists = [];
	var colorScale = []
	var sname = ['max','3rd-q', 'median', '1st-q','min'];
	if (edge_color!=null){
	    for(var i=0; i<nodes.length; i++){
		l_dists.push(nodes[i]['local-dist'])
	    }
	    colorScale = d3.scale.linear()
		.domain(linspace(0, 1, scales_UV["Nodes"].length))
		.range(scales_UV["Nodes"]);
	}

	remove_graph(svg, mode);
	d3.selection.prototype.moveToFront = function() {  
	    return this.each(function(){
		this.parentNode.appendChild(this);
	    });
	};
	d3.selection.prototype.moveToBack = function() {  
            return this.each(function() { 
		var firstChild = this.parentNode.firstChild; 
		if (firstChild) { 
                    this.parentNode.insertBefore(this, firstChild); 
		} 
            });
	};

	paths = svg.selectAll("path")
	    .data(edges);

	if(mode=="varying_node"|| mode=="svarying_node") {
	    paths.enter().append("path")
		.style("fill", "none")
		.style("stroke", "#333")
		.style("stroke-width", "3px");
	    
	    paths
		.attr("d", function(d){
		    return "M" + (d.source.x/scale+modify_x) + "," + d.source.y/scale + "L" + (d.target.x/scale+modify_x) + "," + d.target.y/scale;
		})
		.style("opacity", 0)
		.transition()
		.duration(500)
		.style("opacity",1);
	} else if(mode=="sGraduated_Lines"|| mode=="svarying_line"){
	    for (var tid=0; tid<5; tid++){
		paths.enter().append("path")
		    .style("fill", function(d){
			if (mode=='svarying_line'){
			    return colorScale_s(tid);
			} else {
			    return "none";
			}
		    })
		    .style("stroke", function(d){
			if (mode=='varying_line'){
			    return "#333";
			} else {
			    return colorScale_s(tid);
			}	
		    })
		    .style("stroke-width", function(d){
			if (mode=='svarying_line'){
			    return 0.5;
			} else {
			    var tmp = Math.min(d.source['sldist'][sname[tid]], d.target['sldist'][sname[tid]])
			    var idx = [d.source['sldist'][sname[tid]], d.target['sldist'][sname[tid]]].indexOf(tmp);
			    if(idx==0){
				tmp = d.source['sldist'][sname[tid]];
			    }else{
				tmp = d.target['sldist'][sname[tid]];
			    }
			    return tmp*30;
			}
		    });
		
		paths
		    .attr("d", function(d){
			if (mode=='svarying_line'){
			    return Varying_Line_s(d, tid);
			} else {
			    return "M" + (d.source.x/scale+modify_x) + "," + d.source.y/scale + "L" + (d.target.x/scale+modify_x) + "," + d.target.y/scale;
			}
		    })
		    .style("opacity", 0)
		    .transition()
		    .duration(500)
		    .style("opacity",1);
		
	    }
	}
	else{
	    for (var tid=0; tid<Tcnt; tid++){
		paths.enter().append("path")
		    .style("fill", function(d){
			if (mode=='varying_line'){
			    return scales_UV["setg"][CM_g];
			} else {
			    return "none";
			}	
		    })
		    .style("fill-opacity", 1/Tcnt)
		    .style("stroke", scales_UV["setg"][CM_g])
		    .style("stroke-width", function(d){
			if(mode=="Graduated_Lines"){
			    var tmp = Math.min(d.source['glocal-dist'][tid]["tree-"+(tid+1)], d.target['glocal-dist'][tid]["tree-"+(tid+1)])
			    var idx = [d.source['glocal-dist'][tid]["tree-"+(tid+1)], d.target['glocal-dist'][tid]["tree-"+(tid+1)]].indexOf(tmp);
			    if(idx==0){
				tmp = d.source['glocal-dist'][tid]["tree-"+(tid+1)];
			    }else{
				tmp = d.target['glocal-dist'][tid]["tree-"+(tid+1)];
			    }
			    return (40*tmp+5)+"px"
			} else{
			    return "0px";
			}
		    })
		    .style("stroke-opacity", 1/Tcnt);
		
		paths
		    .attr("d", function(d){
			if (mode=="varying_line"){
			    return Varying_Line(d, tid);
			}else{
			    return "M" + (d.source.x/scale+modify_x) + "," + d.source.y/scale + "L" + (d.target.x/scale+modify_x) + "," + d.target.y/scale;
			}
		    })
		    .style("opacity", 0)
		    .transition()
		    .duration(500)
		    .style("opacity",1);		
	    }
	}
	
	function Varying_Line(d, tid){
	    if (tid==-1){
		var x00 = d.source.x - 5,
		    x01 = d.source.x + 5,
		    x10 = d.target.x - 5,
		    x11 = d.target.x + 5;
	    } else{	
		var x00 = d.source.x - (d.source['glocal-dist'][tid]["tree-"+(tid+1)]*35),
		    x01 = d.source.x + (d.source['glocal-dist'][tid]["tree-"+(tid+1)]*35),
		    x10 = d.target.x - (d.target['glocal-dist'][tid]["tree-"+(tid+1)]*35),
		    x11 = d.target.x + (d.target['glocal-dist'][tid]["tree-"+(tid+1)]*35);
	    };
	    var y0 = d.source.y,
		y1 = d.target.y,
		x0 = d.source.x,
		x1 = d.target.x;

	    var curvature = 0.95;
	    if (d.source['glocal-dist'][tid]["tree-"+(tid+1)]>d.target['glocal-dist'][tid]["tree-"+(tid+1)]){
		curvature = 0.05;
	    };

	    if (Math.abs(d.source['glocal-dist'][tid]["tree-"+(tid+1)]-d.target['glocal-dist'][tid]["tree-"+(tid+1)])<0.1){
		curvature = 0.5;
	    }
	    
	    var x0i = d3.interpolateNumber(x00, x10),
		x02 = x0i(curvature),
		x03 = x0i(1 - curvature),
		yi =  d3.interpolateNumber(y0, y1),
		y2 = yi(curvature),
		y3 = yi(1 - curvature),
		x1i = d3.interpolateNumber(x11, x01),
		x12 = x1i(curvature),
		x13 = x1i(1 - curvature);

	    return "M" + x0 + "," + y0
		+ "C" + x0 + "," + y0
		+ " " + x02 + "," + y2
		+ " " + x1 + "," + y1
		+ "C" + x1 + "," + y1
		+ " " + x13 + "," + y2
		+ " " + x0 + "," + y0;
	}

	function Varying_Line_s(d, tid){
	    var x00 = d.source.x - (d.source['sldist'][sname[tid]]*30),
		x01 = d.source.x + (d.source['sldist'][sname[tid]]*30),
		x10 = d.target.x - (d.target['sldist'][sname[tid]]*30),
		x11 = d.target.x + (d.target['sldist'][sname[tid]]*30);
	    
	    var y0 = d.source.y,
		y1 = d.target.y,
		x0 = d.source.x,
		x1 = d.target.x;

	    var curvature = 0.95;
	    if (d.source['sldist'][sname[tid]]>d.target['sldist'][sname[tid]]){
		curvature = 0.05;
	    };

	    if (Math.abs(d.source['sldist'][sname[tid]]-d.target['sldist'][sname[tid]])<0.1){
		curvature = 0.5;
	    }
	    
	    var x0i = d3.interpolateNumber(x00, x10),
		x02 = x0i(curvature),
		x03 = x0i(1 - curvature),
		yi =  d3.interpolateNumber(y0, y1),
		y2 = yi(curvature),
		y3 = yi(1 - curvature),
		x1i = d3.interpolateNumber(x11, x01),
		x12 = x1i(curvature),
		x13 = x1i(1 - curvature);

	    return "M" + x0 + "," + y0
		+ "C" + x0 + "," + y0
		+ " " + x02 + "," + y2
		+ " " + x1 + "," + y1
		+ "C" + x1 + "," + y1
		+ " " + x13 + "," + y2
		+ " " + x0 + "," + y0;
	}

	
	paths.sort(function(a, b){
	    return a.id-b.id;
	})

	circle = svg.selectAll("g.nodes")
	    .data(nodes);
	
	var circleEnter = circle.enter()
	    .append("g")
	    .attr('class', 'nodes')

	if(mode=="varying_node"){
	     circleEnter.append("circle")
		.attr("r", 3)
		.style("fill", function(d){
		    //return colorScale(d['local-dist']);
		    return scales_UV["setg"][CM_g];
		})
		.attr("transform", function(d){
		    return "translate(" + (d.x/scale+modify_x) + "," + d.y/scale + ")";})
		.style("opacity", 0)
		.transition()
		.style("stroke-width", 0)
		.duration(500)
		.style("opacity",1);
	    
	    for (var tid=0; tid<Tcnt; tid++){
		circleEnter.append("circle")
		    .attr("r", function(d){
			return String(50/scale*ss*d['glocal-dist'][tid]["tree-"+(tid+1)]+3);
		    })
		    .style("fill", function(d){
			//return colorScale(d['local-dist']);
			return scales_UV["setg"][CM_g];
		    })
		    .style("fill-opacity", 1/Tcnt)
		    .attr("class", function(d){
			if(mode=="display"){
			    return "circle-display";
			}
			else if(mode=='fixed'){
			    return "circle-fixed";
			}
			else{
			    return d.cls;}
		    })
		    .style("z-index", function(d){
			if(d.cls=="IsLeaf"){
			    return 4;
			}else{
			    return 3;
			}
		    })
		    .style("stroke-width", 0)
		    .attr("transform", function(d){
			return "translate(" + (d.x/scale+modify_x) + "," + d.y/scale + ")";})
		    .style("opacity", 0)
		    .transition()
		    .duration(500)
		    .style("opacity",1);
	    }

	}else if(mode=="svarying_node"){
	    for (var tid=0; tid<5; tid++){
		circleEnter.append("circle")
		    .attr("r", function(d){
			return String(30*d['sldist'][sname[tid]]);
		    })
		    .style("fill", function(d){
			//return colorScale(d['local-dist']);
			return colorScale_s(tid);
		    })
		    .attr("class", function(d){
			if(mode=="display"){
			    return "circle-display";
			}
			else if(mode=='fixed'){
			    return "circle-fixed";
			}
			else{
			    return d.cls;}
		    })
		    .style("z-index", function(d){
			if(d.cls=="IsLeaf"){
			    return 4;
			}else{
			    return 3;
			}
		    })
		    .style("stroke-width", 0.5)
		    .attr("transform", function(d){
			return "translate(" + (d.x/scale+modify_x) + "," + d.y/scale + ")";})
		    .style("opacity", 0)
		    .transition()
		    .duration(500)
		    .style("opacity",1);
	    }
	
	}
	
	else{
	    circleEnter.append("circle")
		.attr("r", function(d){
		    if (mode=="varying_node"){
			return String(15/scale*ss*d['local-dist']+15);
		    } else if(mode=="Graduated_Lines"||mode=="varying_line"||mode=="sGraduated_Lines"||mode=="svarying_line"){
			return 15;
		    }
		    else{
			return String(30/scale*ss);
		    }
		    
		})
		.attr("class", function(d){
		    if(mode=="display"){
			return "circle-display";
		    }
		    else if(mode=='fixed'){
			return "circle-fixed";
		    }
		    else{
			return d.cls;}
		})
		.style("z-index", function(d){
		    if(d.cls=="IsLeaf"){
			return 4;
		    }else{
			return 3;
		    }
		})
		.style("stroke-width", function(d){
		    if(scale!=1){
			return 4/scale*ss+"px";
		    }
		    else{
			return "2px";}
		})
		.attr("transform", function(d){
		    return "translate(" + (d.x/scale+modify_x) + "," + d.y/scale + ")";})
		.style("opacity", 0)
		.transition()
		.duration(500)
		.style("opacity",1);

	    circle.select('circle').style("fill", function(d, i){
		return colorScale(l_dists[i]);
	    });  
	}
	
	circleEnter.each(function(d){
	    d3.select(this).moveToFront();
	});

	if (mode=="Graduated_Lines"||mode=="varying_line"||mode=="sGraduated_Lines"||mode=="svarying_line"){
	    circle.select('circle').style("fill", "#333").style("stroke", "#e3e4e8");
	}

	
	paths.exit().transition().duration(1000).remove();
	circle.exit().transition().duration(1000).remove();

	edge_color = null;

	return [circle, paths];
	
    }

    function DRAW_TREE(response, DS, svg, selected_id, circle, paths, colorScale, MTS){
	var dt = [circle, paths]
	if(selected_id == "AMT"){
	    if(DS=='LS'){
		insert_annotation(svg, ['#8e0c01', '#006400', '#2b303c'], ['white', 'white', '#2b303c'], ['Labelled Leaf', 'Newly Labelled Leaf', "NOT Leaf"], 50);
		dt = draw_tree(response["UEdges-AMT"], response["UNodes-AMT"], svg, dt[0], dt[1], 1, 'large');
	    }
	    else if (DS=='UV'){
		delete_annotation(svg);
		if (MTS=="MT1"){
		    dt = draw_tree(response["UEdges-AMT"], response["UNodes-AMT"], svg, dt[0], dt[1], 1, 'varying_node', colorScale(0));}
		else{
		    dt = draw_statistic_tree(response["UEdges-AMT"], response["UNodes-AMT"], svg, dt[0], dt[1], 1, 'varying_node', colorScale(0));
		}
	    } else if (DS=="UV2"){
		delete_annotation(svg);
		if (MTS=="MT1"){
		    dt = draw_tree(response["UEdges-AMT"], response["UNodes-AMT"], svg, dt[0], dt[1], 1, 'Graduated_Lines', colorScale(0));}
		else{
		    dt = draw_statistic_tree(response["UEdges-AMT"], response["UNodes-AMT"], svg, dt[0], dt[1], 1, 'Graduated_Lines', colorScale(0));}   
	    }
	    else if (DS=="SUV1"){
		delete_annotation(svg);
		dt = draw_statistic_tree(response["UEdges-AMT"], response["UNodes-AMT"], svg, dt[0], dt[1], 1, 'svarying_node', colorScale(0));
	    } else if (DS=="SUV2"){
		delete_annotation(svg);
		dt = draw_statistic_tree(response["UEdges-AMT"], response["UNodes-AMT"], svg, dt[0], dt[1], 1, 'sGraduated_Lines', colorScale(0));
	    } else if (DS=="SUV3"){
		delete_annotation(svg);
		dt = draw_statistic_tree(response["UEdges-AMT"], response["UNodes-AMT"], svg, dt[0], dt[1], 1, 'svarying_line', colorScale(0));
	    }
	    else{
		delete_annotation(svg);
		if (MTS=="MT1"){
		    dt = draw_tree(response["UEdges-AMT"], response["UNodes-AMT"], svg, dt[0], dt[1], 1, 'varying_line', colorScale(0));}
		else{
		    dt = draw_statistic_tree(response["UEdges-AMT"], response["UNodes-AMT"], svg, dt[0], dt[1], 1, 'varying_line', colorScale(0));
		}
	    }
	}

	 else{
	     if(DS =='LS'){
		 insert_annotation(svg, ['#8e0c01', '#006400', '#2b303c'], ['white', 'white', '#2b303c'], ['Labelled Leaf', 'Newly Labelled Leaf', "NOT Leaf"], 50);
		 dt = draw_tree(response["Edges-"+selected_id], response["Nodes-"+selected_id], svg, dt[0], dt[1], 1, 'large');
	     }
	     else if(DS=='UV') {
		 delete_annotation(svg);
		 dt = draw_tree(response["Edges-"+selected_id], response["Nodes-"+selected_id], svg, dt[0], dt[1], 1, 'varying_node', colorScale(response["IL-dist-"+selected_id]));
	     } else if(DS == "UV2") {
		 delete_annotation(svg);
		 dt = draw_tree(response["Edges-"+selected_id], response["Nodes-"+selected_id], svg, dt[0], dt[1], 1, 'Graduated_Lines', colorScale(response["IL-dist-"+selected_id]));
	     } else {
		 delete_annotation(svg);
		 dt = draw_tree(response["Edges-"+selected_id], response["Nodes-"+selected_id], svg, dt[0], dt[1], 1, 'varying_line', colorScale(response["IL-dist-"+selected_id]));
	     }
	 }
	return [dt[0], dt[1]];
    }

    function ANIMATION(response, svg, selected_id, dt, colorScale){
	var svg_source = d3.select("#trees-source");
	var svg_target = d3.select("#trees-target");
	var dt_source, dt_target;			    
	if(AM=='LA'){
	    if(AM_c=='LS'){
		dt = animation(response, svg4, dt[0], dt[1], selected_id, null, null, a_s, svg4_width/20);
		dt_source = draw_tree(response["UEdges-AMT"], response["UNodes-AMT"], svg_source, dt[0], dt[1], at_s, 'small', null, 10);
		dt_target = draw_tree(response["Edges-"+selected_id], response["Nodes-"+selected_id], svg_target, dt[0], dt[1], at_s, 'small', null, 10);
		insert_annotation_animation(svg_target, selected_id);
		insert_annotation(svg4, ['#8e0c01', '#006400', '#2b303c'], ['white', 'white', '#2b303c'], ['original labeled leaf', 'newly labeled leaf', "internal vertex"], 100);
	    }else{
		delete_annotation(svg4);
		dt = animation(response, svg4, dt[0], dt[1], selected_id, colorScale(0), colorScale(response["IL-dist-"+selected_id]), a_s, svg4_width/20);
		dt_source = draw_tree(response["UEdges-AMT"], response["UNodes-AMT"], svg_source, dt[0], dt[1], at_s, 'small', colorScale(0), 10);
		dt_target = draw_tree(response["Edges-"+selected_id], response["Nodes-"+selected_id], svg_target, dt[0], dt[1], at_s, 'small', colorScale(response["IL-dist-"+selected_id]), 10);
		insert_annotation_animation(svg_target, selected_id);
	    }
	}
	else{
	    if(AM_c=='LS'){
		dt = geodesic_animation(response, svg4, dt[0], dt[1], selected_id, null, a_s, svg4_width/20);
		dt_source = draw_tree(response["UEdges-AMT"], response["UNodes-AMT"], svg_source, dt[0], dt[1], at_s, 'small', null, 10);
		dt_target = draw_tree(response["Edges-"+selected_id], response["Nodes-"+selected_id], svg_target, dt[0], dt[1], at_s, 'small', null, 10);
		insert_annotation_animation(svg_target, selected_id);
		insert_annotation(svg4, ['#8e0c01', '#006400', '#2b303c'], ['white', 'white', '#2b303c'], ['original labeled leaf', 'newly labeled leaf', "internal vertex"], 100);
	    }else{
		delete_annotation(svg4);
		dt = geodesic_animation(response, svg4, dt[0], dt[1], selected_id, colorScale, a_s, svg4_width/20);
		dt_source = draw_tree(response["UEdges-AMT"], response["UNodes-AMT"], svg_source, dt[0], dt[1], at_s, 'small', colorScale(0), 10);
		dt_target = draw_tree(response["Edges-"+selected_id], response["Nodes-"+selected_id], svg_target, dt[0], dt[1], at_s, 'small', colorScale(response["IL-dist-"+selected_id]), 10);
		insert_annotation_animation(svg_target, selected_id);
	    }
	}
	
    }
    

    function animation(data, svg, circle, paths, id, edge_color1=null, edge_color2=null, scaler=1, modify_x){
	var dt = draw_tree(data["UEdges-AMT"], data["UNodes-AMT"], svg, circle, paths, scaler, 'large', edge_color1, modify_x);

	var edge_name = "Edges-"+id;
	var node_name = "Nodes-"+id;
	svg.selectAll('.legend').remove();

	data[node_name].sort(function(a, b){
	    return b.id-a.id;
	})
	paths = svg.selectAll("path")
	    .sort(function(a, b){
		return a.id-b.id;
	    })
	paths = svg.selectAll("path")
	    .data(data[edge_name]);

	paths.enter().append("path")
	    .style("fill", "none")
	    .style("stroke", function(d){
		if(edge_color1==null){return "#333";}
		else{return edge_color1;}
	    })
	    .style("stroke-width", "4px")
	    .style("cursor", "default");
	
	paths
	    .transition()
	    .delay(500)
	    .duration(1000)
	    .attr("d", function(d){
		return "M" + (d.source.x/scaler+modify_x) + "," + d.source.y/scaler + "L" + (d.target.x/scaler+modify_x) + "," + d.target.y/scaler;
	    })
	    .style("stroke", function(d){
		if(edge_color1==null){return "#333";}
		else{return edge_color2;}
	    });

	var l_dists = [];
	var colorScale = []
	if (edge_color1!=null){
	    for(var i=0; i<data[node_name].length; i++){
		l_dists.push(data[node_name][i]['local-dist'])
	    }
	    colorScale = d3.scale.linear()
		.domain(linspace(0, 1, scales_UV["Nodes"].length))
		.range(scales_UV["Nodes"]);
	}

	circle = svg.selectAll("g.nodes")
	    .sort(function(a, b){
		return b.id-a.id;
	    })
	
	
	circle = svg.selectAll("g.nodes")
	    .data(data[node_name]);

	var circleEnter = circle.enter()
	    .append("g")
	    .attr('class', 'nodes')
	
	circleEnter.append("circle")
	    .attr("r", String(30))
	    .attr("class", function(d){return d.cls;})
	    .attr("transform", function(d){
		return "translate(" + (d.x/scaler+modify_x) + "," + d.y/scaler + ")";});

	circleEnter.append("text")
	    .attr("text-anchor","middle")
	    .attr("dy", "6px")
	    .attr("font-size", "25px")
	    .attr("fill","#F6FBFF");
	
	circle.select('circle')
	    .attr("class", function(d){return d.cls;})
	    .transition()
	    .delay(500)
	    .duration(1000)
	    .attr("class", function(d){return d.cls;})
	    .attr("transform", function(d){
		return "translate(" + (d.x/scaler+modify_x) + "," + d.y/scaler + ")";})
	    .style("stroke", function(d){
		if(edge_color1!=null){
		    return edge_color2;
		} else{
		    return "#333";
		}
	    });

	if (edge_color1!=null){
	    circle.select('circle')
		.attr("class", function(d){return d.cls;})
		.transition()
		.delay(500)
		.duration(1000)
		.attr("transform", function(d){
		    return "translate(" + (d.x/scaler+modify_x) + "," + d.y/scaler + ")";})
		.style("fill", function(d, i){
		    return colorScale(l_dists[i]);
		})
		.style("stroke", function(d){
		    if(edge_color1!=null){
			return edge_color2;
		    } else{
			return "#333";
		    }
		});
	}
	
	circle.select('text')
	    .text(function(d){return d.title;})
	    .transition()
	    .delay(500)
	    .duration(1000)
	    .attr("x", function(d){return (d.x/scaler+modify_x);})
	    .attr("y", function(d){return d.y/scaler;});
	
	circle.each(function(d){
	    d3.select(this).moveToFront();
	});
	
	circle.exit().transition().duration(1000).remove();
	paths.exit().transition().duration(1000).remove();

	data["UNodes-AMT"].sort(function(a, b){
	    return b.id-a.id;
	})
	
	paths = svg.selectAll("path")
	    .data(data["UEdges-AMT"]);
	paths.enter().append("path")
	    .style("fill", "none")
	    .style("stroke", function(d){
		if(edge_color1==null){return "#333";}
		else{return edge_color2;}
	    })
	    .style("stroke-width", "4px")
	    .style("cursor", "default");
	
	paths
	    .transition()
	    .delay(2000)
	    .duration(1000)
	    .attr("d", function(d){
		return "M" + (d.source.x/scaler+modify_x) + "," + d.source.y/scaler + "L" + (d.target.x/scaler+modify_x) + "," + d.target.y/scaler;
	    })
	    .style("stroke", function(d){
		if(edge_color1==null){return "#333";}
		else{return edge_color1;}
	    });
	var l_dists = [];
	if (edge_color1!=null){
	    for(var i=0; i<data["UNodes-AMT"].length; i++){
		l_dists.push(data["UNodes-AMT"][i]['local-dist'])
	    }
	    colorScale = d3.scale.linear()
		.domain(linspace(0, 1, scales_UV["Nodes"].length))
		.range(scales_UV["Nodes"]);
	}
	circle = svg.selectAll("g.nodes")
	    .data(data["UNodes-AMT"]);

	circleEnter = circle.enter()
	    .append("g")
	    .attr('class', 'nodes')
	
	circleEnter.append("circle")
	    .attr("r", String(30))
	    .attr("class", function(d){return d.cls;})
	    .attr("transform", function(d){
		return "translate(" + (d.x/scaler+modify_x) + "," + d.y/scaler + ")";});

	circleEnter.append("text")
	    .attr("text-anchor","middle")
	    .attr("dy", "6px")
	    .attr("font-size", "25px")
	    .attr("fill","#F6FBFF");
	
	circle.select('circle')
	    .attr("class", function(d){return d.cls;})
	    .transition()
	    .delay(2000)
	    .duration(1000)
	    .attr("class", function(d){return d.cls;})
	    .attr("transform", function(d){
		return "translate(" + (d.x/scaler+modify_x) + "," + d.y/scaler + ")";})
	    .style("stroke", function(d){
		if(edge_color1!=null){
		    return edge_color1;
		} else{
		    return "#333";
		}
	    });

	if (edge_color1!=null){
	    circle.select('circle')
		.attr("class", function(d){return d.cls;})
		.transition()
		.delay(2000)
		.duration(1000)
		.attr("transform", function(d){
		    return "translate(" + (d.x/scaler+modify_x) + "," + d.y/scaler + ")";})
		.style("fill", function(d, i){
		    return colorScale(l_dists[i]);
		})
		.style("stroke", function(d){
		    if(edge_color1!=null){
			return edge_color1;
		    } else{
			return "#333";
		    }
		});
	}
	

	circle.select('text')
	    .text(function(d){return d.title;})
	    .transition()
	    .delay(2000)
	    .duration(1000)
	    .attr("x", function(d){return (d.x/scaler+modify_x);})
	    .attr("y", function(d){return d.y/scaler;});
	
	circle.each(function(d){
	    d3.select(this).moveToFront();
	});
	
	
	circle.exit().transition().duration(1000).remove();
	paths.exit().transition().duration(1000).remove();

	if(edge_color1!=null){
	    insert_legend(svg, [0, 1], 1, scales_UV["Nodes"]);
	}
	return [circle, paths];
    }
    

    function geodesic_animation(data, svg, circle, paths, id, colorScale_Edge=null, scaler=1, modify_x){
	var dt;
	if (colorScale_Edge!=null){
	    dt = draw_tree(data["UEdges-AMT"], data["UNodes-AMT"], svg, circle, paths, scaler, 'large', colorScale_Edge(0), modify_x);
	} else{
	    dt = draw_tree(data["UEdges-AMT"], data["UNodes-AMT"], svg, circle, paths, scaler, 'large', null, modify_x);
	}
	
	circle = dt[0];
	paths = dt[1];
	svg.selectAll('.legend').remove();

	var dur_time = 200
	var del_time = 100
	
	
	var edge_name = "Edges-"+id;
	var node_name = "Nodes-"+id;
	var IL_name = "IL-dist-"+id;
	var GA_param = data["GA_param"]

	var lamdas = [0]
	for (var i = 0; i<GA_param; i++){
	    lamdas.push(1/GA_param*(i+1));
	}
	var edge_color;
	var colorScale = [];
	if (colorScale_Edge!=null){
	    edge_color = colorScale_Edge(0);
	    colorScale = d3.scale.linear()
		.domain(linspace(0, 1, scales_UV["Nodes"].length))
		.range(scales_UV["Nodes"]);
	}
	
	
	for(var i = 0; i<GA_param+1; i++){
	    data[node_name+'-'+i].sort(function(a, b){
		return b.id-a.id;
	    });
	    
	    paths = svg.selectAll("path")
		.sort(function(a, b){
		    return a.id-b.id;
		})

	    
	    paths = svg.selectAll("path")
		.data(data[edge_name+'-'+i]);
	    
	    paths.enter().append("path")
		.style("fill", "none")
		.style("stroke", function(d){
		    if(colorScale_Edge==null){
			return "#333";
		    } else { return edge_color;}
		})
		.style("stroke-width", "4px")
		.style("cursor", "default");

	    if (colorScale_Edge!=null){
		edge_color = colorScale_Edge(data[IL_name+'-'+i]);
	    }
	    
	    paths
		.transition()
		.delay(500+(dur_time+del_time)*i)
		.duration(dur_time)
		.attr("d", function(d){
		    return "M" + (d.source.x/scaler+modify_x) + "," + d.source.y/scaler + "L" + (d.target.x/scaler+modify_x) + "," + d.target.y/scaler;
		})
		.style("stroke", function(d){
		    if(colorScale_Edge==null){
			return "#333";
		    } else { return edge_color;}
		});

	    var l_dists = [];
	    if (edge_color!=null){
		for(var j=0; j<data[node_name+'-'+i].length; j++){
		    l_dists.push(data[node_name+'-'+i][j]['local-dist'])
		}
	    }
	    circle = svg.selectAll("g.nodes")
		.sort(function(a, b){
		    return b.id-a.id;
		});

	    
	    circle = svg.selectAll("g.nodes")
		.data(data[node_name+'-'+i]);
	    
	    var circleEnter = circle.enter()
		.append("g")
		.attr('class', 'nodes')
	    
	    circleEnter.append("circle")
		.attr("r", String(30))
		.attr("class", function(d){return d.cls;})
		.attr("transform", function(d){
		    return "translate(" + (d.x/scaler+modify_x) + "," + d.y/scaler + ")";});

	    circleEnter.append("text")
		.attr("text-anchor","middle")
		.attr("dy", "6px")
		.attr("font-size", "25px")
		.attr("fill","#F6FBFF");

	    circle.select('circle')
		.attr("class", function(d){return d.cls;})
		.transition()
		.delay(500+(dur_time+del_time)*i)
		.duration(dur_time)
		.attr("class", function(d){return d.cls;})
		.attr("transform", function(d){
		    return "translate(" + (d.x/scaler+modify_x) + "," + d.y/scaler + ")";})
		.style("stroke", function(d){
		    if(edge_color!=null){
			return edge_color;
		    } else{
			return "#333";
		    }
		});

	    if (edge_color!=null){
		circle.select('circle')
		    .attr("class", function(d){return d.cls;})
		    .transition()
		    .delay(500+(dur_time+del_time)*i)
		    .duration(dur_time)
		    .attr("transform", function(d){
			return "translate(" + (d.x/scaler+modify_x) + "," + d.y/scaler + ")";})
		    .style("fill", function(d, i){
			return colorScale(l_dists[i]);
		    })
		    .style("stroke", function(d){
			if(edge_color!=null){
			    return edge_color;
			} else{
			    return "#333";
			}
		    });
	    };
	
	    circle.select('text')
		.text(function(d){return d.title;})
		.transition()
		.delay(500+(dur_time+del_time)*i)
		.duration(dur_time)
		.attr("x", function(d){return (d.x/scaler+modify_x);})
		.attr("y", function(d){return d.y/scaler;});
	    
	    circle.each(function(d){
		d3.select(this).moveToFront();		
	    });

	    circle.exit().transition().duration(1000).remove();
	    paths.exit().transition().duration(1000).remove();

	}
	var j = 0
	for(var i = GA_param-1; i>-1; i--){
	    var tt =500+(dur_time+del_time)*GA_param+dur_time;
	    
	    data[node_name+'-'+i].sort(function(a, b){
		return b.id-a.id;
	    })
	    
	    paths = svg.selectAll("path")
		.sort(function(a, b){
		    return a.id-b.id;
		});

	    circle = svg.selectAll("g.nodes")
		.sort(function(a, b){
		    return b.id-a.id;
		});
	    

	    paths = svg.selectAll("path")
		.data(data[edge_name+'-'+i]);
	    
	    paths.enter().append("path")
		.style("fill", "none")
		.style("stroke", function(d){
		    if(colorScale_Edge==null){
			return "#333";
		    } else { return edge_color;}
		})
		.style("stroke-width", "4px")
		.style("cursor", "default");

	    if (colorScale_Edge!=null){
		edge_color = colorScale_Edge(data[IL_name+'-'+i]);
	    }
	    
	    paths
		.transition()
		.delay(tt+500+(dur_time+del_time)*j)
		.duration(dur_time)
		.attr("d", function(d){
		    return "M" + (d.source.x/scaler+modify_x) + "," + d.source.y/scaler + "L" + (d.target.x/scaler+modify_x) + "," + d.target.y/scaler;
		})
	    	.style("stroke", function(d){
		    if(colorScale_Edge==null){
			return "#333";
		    } else { return edge_color;}
		});

	    var l_dists = [];
	    if (edge_color!=null){
		for(var k=0; k<data[node_name+'-'+i].length; k++){
		    l_dists.push(data[node_name+'-'+i][k]['local-dist'])
		}
	    }
	    
	    circle = svg.selectAll("g.nodes")
		.data(data[node_name+'-'+i]);
	    
	    var circleEnter = circle.enter()
		.append("g")
		.attr('class', 'nodes')
	    
	    circleEnter.append("circle")
		.attr("r", String(30))
		.attr("class", function(d){return d.cls;})
		.attr("transform", function(d){
		    return "translate(" + (d.x/scaler+modify_x) + "," + d.y/scaler + ")";});

	    circleEnter.append("text")
		.attr("text-anchor","middle")
		.attr("dy", "6px")
		.attr("font-size", "25px")
		.attr("fill","#F6FBFF");

	    circle.select('circle')
		.attr("class", function(d){return d.cls;})
		.transition()
		.delay(tt+500+(dur_time+del_time)*j)
		.duration(dur_time)
		.attr("class", function(d){return d.cls;})
		.attr("transform", function(d){
		    return "translate(" + (d.x/scaler+modify_x) + "," + d.y/scaler + ")";})
		.style("stroke", function(d){
		    if(edge_color!=null){
			return edge_color;
		    } else{
			return "#333";
		    }
		});

	    if (edge_color!=null){
		circle.select('circle')
		    .attr("class", function(d){return d.cls;})
		    .transition()
		    .delay(tt+500+(dur_time+del_time)*j)
		    .duration(dur_time)
		    .attr("transform", function(d){
			return "translate(" + (d.x/scaler+modify_x) + "," + d.y/scaler + ")";})
		    .style("fill", function(d, i){
			return colorScale(l_dists[i]);
		    })
		    .style("stroke", function(d){
			if(edge_color!=null){
			    return edge_color;
			} else{
			    return "#333";
			}
		    });
	    };

	    circle.select('text')
		.text(function(d){return d.title;})
		.transition()
		.delay(tt+500+(dur_time+del_time)*j)
		.duration(dur_time)
		.attr("x", function(d){return (d.x/scaler+modify_x);})
		.attr("y", function(d){return d.y/scaler;});
	    
	    circle.each(function(d){
		d3.select(this).moveToFront();
	    });

  
	    circle.exit().transition().duration(1000).remove();
	    paths.exit().transition().duration(1000).remove();
	    j = j+1;
	}
	if(edge_color!=null){
	    insert_legend(svg, [0, 1], 1, scales_UV["Nodes"]);
	}
	return [circle, paths];
    }

    

})(window.d3, window.saveAs, window.Blob);

