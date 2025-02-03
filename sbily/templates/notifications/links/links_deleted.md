This is an automatic notification to inform you that your {% if need_upgrade %}links have been deleted for exceeding your account limits.{% else %}expired links have been automatically removed.{% endif %}
{% if need_upgrade %}
Please upgrade your account to a higher level or purchase more links!
{% endif %}
There are a total of {{ links_count }} links removed, here they are:

{% for link in links %}
{{ forloop.counter }}. {{ link.shortened_link }} (<{{ link.original_link }}>)</li>
{% endfor %}
