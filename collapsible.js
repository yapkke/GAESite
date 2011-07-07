function makeAllCollapsible(name){
  var llists = document.getElementsByName(name);
  for (litem in llists)
	 makeCollapsible(llists[litem]);
}

/* makeCollapsible - makes a list have collapsible sublists
 * 
 * listElement - the element representing the list to make collapsible
 */
function makeCollapsible(listElement){
 
  // removed list item bullets and the sapce they occupy
  listElement.style.listStyle='none';
//  listElement.style.marginLeft='0';
  listElement.style.paddingLeft='0';
 
  // loop over all child elements of the list
  var child=listElement.firstChild;
  while (child!=null){
 
    // only process li elements (and not text elements)
    if (child.nodeType==1){
 
      // build a list of child ol and ul elements and hide them
      var list=new Array();
      var grandchild=child.firstChild;
      while (grandchild!=null){
        if (grandchild.tagName=='OL' || grandchild.tagName=='UL'){
          grandchild.style.display='none';
          list.push(grandchild);
        }
        grandchild=grandchild.nextSibling;
      }
 
      // add toggle buttons
      var node=document.createElement('a');
      node.setAttribute('class','collapsibleClosed');
      node.innerHTML = '(+)&nbsp&nbsp';
      node.onclick=createToggleFunction(node,list);
      node.style.textDecoration = "none"
      child.insertBefore(node,child.firstChild);
    }
 
    child=child.nextSibling;
  }
 
}
 
/* createToggleFunction - returns a function that toggles the sublist display
 * 
 * toggleElement  - the element representing the toggle gadget
 * sublistElement - an array of elements representing the sublists that should
 *                  be opened or closed when the toggle gadget is clicked
 */
function createToggleFunction(toggleElement,sublistElements){
 
  return function(){
 
    // toggle status of toggle gadget
    if (toggleElement.getAttribute('class')=='collapsibleClosed'){
      toggleElement.setAttribute('class','collapsibleOpen');
      toggleElement.innerHTML = '(--)&nbsp&nbsp';
    }else{
      toggleElement.setAttribute('class','collapsibleClosed');
      toggleElement.innerHTML = '(+)&nbsp&nbsp';
    }
 
    // toggle display of sublists
    for (var i=0;i<sublistElements.length;i++){
      sublistElements[i].style.display=
          (sublistElements[i].style.display=='block')?'none':'block';
    }
 
  }
 
}
 
