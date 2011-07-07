def get_google_analytics(code):
    """Get code for Google analytics
    """
    return '''
    <script type="text/javascript">
    var _gaq = _gaq || [];
    _gaq.push([\'_setAccount\', \'%s\']);
    _gaq.push([\'_trackPageview\']);
    (function() {
    var ga = document.createElement(\'script\'); ga.type = \'text/javascript\'; ga.async = true;
    ga.src = (\'https:\' == document.location.protocol ? \'https://ssl\' : \'http://www\') + \'.google-analytics.com/ga.js\';
    var s = document.getElementsByTagName(\'script\')[0]; s.parentNode.insertBefore(ga, s);
    })();
    </script>
    ''' % code

def get_css(cssfile):
    return '''
    <link type="text/css" rel="stylesheet" href="%s" />
    ''' % cssfile

def get_js(jsfile):
    return '''
    <script language="javascript" src="%s"></script>
    ''' % jsfile
