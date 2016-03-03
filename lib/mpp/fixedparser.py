import feedparser
if 'drv_libxml2' in feedparser.PREFERRED_XML_PARSERS:
    feedparser.PREFERRED_XML_PARSERS.remove('drv_libxml2') 
