{% extends "wrapper.tpl" %}
{% block body %}
    <div class="row">
        <div class="span12">
            <h1>Config</h1>
            <h2>
                <form class="form-inline" action="/config/" method="post">
                {% module xsrf_form_html() %}
                Save Path: <input type="text" name="savepath" 
                {% if "savepath" in config %}
                    value="{{ config["savepath"] }}"
                {% end %}
                >
                <button name="do" value="savepath" type="submit" class="btn">Save</button>
                </form>
            </h2>
            {% if len(cameras) > 0 %}
                <h2>Cameras</h2>
                {% for camera in cameras %}
                    <div class="well">
                        <form class="form-inline" action="/config/" method="post">
                            {% module xsrf_form_html() %}
                            <input type=hidden name="camera.name" value="{{ camera.name }}">
                            <strong>{{ camera.name }}</strong>: {{ camera.host }} <button name="do" value="delete" type="submit" class="btn">Delete</button>
                        {% if camera.errors > 2 %}
                        <div class="alert">Monitoring of this camera has been disabled because of errors, please check it.</div>
                        {% end %}
                        </form>
                    </div>
                {% end %}
            {% else %}
            <div>
                Thank you for installing Eyenado. Please use the form below to start adding your cameras.
            </div>
            {% end %}
            <form class="form-inline" action="/config/" method="post">
                {% module xsrf_form_html() %}
                <legend>Add a camera</legend>
                <input type="text" placeholder="Camera name" name="camera.name">
                <input type="text" placeholder="Camera host" name="camera.host">
                <input type="text" placeholder="Camera user (blank for none)" name="camera.user">
                <input type="password" placeholder="Camera password (blank for none)" name="camera.password">
                <button name="do" value="add" type="submit" class="btn">Add Camera</button>
            </form>
        </div>
    </div>
{% end %}
