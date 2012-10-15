{% extends "wrapper.tpl" %}
{% block body %}
    <div class="row">
        <div class="span12">
            <h1>Config</h1>
            {% if len(cameras) > 0 %}
                <h2>Cameras</h2>
                {% for camera in cameras %}
                    <div class="well">
                        <form class="form-inline" action="/config/" method="post">
                            <input type=hidden name="camera.name" value="{{ camera.name }}">
                            <strong>{{ camera.name }}</strong>: {{ camera.host }} <button name="do" value="delete" type="submit" class="btn">Delete</button>
                        </form>
                    </div>
                {% end %}
            {% end %}
            <form class="form-inline" action="/config/" method="post">
                <legend>Add a camera</legend>
                <input type="text" placeholder="Camera name" name="camera.name">
                <input type="text" placeholder="Camera host" name="camera.host">
                <button name="do" value="add" type="submit" class="btn">Add Camera</button>
            </form>
        </div>
    </div>
{% end %}
