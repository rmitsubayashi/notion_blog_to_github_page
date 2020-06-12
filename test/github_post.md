---
layout: post
title: "this is the title"
date: 2019-10-25 11:00:00 +0900
categories: jekyll update
id: "unique id"
---
{% if post %}
{% assign categories = post.categories %}
{% else %}
{% assign categories = page.categories %}
{% endif %}
{% for category in categories %}
<a href="{{site.baseurl}}/categories/#{{category|slugize}}" style="float: right; margin-left: 4px;">{{category}}</a>
{% endfor %}
<br>
blah