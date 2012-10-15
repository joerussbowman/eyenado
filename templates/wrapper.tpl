<!DOCTYPE html>
<html>
<head>
    <title>Eyenado - Survelliance Cam Software</title>
    <link href="{{ static_url("css/bootstrap.min.css") }}" rel="stylesheet">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style type="text/css">
      body {
        padding-top: 60px;
        padding-bottom: 40px;
      }
        @media (max-width: 979px) {
          body {
            padding-top: 0px;
          }
        }
      .sidebar-nav {
        padding: 9px 0;
      }
    </style>
</head>
<body>
    <div class="navbar navbar-inverse navbar-fixed-top">
      <div class="navbar-inner">
        <div class="container-fluid">
          <a class="btn btn-navbar" data-toggle="collapse" data-target=".nav-collapse">
            <span class="icon-bar"></span>
            <span class="icon-bar"></span>
            <span class="icon-bar"></span>
          </a>
          <a class="brand" href="#">Eyenado</a>
          <div class="nav-collapse collapse">
            <ul class="nav">
              <li class="active"><a href="#">Home</a></li>
              <li><a href="#about">Cameras</a></li>
              <li><a href="#contact">Configuration</a></li>
            </ul>
          </div><!--/.nav-collapse -->
        </div>
      </div>
    </div>
    <div class="container">
{% block body %}
{% end %}
    </div>
<script src="{{ static_url("js/jquery-1.8.2.min.js") }}"></script>
</body>
</html>
