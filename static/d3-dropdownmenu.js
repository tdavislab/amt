/*-------------------------------------------------------------------*/
/* When the script is imported it extends the d3 library             */
/* to include d3.element.dropdownmenu                                */
/*-------------------------------------------------------------------*/

(function() {

d3.element = {}; // initialize the namespace
var root; // make a closure around root

/*-------------------------------------------------------------------*/
/* Helper methods                                                    */
/* Local to this self-calling anonymous function                     */
/* Don't pollute global namespace                                    */
/*-------------------------------------------------------------------*/
function styleUL(ul) {
  ul
		.style('position', 'absolute')
		.style('list-style', 'none')
		.style('padding', '0')
		.style('left', '100%')
		.style('top', '0%')
		.style('display', 'none')
}
function styleLI(li) {
	li
		.style('position', 'relative')
		.style('white-space', 'nowrap')
}
function setHandlersForLI(li) {
	/* namespaced so d3 won't remove them later */
	li.on('mouseover.d3-dropdownmenu', function() {
		d3.select(this).select('ul')
			.style('display', 'block');
	})
	li.on('mouseout.d3-dropdownmenu', function() {
		d3.select(this).select('ul')
			.style('display', 'none');
	})
}
/*-------------------------------------------------------------------*/
function toLink(selection) {
	/* tree traversal methods */
	selection.root = function() {
		return root;
	}

	selection.nodes = function() {
		return this.selectAll('li').each(function() {
			toNode(d3.select(this))
		})
	}

	selection.links = function() {
		return this.selectAll('ul').each(function() {
			toLink(d3.select(this))
		})
	}

	selection.childNodes = function() {
		return d3.selectAll(this.childNodes)
					.each(function() {
						toNode(d3.select(this))
					});
	}
	selection.firstChildNode = function() {
		return toNode(d3.select(this.node().firstChild));
	}
	selection.lastChildNode = function() {
		return toNode(d3.select(this.node().lastChild));
	}

	selection.parentNode = function() {
		return toNode(d3.select(this.node().parentNode));
	}
	/* end of tree traversal methods */
	/*---------------------------------------------------------------*/
	selection.horizontal = function() {
		d3.selectAll(this.node().childNodes)
			.style('float', 'left')
			.select('ul') // have to shift child list over
			.style('left', '0%')
			.style('top', '100%')

		return toLink(d3.select(this))
	};
	return selection;
}
function toNode(selection) {
	selection.add = function(data) {
		var ul = this.select('ul');
		if (ul.empty()) {
			ul = this
					.append('ul')
					.call(styleUL);
		}

		// parses tree recursively
		(function parseTree(selection, tree) {

			for (var attrname in tree) {
				selection.append('li').datum(attrname)
					.html(function(d) { return d; })
					.call(styleLI)
					.call(setHandlersForLI)
					// so as not to waste space on null terminators
					.call(function(selection) {
						if (tree[attrname]) { 
							selection.append('ul')
								.call(styleUL)
								.call(parseTree, tree[attrname]);
						}
					});
			}

		})(ul, data);

		return this; // for method chaining
	};

	/* tree traversal methods */
	selection.root = function() {
		return root;
	};

	selection.nodes = function() {
		return this.selectAll('li').each(function() {
			toNode(d3.select(this))
		});
	};

	selection.links = function() {
		return this.selectAll('ul').each(function() {
			toLink(d3.select(this))
		});
	};

	selection.childNodes = function() {
		var ul = this.select('ul').node();
		if (ul) {
			return d3.selectAll(ul.childNodes)
				.each(function() {
					toNode(d3.select(this));
				});
		} else {
			return null;
		}	
	};
	selection.firstChildNode = function() {
		var ul = this.select('ul').node();
		if (ul) {
			return toNode(d3.select(ul.firstChild));
		} else {
			return null;
		}
	};
	selection.lastChildNode = function() {
		var ul = this.select('ul').node();
		if (ul) {
			return toNode(d3.select(ul.lastChild));
		} else {
			return null;
		}
	};

	selection.childLink = function() {
		var ul = this.select('ul');
		if (ul) {
			return toLink(ul);
		} else {
			return null;
		}
	};

	selection.parentLink = function() {
		return toLink(d3.select(this.node().parentNode));
	};
	selection.parentNode = function() {
		if (this === root) {
			return null;
		} else {
			return toNode(d3.select(this.node().parentNode.parentNode));
		}
	}

	selection.nextSiblingNode = function() {
		return toNode(d3.select(this.node().nextSibling))
	};
	selection.previousSiblingNode = function() {
		return toNode(d3.select(this.node().previousSibling));
	};
	selection.prevSiblingNode = selection.previousSiblingNode;

	return selection;
}
/*-------------------------------------------------------------------*/

d3.element.dropdownmenu = function(container) { // returns a menu
	root = toNode(d3.select(container));
	root.show = function() {
		this.select('ul')
			.style('display', 'block') // make it visible
			.style('left', 'auto').style('top', 'auto')

		return this;
	}
	return root;
};

})();
