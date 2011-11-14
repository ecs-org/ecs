Custom Event
============

Allows to create custom events based on other custom events. Requires MooTools Core 1.3.

![Screenshot](http://cpojer.net/Logo/custom-event.png)

This Plugin is part of MooTools [PowerTools!](http://cpojer.net/PowerTools).

* [Build PowerTools!](http://cpojer.net/PowerTools)
* [Fork PowerTools!](https://github.com/cpojer/PowerTools)

Build
-----

Build via [Packager](http://github.com/kamicane/packager), requires [MooTools Core](http://github.com/mootools/mootools-core) to be registered to Packager already

	packager register /path/to/custom-event
	packager build Custom-Event/* > custom-event.js

To build this plugin without external dependencies use

	packager build Custom-Event/* +use-only Custom-Event > custom-event.js

Demo
----

See Demos/index.html

How To Use
----------

This plugin provies a method Element.defineCustomEvent

	// Fires when the user presses control
	Element.defineCustomEvent('control', {

		base: 'keydown',

		condition: function(event){
			return !!event.control;
		}

	});

Usage

	document.addEvent('control', function(event){
		// doSomething
	});

Subclassing

	// Fires when the user presses both control and alt
	Element.defineCustomEvent('control+alt', {

		base: 'control',

		condition: function(event){
			return !!event.alt;
		}

	});

	document.addEvent('control+alt', function(event){
		// doSomething else
	});

In addition there are also new "onSetup" and "onTeardown" events that get fired when the first listener gets added and when the last one got removed

	// Example from MooTools Mobile ( http://github.com/cpojer/mootools-mobile )
	var preventDefault = function(event){
		event.preventDefault();
	};

	Element.defineCustomEvent('touch', {

		base: 'touchend',

		condition: function(event){
			// code
		},

		onSetup: function(){
			this.addEvent('touchstart', preventDefault);
		},

		onTeardown: function(){
			this.removeEvent('touchstart', preventDefault);
		}

	});

There is also a new "hasEvent" method on Element to check whether an element has listeners associated to a specified event

	if (myElement.hasEvent('click')) // this element has click events associated with it

Enable / Disable Custom Events
------------------------------

To disable or enable certain custom events global you can use

	Element.disableCustomEvents();

To enable them again you can use

	Element.enableCustomEvents();

There are onEnable and onDisable methods on custom events to manually handle a call do disable/enable:

	var isEnabled = true;
	Element.defineCustomEvent('myCustomEvent', {

		base: 'touchstart'

		condition: function(){
			return isEnabled;
		},

		onEnable: function(){
			isEnabled = true;
		}

		onDisable: function(){
			isEnabled = false;
		}

	});
