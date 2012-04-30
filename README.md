# transmogrifier

	curl https://github.com/VPH-Share/transmogrifier/raw/master/bootstrap.lucid64.sh | sh
## What?

**Transmogrifier** is a [RESTful](http://en.wikipedia.org/wiki/Representational_state_transfer) *image manipulation webservice* wrapper around [GraphicsMagick](http://www.graphicsmagick.org/) which is the swiss army knife of image processing. There are many possible uses for this, but one major use is to resize images on-the-fly directly from HTML code, rather than processing the image when it is first uploaded or created. For example, if a user uploads a file to LOBCDER and it gets stored in `lob://image.jpg` or is stored externally, you could show a thumbnailed 50x50 px version like this:

	<img src="http://127.0.0.1:8080/convert?thumbnail=50x50&src=lob://image.jpg">

If you ever decided to change the size, you wouldn't have to re-encode anything, just change the HTML:

	<img src="http://127.0.0.1:8080/convert?thumbnail=75x75&src=http://www.example.com/image.jpg">

You can also perform transformations by making requests via curl or the programming language of your choice. Use its `identify` method to identify the image format and metadata attributes associated with the image.

As you can imagine you can pipline transfomations, and the API will sequence the transformation in the order you sepcify, as shown below:

	<img src="http://127.0.0.1:8080/convert?flip=V&thumbnail=75x75&src=http://www.example.com/image.jpg">

Without sounding too pretentious, I have used this simple project to consolidate the many RESTful best practices I have known about, to help developers write good and more importantly usable web services.

## Why?

> [Because] it's amazing what they can do with corrugated cardboards these days...Oh the horrors we visit upon ourselves in the name of science. ~ Hobbes

## How?

Transmogrifier uses a large amount of open-source tools, and wouldn't be possible without them.

#### Standards

* [HTML5](http://www.html5rocks.com/en/)
* [CSS3](http://www.css3.info/)

#### Front-End
* [HTML5 Boilerplate](http://html5boilerplate.com/)
* [Twitter Bootstrap](http://twitter.github.com/bootstrap/)
* [jQuery](http://jquery.com/)
* [Modernizr](http://modernizr.com/)

#### Back-End
* [Flask](http://flask.pocoo.org/)
* [Gunicorn](http://gunicorn.org/)
* [Gevent](http://www.gevent.org/)
* [Supervisord](http://supervisord.org/)
* [GraphicsMagick](http://www.graphicsmagick.org/)


## Status

This project was a quick prototype written in under a day for demostration purposes, so is in no way complete. There are definitely some improvements that need to be made. Suggestions and pull requests are welcome.

### Current Features

* Describe the attributes of the image
* Resize, Flip, Rotate, Thumbnail the format of the image
* ~~Access LOBCDER URIs. (Locally mounted WebDAV resources)~~

The latest API base URL that implements these features is `http://127.0.0.1:8080/v1`

### Future Features
* [Composite images together](http://www.graphicsmagick.org/composite.html)
* [Compare two images using statistics and/or visual differencing](http://www.graphicsmagick.org/compare.html)
* Support BATCH API calls
* Use [X-Sendfile / X-Accel-Redirect](http://wiki.nginx.org/XSendfile) Headers
* Support at least [HTTP Basic-Auth](http://en.wikipedia.org/wiki/Basic_access_authentication) or [HTTP Digest Auth](http://en.wikipedia.org/wiki/Digest_access_authentication)
* Got SOAP? It's OK, I don't like you either! :)
* Generate documentation from API specification
* Basic More Advanced error handling
* Lots and lots of refactoring
* ~~Basic~~ [spel-cheking](https://www.google.co.uk/search?q=spel-cheking) :) Note to self: Hire a copy editor or Mom.
* Minimise API documentation html, img, jss, css

## Performance
Transmogrifier is by no means performant. It is written in Python and shells out to
GraphicsMagick for its magic. It could be written in C as an Apache/Nginx module, but I don't have the time nor the inclination to do so.

Moreover it does not perform any form of caching, which IMHO is better left to CDN's like [Akamai](http://www.akamai.com/) or [CloudFront](https://aws.amazon.com/cloudfront/) or to caching proxies such as [Varnish](https://www.varnish-cache.org/) or [Squid](http://www.squid-cache.org/).
