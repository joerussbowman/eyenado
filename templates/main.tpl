{% extends "wrapper.tpl" %}
{% block body %}
    <h1>Eyenado</h1>
    {% for camera in cameras %}
        <h2>{{ camera.name }}</h2>
        <img class="cam" src="/getimage/{{ camera.name }}/?ts="><br />
        <a href="/viewpics/{{ camera.name }}/">View pictures</a>
    {% end %}
{% end %}
{% block javascript %}
jQuery(function($) {
    $(document).ready(function() {
        setInterval(function(){
            $('.cam').each(function() {
                var jqt = $(this);
                var src = jqt.attr('src');
                src = src.substr(0,src.indexOf('?'));
                src += '?_ts=' + new Date().getTime();
                jqt.attr('src',src);
            });
        }, 500);
    });
});
{% end %}
