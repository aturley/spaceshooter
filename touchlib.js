// Copyright (C) 2009  Andrew Turley <aturley@acm.org>

// This program is free software; you can redistribute it and/or modify
// it under the terms of the GNU General Public License as published by
// the Free Software Foundation; either version 3 of the License, or
// (at your option) any later version.

// This program is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU General Public License for more details.

// You should have received a copy of the GNU General Public License
// along with this program; if not, write to the Free Software
// Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  US

function getXmlHttpRequestObject() {
  if (window.XMLHttpRequest) {
    return new XMLHttpRequest();
  } else if(window.ActiveXObject) {
    return new ActiveXObject("Microsoft.XMLHTTP");
  } else {
    document.getElementById('p_status').innerHTML = 
      'Status: Cound not create XmlHttpRequest Object.' +
      'Consider upgrading your browser.';
  }
}

function ButtonDown(elementId) {
  this.elementId = elementId;
  this.toJson = function() {
    return "{\"elementId\":\"" + elementId + "\",\"action\":\"ButtonDown\"}";
  };
}

function ButtonUp(elementId) {
  this.elementId = elementId;
  this.toJson = function() {
    return "{\"elementId\":\"" + elementId + "\",\"action\":\"ButtonUp\"}";
  };
}

function MultitouchTouch(elementId, x, y) {
  this.elementId = elementId;
  this.x = x;
  this.y = y;
  this.toJson = function() {
    json = "";
    json += "{\"elementId\":\"" + elementId + "\",\"action\":\"MultitouchTouch\",\"coord:\"";
    json += "[" + x + "," + y + "]";
    json += "}"; 
    return json;
  };
}

function MultitouchTouchList(elementId, offsetX, offsetY, evt) {
  this.elementId = elementId;
  this.touches = new Array(evt.touches.length);

  if (this.touches.length > 0) {
    for (i = 0; i < evt.touches.length; i++) {
      this.touches[i] = [evt.touches[i].pageX - offsetX, evt.touches[i].pageY - offsetY, evt.touches[i].identifier];
    }
  }
  
  this.toJson = function() {
    json = "";
    if (this.touches.length > 0) {
      json += "{\"elementId\":\"" + elementId + "\",\"action\":\"MultitouchTouchList\",\"coords\":[";
      for (j = 0; j < this.touches.length - 1; j++) {
	json += "[" + this.touches[j][0] + "," + this.touches[j][1] + "," + this.touches[j][2] + "],";
      }
      json += "[" + this.touches[this.touches.length - 1][0] + "," + this.touches[this.touches.length - 1][1] + "," + this.touches[this.touches.length - 1][2] + "]";
      json += "]}"; 
    }
    return json;
  };
}

function MultitouchTouchListEnd(elementId, offsetX, offsetY, evt) {
  this.elementId = elementId;
  this.touches = new Array(evt.changedTouches.length);

  if (this.touches.length > 0) {
    for (i = 0; i < evt.changedTouches.length; i++) {
      this.touches[i] = [evt.changedTouches[i].pageX - offsetX, evt.changedTouches[i].pageY - offsetY, evt.changedTouches[i].identifier];
    }
  }
  
  this.toJson = function() {
    json = "";
    if (this.touches.length > 0) {
      json += "{\"elementId\":\"" + elementId + "\",\"action\":\"MultitouchTouchListEnd\",\"coords\":[";
      for (var j = 0; j < this.touches.length - 1; j++) {
	json += "[" + this.touches[j][0] + "," + this.touches[j][1] + "," + this.touches[j][2] + "],";
      }
      json += "[" + this.touches[this.touches.length - 1][0] + "," + this.touches[this.touches.length - 1][1] + "," + this.touches[this.touches.length - 1][2] + "]";
      json += "]}"; 
    }
    return json;
  };
}

function MultitouchTouchNone(elementId) {
  this.elementId = elementId;
  this.toJson = function() {
    return "{\"elementId\":\"" + elementId + "\",\"action\":\"MultitouchTouchNone\"}";
  };
}

function Reset(elementId) {
  this.elementId = elementId;
  this.toJson = function() {
    return "{\"elementId\":\"" + elementId + "\",\"action\":\"Reset\"}";
  };
}

function ControlElement() {
}

function Button(element, elementId) {
  this.eventList = new Array();

  this.element = element;
  this.elementId = elementId;

  var thisx = this;

  this.element.addEventListener("touchstart", function(evt) {
      evt.preventDefault();
      if (evt.touches.length == 1) {
	// thisx.eventList.push(new ButtonDown(elementId));
	thisx.addEventToList(new ButtonDown(elementId));
      }
    }, false);
  this.element.addEventListener("touchend", function(evt) {
      evt.preventDefault();
      if (evt.touches.length == 0) {
	// thisx.eventList.push(new ButtonUp(elementId));
	thisx.addEventToList(new ButtonDown(elementId));
      }
    }, false);
}

Button.prototype = new ControlElement;

function Multitouch(element, elementId) {
  this.eventList = new Array();

  this.element = element;
  this.elementId = elementId;

  var thisx = this;
  this.element.addEventListener("touchstart", function(evt) {
      evt.preventDefault();
      if (evt.touches.length > 0) {
	// thisx.eventList.push(new MultitouchTouchList(elementId, element.offsetTop, element.offsetLeft, evt));
	thisx.addEventToList(new MultitouchTouchList(elementId, element.offsetTop, element.offsetLeft, evt));
      }
    }, false);

  this.element.addEventListener("touchmove", function(evt) {
      evt.preventDefault();
      if (evt.touches.length > 0) {
	// thisx.eventList.push(new MultitouchTouchList(elementId, element.offsetTop, element.offsetLeft, evt));
	thisx.addEventToList(new MultitouchTouchList(elementId, element.offsetTop, element.offsetLeft, evt));
      }
    }, false);
  this.element.addEventListener("touchend", function(evt) {
      evt.preventDefault();
      // thisx.eventList.push(new MultitouchTouchListEnd(elementId, element.offsetTop, element.offsetLeft, evt));
      thisx.addEventToList(new MultitouchTouchListEnd(elementId, element.offsetTop, element.offsetLeft, evt));
      if (evt.touches.length > 0) {
	thisx.addEventToList(new MultitouchTouchList(elementId, element.offsetTop, element.offsetLeft, evt));
      } else {
	thisx.addEventToList(new MultitouchTouchNone(elementId));
      }
    }, false);
  this.element.addEventListener("gesturestart", function(evt) {
      evt.preventDefault();
    }, false);
  this.element.addEventListener("gesturechange", function(evt) {
      evt.preventDefault();
    }, false);
  this.element.addEventListener("gestureend", function(evt) {
      evt.preventDefault();
    }, false);
}

Multitouch.prototype = new ControlElement;

function MultitouchStartEnd(element, elementId) {
  this.eventList = new Array();

  this.element = element;
  this.elementId = elementId;

  var thisx = this;
  this.element.addEventListener("touchstart", function(evt) {
      evt.preventDefault();
      if (evt.touches.length > 0) {
	// thisx.eventList.push(new MultitouchTouchList(elementId, element.offsetTop, element.offsetLeft, evt));
	thisx.addEventToList(new MultitouchTouchList(elementId, element.offsetTop, element.offsetLeft, evt));
      }
    }, false);

  this.element.addEventListener("touchmove", function(evt) {
      evt.preventDefault();
    }, false);
  this.element.addEventListener("touchend", function(evt) {
      evt.preventDefault();
      // thisx.eventList.push(new MultitouchTouchListEnd(elementId, element.offsetTop, element.offsetLeft, evt));
      thisx.addEventToList(new MultitouchTouchListEnd(elementId, element.offsetTop, element.offsetLeft, evt));
      if (evt.touches.length > 0) {
	// thisx.eventList.push(new MultitouchTouchList(elementId, element.offsetTop, element.offsetLeft, evt));
	thisx.addEventToList(new MultitouchTouchList(elementId, element.offsetTop, element.offsetLeft, evt));
      }
    }, false);
  this.element.addEventListener("touchcancel", function(evt) {
      evt.preventDefault();
    }, false);
  this.element.addEventListener("gesturestart", function(evt) {
      evt.preventDefault();
    }, false);
  this.element.addEventListener("gesturechange", function(evt) {
      evt.preventDefault();
    }, false);
  this.element.addEventListener("gestureend", function(evt) {
      evt.preventDefault();
    }, false);
}

MultitouchStartEnd.prototype = new ControlElement;

function JsonEventSender(xmlHttpRequest) {
  var thisx = this;

  this.msgList = new Array();
  this.outgoingMsgList = new Array();

  this.xmlHttpRequest = xmlHttpRequest;
  this.canSendEvents = true;

  this.backoff = 1;
  this.backoffCount = this.backoff;

  this.addControl = function (control) {
    control.addEventToList = function (evt) {
      thisx.msgList.push(evt);
    }
  };

  this.collectJson = function() {
    this.msgList.reverse();
    while (this.msgList.length > 0) {
      this.outgoingMsgList.push(this.msgList.pop());
    }
    
    var json = "";
    var jsonCore = "";
    var x = "";
    if (this.outgoingMsgList.length > 0) {
      for (var j = 0; j < this.outgoingMsgList.length - 1; j++) {
	jsonCore += this.outgoingMsgList[j].toJson() + ",";
      }
      jsonCore += this.outgoingMsgList[this.outgoingMsgList.length - 1].toJson();
    }
    if (jsonCore.length > 0) {
      json += "[";
      json += jsonCore;
      json += "]";
    }
    return json;
  };

  this.sendEvents = function(path) {
    if (!this.canSendEvents) {
      return;
    }

    this.backoffCount--;
    if (this.backoffCount > 0) {
      return;
    }

    var json = this.collectJson();

    if (json && json.length) {
      this.canSendEvents = false;
      with (xmlHttpRequest) {
	open("POST", path, true);
	onreadystatechange = function () {
	  if (thisx.xmlHttpRequest.readyState == 4) {
	    thisx.canSendEvents = true;
	    if (thisx.timeoutId) {
	      clearTimeout(thisx.timeoutId);
	      thisx.backoff = 1;
	      thisx.backoffCount = thisx.backoff;
	    }
	    while (thisx.outgoingMsgList.length > 0) {
	      thisx.outgoingMsgList.pop();
	    }
	  }
	};
	setRequestHeader("Content-Type", "text/plain;");
	send(json);
	this.timeoutId = setTimeout( function() {
	    thisx.xmlHttpRequest.abort();
	    thisx.canSendEvents = true;
	    thisx.backoff *= 2;
	    thisx.backoffCount = thisx.backoff;
	  }, 2000);
      }
    }
  }
}
