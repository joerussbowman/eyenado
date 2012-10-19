{% extends "wrapper.tpl" %}
{% block body %}
    <h1>Hello World</h1>
    {% for camera in cameras %}
        <img class="cam" src="http://{{camera.host}}/snapshot.cgi?user={{camera.user}}&password={{camera.password}}">
    {% end %}
{% end %}
{% block javascript %}
jQuery(function($) {
    $(document).ready(function() {
        setInterval(function(){
            $('.cam').attr('src', $(this).attr('src')+'&'+Math.random());
        }, 500);
    });
});
{% end %}
